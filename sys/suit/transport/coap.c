/*
 * Copyright (C) 2019 Freie Universität Berlin
 *               2019 Inria
 *               2019 Kaspar Schleiser <kaspar@schleiser.de>
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     sys_suit
 * @{
 *
 * @file
 * @brief       SUIT coap
 *
 * @author      Koen Zandberg <koen@bergzand.net>
 * @author      Kaspar Schleiser <kaspar@schleiser.de>
 * @author      Francisco Molina <francois-xavier.molina@inria.fr>
 * @author      Alexandre Abadie <alexandre.abadie@inria.fr>
 * @}
 */

#include <assert.h>
#include <inttypes.h>
#include <string.h>

#include "msg.h"
#include "log.h"
#include "net/nanocoap.h"
#include "net/nanocoap_sock.h"
#include "thread.h"
#include "periph/pm.h"
#include "xtimer.h"

#include "suit/transport/coap.h"
#include "net/sock/util.h"

#ifdef MODULE_RIOTBOOT_SLOT
#include "riotboot/slot.h"
#endif

#ifdef MODULE_SUIT
#include "suit.h"
#include "suit/handlers.h"
#include "suit/storage.h"
#endif

#if defined(MODULE_PROGRESS_BAR)
#include "progress_bar.h"
#endif

#define ENABLE_DEBUG 0
#include "debug.h"

#ifndef SUIT_COAP_STACKSIZE
/* allocate stack needed to do manifest validation */
#define SUIT_COAP_STACKSIZE (3 * THREAD_STACKSIZE_LARGE)
#endif

#ifndef SUIT_COAP_PRIO
#define SUIT_COAP_PRIO THREAD_PRIORITY_MAIN - 1
#endif

#ifndef SUIT_URL_MAX
#define SUIT_URL_MAX            128
#endif

#ifndef SUIT_MANIFEST_BUFSIZE
#define SUIT_MANIFEST_BUFSIZE   640
#endif

#define SUIT_MSG_TRIGGER        0x12345

static char _stack[SUIT_COAP_STACKSIZE];
static char _url[SUIT_URL_MAX];
static uint8_t _manifest_buf[SUIT_MANIFEST_BUFSIZE];


/* for patch updates */
#include "suit/bspatch.h"
#include "heatshrink_decoder.h"

#include "riotboot/slot.h"
#include "periph/flashpage.h"

bool detect_patch = 0;

# define LEN_DIFF_PATCH FLASHPAGE_SIZE
uint16_t ring_size = 0;
uint16_t ptr_ring = 0;
uint8_t* ring_buffer;

uint16_t ptr_inner_ring = 0;
uint8_t* inner_ring_buffer;

unsigned new_data_page = 0;
unsigned old_data_page = 0;
unsigned old_data_start_page = 0;
size_t storage_offset = 0;

suit_storage_t* storage_ring_buffer = NULL;
suit_manifest_t* manifest_ring_buffer = NULL;

/* heatshrink decoder */
# define DECODER_POLL 128
static heatshrink_decoder _decoder;

/* bsdiff values */
size_t newsize,ctrllen,datalen;
size_t ctrlblock;
size_t diffblock, extrablock;
size_t oldpos,newpos,patch_pos;
size_t ctrl[3];
size_t i_loop;
uint8_t i_loop_done = 1;
bool __init_own_bsdiff = 0;

#define SIZE_BUFFER_HEADER 4
uint8_t size_buffer_header_counter = 0;

uint8_t* buffer_header;

size_t offset_patch_data;
size_t offset_old_data;
uint8_t old_data[FLASHPAGE_SIZE];

typedef struct {
    size_t offset_pointer;
    size_t size_pointer;
}extra_pointers_t;

#define LEN_EXTRA_POINTER 64
extra_pointers_t* extra_pointers;
uint8_t entry_extrpointer = 0;
bool calc_extra_blocks = 0;
bool extra_blocks_done = 0;
bool load_extra_data = 0;

uint8_t loop = 0;


#ifdef MODULE_SUIT
static inline void _print_download_progress(suit_manifest_t *manifest,
                                            size_t offset, size_t len,
                                            size_t image_size)
{
    (void)manifest;
    (void)offset;
    (void)len;
    DEBUG("_suit_flashwrite(): writing %u bytes at pos %u\n", len, offset);
#if defined(MODULE_PROGRESS_BAR)
    if (image_size != 0) {
        char _suffix[7] = { 0 };
        uint8_t _progress = 100 * (offset + len) / image_size;
        sprintf(_suffix, " %3d%%", _progress);
        progress_bar_print("Fetching firmware ", _suffix, _progress);
        if (_progress == 100) {
            puts("");
        }
    }
#else
    (void) image_size;
#endif
}
#endif

static kernel_pid_t _suit_coap_pid;

ssize_t coap_subtree_handler(coap_pkt_t *pkt, uint8_t *buf, size_t len,
                             void *context)
{
    coap_resource_subtree_t *subtree = context;
    return coap_tree_handler(pkt, buf, len, subtree->resources,
                             subtree->resources_numof);
}

static inline uint32_t _now(void)
{
    return xtimer_now_usec();
}

static inline uint32_t deadline_from_interval(int32_t interval)
{
    assert(interval >= 0);
    return _now() + (uint32_t)interval;
}

static inline uint32_t deadline_left(uint32_t deadline)
{
    int32_t left = (int32_t)(deadline - _now());

    if (left < 0) {
        left = 0;
    }
    return left;
}

static ssize_t _nanocoap_request(sock_udp_t *sock, coap_pkt_t *pkt, size_t len)
{
    ssize_t res = -EAGAIN;
    size_t pdu_len = (pkt->payload - (uint8_t *)pkt->hdr) + pkt->payload_len;
    uint8_t *buf = (uint8_t *)pkt->hdr;
    uint32_t id = coap_get_id(pkt);

    /* TODO: timeout random between between ACK_TIMEOUT and (ACK_TIMEOUT *
     * ACK_RANDOM_FACTOR) */
    uint32_t timeout = CONFIG_COAP_ACK_TIMEOUT * US_PER_SEC;
    uint32_t deadline = deadline_from_interval(timeout);

    /* add 1 for initial transmit */
    unsigned tries_left = CONFIG_COAP_MAX_RETRANSMIT + 1;

    while (tries_left) {
        if (res == -EAGAIN) {
            res = sock_udp_send(sock, buf, pdu_len, NULL);
            if (res <= 0) {
                DEBUG("nanocoap: error sending coap request, %d\n", (int)res);
                break;
            }
        }

        res = sock_udp_recv(sock, buf, len, deadline_left(deadline), NULL);
        if (res <= 0) {
            if (res == -ETIMEDOUT) {
                DEBUG("nanocoap: timeout\n");

                tries_left--;
                if (!tries_left) {
                    DEBUG("nanocoap: maximum retries reached\n");
                    break;
                }
                else {
                    timeout *= 2;
                    deadline = deadline_from_interval(timeout);
                    res = -EAGAIN;
                    continue;
                }
            }
            DEBUG("nanocoap: error receiving coap response, %d\n", (int)res);
            break;
        }
        else {
            if (coap_parse(pkt, (uint8_t *)buf, res) < 0) {
                DEBUG("nanocoap: error parsing packet\n");
                res = -EBADMSG;
            }
            else if (coap_get_id(pkt) != id) {
                res = -EBADMSG;
                continue;
            }

            break;
        }
    }

    return res;
}

static int _fetch_block(coap_pkt_t *pkt, uint8_t *buf, sock_udp_t *sock,
                        const char *path, coap_blksize_t blksize, size_t num)
{
    uint8_t *pktpos = buf;
    uint16_t lastonum = 0;

    pkt->hdr = (coap_hdr_t *)buf;

    pktpos += coap_build_hdr(pkt->hdr, COAP_TYPE_CON, NULL, 0, COAP_METHOD_GET,
                             num);
    pktpos += coap_opt_put_uri_pathquery(pktpos, &lastonum, path);
    pktpos +=
        coap_opt_put_uint(pktpos, lastonum, COAP_OPT_BLOCK2,
                          (num << 4) | blksize);

    pkt->payload = pktpos;
    pkt->payload_len = 0;

    int res = _nanocoap_request(sock, pkt, 64 + (0x1 << (blksize + 4)));
    if (res < 0) {
        return res;
    }

    res = coap_get_code(pkt);
    DEBUG("code=%i\n", res);
    if (res != 205) {
        return -res;
    }

    return 0;
}

void __print_bin_data(uint8_t* data, size_t start, size_t end){
    for (size_t ptr = start; ptr < end; ptr = ptr+16) {
        printf("%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x\n",
            data[ptr],data[ptr+1],data[ptr+2],data[ptr+3],data[ptr+4],data[ptr+5],data[ptr+6],data[ptr+7],
            data[ptr+8],data[ptr+9],data[ptr+10],data[ptr+11],data[ptr+12],data[ptr+13],data[ptr+14],data[ptr+15]);
    }
}

int write_inner_ring_buffer(uint8_t* data, uint8_t length) {
    if (storage_ring_buffer == NULL || manifest_ring_buffer == 0) {
        printf("Ring buffer storage and manifest not initialized\n");
        return -2;
    }
    for (int i = 0; i < length; i++) {
        inner_ring_buffer[ptr_inner_ring] = data[i];
        ptr_inner_ring++;
        if (ptr_inner_ring == ring_size) {
            if (suit_storage_write(storage_ring_buffer, manifest_ring_buffer, inner_ring_buffer, storage_offset, ring_size) != SUIT_OK){
                printf("Write Buffer to Storage failed!\n");
                return -1;
            }
            /* reset buffer and increment storage */
            storage_offset += ring_size;
            ptr_inner_ring = 0;
        }
    }
    return 0;
}

int init_own_bsdiff(void){
    printf("INIT own bsdiff\n");
    /* allocate extra pointers */
    extra_pointers = (extra_pointers_t*) malloc(LEN_EXTRA_POINTER * sizeof(extra_pointers_t));
    if (extra_pointers == NULL){
        printf("Out of mem for extra_pointers\n");
        return -1;
    }
    if (buffer_header == NULL) {
        printf("ERROR buffer header is NULL\n");
        return -1;
    }

    /* Read lengths from patch header */
    ctrllen=offtin(buffer_header+8);
    datalen=offtin(buffer_header+16);
    newsize=offtin(buffer_header+24);

    printf("newsize: %d\n", newsize);
    printf("ctrllen: %d\n", ctrllen);
    printf("datalen: %d\n", datalen);

    /* Get pointers into the header metadata */
    ctrlblock  = 32;
    diffblock  = 32+ctrllen;
    extrablock = 32+ctrllen+datalen;

    /* init positions */
    oldpos=0;newpos=0;patch_pos=0;

    __init_own_bsdiff = 1;
    return 0;
}

int own_bsdiff_ctrlblock(void) {
    if (load_extra_data) {
        printf("Leaving OWN controlblock");
        return 0;
    }

    /* set offset for patch_data */
    size_t offset_temp = diffblock;
    if (offset_temp <= FLASHPAGE_SIZE) {
        offset_patch_data = offset_temp;
        patch_pos += offset_patch_data;
    }

    /* Read control block */
    ctrl[0] = offtin(&buffer_header[ctrlblock]);
    ctrl[1] = offtin(&buffer_header[ctrlblock+8]);
    ctrl[2] = offtin(&buffer_header[ctrlblock+16]);

    ctrlblock += 24;

    /* print control block */
    //printf("ctrl0: %d\n", ctrl[0]);
    //printf("ctrl1: %d\n", ctrl[1]);
    //printf("ctrl2: %d\n", ctrl[2]);

    /* Sanity check */
    if(newpos+ctrl[0]>newsize) {
        printf("Ctrl0 bigger than newsize\n");
        return -3; /* Corrupt patch */
    }
    /* increment diffblock */
    diffblock += ctrl[0];

    i_loop = 0;
    loop++;

    return 0;
}

void extrablock_calculation(uint8_t* patch) {
    uint8_t* buf_flash;
    uint8_t* buf_new_data;

    buf_flash = (uint8_t*) malloc(FLASHPAGE_SIZE * sizeof(uint8_t));
    buf_new_data = (uint8_t*) malloc(FLASHPAGE_SIZE * sizeof(uint8_t));
    if (buf_flash == NULL && buf_new_data == NULL) {
        printf("ERROR init buf_extra\n");
        return;
    }

    size_t offset_patch = extrablock%ring_size;

    printf("EXTRA offset: %d\n", offset_patch);
    //__print_bin_data(patch,offset_patch,ring_size);

    for (uint8_t extra = 0; extra < entry_extrpointer; extra++) {

        printf("EXTRA entry: %d\n", extra);

        uint16_t page_offset = extra_pointers[extra].offset_pointer%FLASHPAGE_SIZE;
        uint8_t extra_size = extra_pointers[extra].size_pointer;

        if (extra_size) {
            size_t ptr = extra_pointers[extra].offset_pointer;
            void* addr = flashpage_addr(new_data_page);
            unsigned page = flashpage_page(addr + ptr);

            flashpage_read(page, buf_flash);
            //printf("flash data:\n");
            //__print_bin_data(buf_flash,0,FLASHPAGE_SIZE);

            bool extra_done_page = 0;
            /* write extra data to buf_new_data */
            for (int i = 0; i < FLASHPAGE_SIZE; i++) {
                /* write extra data */
                if (i == page_offset && !extra_done_page) {
                    for (int j = 0; j < extra_size; j++, i++) {
                        /* if buffer exceeded */
                        if (i >= FLASHPAGE_SIZE) {
                            printf("Buffer exceeded at %d.\n", j);
                            /* write data to flash */
                            printf("write page: %d\n", page);
                            flashpage_write_page(page,buf_new_data);
                            i = 0;
                            /* read new page */
                            page++;
                            flashpage_read(page, buf_flash);
                        }
                        if (offset_patch >= ring_size) {
                            /* patch exceeded */
                            printf("Extrablocks exceeded.\n");
                            extra_pointers[extra].size_pointer = extra_size-j;
                            extra_pointers[extra].offset_pointer = page_offset+j;
                            load_extra_data = 1;
                            free(buf_flash);
                            free(buf_new_data);
                            return;
                        }
                        buf_new_data[i] = patch[offset_patch];
                        offset_patch++;
                    }
                    extra_done_page = 1;
                }
                /* write flash data */
                buf_new_data[i] = buf_flash[i];
            }

            /* write data to flash */
            flashpage_write_page(page,buf_new_data);
        }

        /* mark extra content as done */
        extra_pointers[extra].size_pointer = 0;
    }
    printf("Extrablocks DONE!\n");
    calc_extra_blocks = 0;
    extra_blocks_done = 1;

    free(buf_flash);
    free(buf_new_data);
    return;
}

int for_loop(uint8_t* patch) {

    uint8_t temp;
    void* addr;
    unsigned curr_page = 0;

    for (; i_loop < ctrl[0]; i_loop++){

        offset_old_data = i_loop%FLASHPAGE_SIZE;
        /* check old_data_page */
        if ((old_data_page+1 - old_data_start_page)*FLASHPAGE_SIZE <= i_loop) {
            old_data_page++;
            //printf("read page: %d\n", old_data_page);
            flashpage_read(old_data_page, old_data);
        }
        if (oldpos) {
            addr = flashpage_addr(old_data_start_page);
            old_data_page = flashpage_page(addr+oldpos+i_loop);
            if (curr_page != old_data_page) {
                //printf("read page: %d\n", old_data_page);
                flashpage_read(old_data_page, old_data);
                curr_page = old_data_page;
            }
            offset_old_data = (oldpos + i_loop)%FLASHPAGE_SIZE;
        }

        /* check if patch buffer exceeded */
        if (offset_patch_data >= FLASHPAGE_SIZE) {
            //LOG_INFO("Buffer exceeded, breaking\n");
            offset_patch_data = 0;
            return 0;
        }
        else {//if ((oldpos+i_loop<oldsize)) {
            temp = patch[offset_patch_data] + old_data[offset_old_data];

            /* write data to storage */
            patch_pos++;
            write_inner_ring_buffer(&temp, 1);
            if (loop == 0) {
                printf("DATA: %x\n", temp);
                printf("offset old: %x\n", offset_old_data);
                printf("offset patch: %x\n", offset_patch_data);
            }
        }
        if (patch_pos >= extrablock && !extra_blocks_done) {
            if (!entry_extrpointer) {
                calc_extra_blocks = 0;
            }
            else {
                calc_extra_blocks = 1;
            }
            /* handle extrapointers */
            for (int i = 0; i < entry_extrpointer; i++) {
                printf("Extra offset %d, size %d\n",extra_pointers[i].offset_pointer, extra_pointers[i].size_pointer);
            }
            return 0;
        }
        offset_patch_data++;
    }
    return 1;
}

int own_bspatch(uint8_t* patch)
{
    /* Sanity checks */
    if (old_data == NULL || patch == NULL || old_data_page == 0) return -1;

    flashpage_read(old_data_page, old_data);

    if (!calc_extra_blocks) {
        i_loop_done = for_loop(patch);
    }

    if (calc_extra_blocks && !extra_blocks_done){
        extrablock_calculation(patch);
    }

    if (i_loop_done == 1) {
        //printf("Loop_done\n");

        /* Adjust pointers */
        newpos+=ctrl[0];
        oldpos+=ctrl[0];

        /* Sanity check */
        if(newpos+ctrl[1]>newsize) {
            /* finish inner_ring_buffer */
            uint8_t zero = 0x00;
            while (ptr_inner_ring) {
                write_inner_ring_buffer(&zero, 1);
            }
            return -3;
        }

        /* write empty extra data */
        uint8_t empty = 0xff;
        for (size_t i = 0; i < ctrl[1]; i++) {
            write_inner_ring_buffer(&empty, 1);
        }

        /* save extrapointers */
        extra_pointers[entry_extrpointer].offset_pointer = newpos;
        extra_pointers[entry_extrpointer].size_pointer = ctrl[1];
        entry_extrpointer++;

        //printf("extrapointer length: %d\n", entry_extrpointer);

        /* Adjust pointers */
        newpos+=ctrl[1];
        oldpos+=ctrl[2];
    }

    if (offset_patch_data && i_loop_done == 1 && !load_extra_data) {
        int res = own_bsdiff_ctrlblock();
        if (res == -1) {
            printf("Read new data Extracontrol\n");
            return 0;
        }
        else if (res != 0) {
            printf("ERROR controlblock\n");
        }
        //printf("do LOOP again!\n");
        //printf("patch_offset: %d\n", offset_patch_data);
        own_bspatch(patch);
    }
    return 0;
}

int init_ring_buffer(uint16_t size, suit_storage_t* storage, suit_manifest_t* manifest, unsigned page_old, unsigned page_new){
    if (manifest == NULL && storage == NULL){
        printf("Error manifest and storage equal NULL\n");
        return -1;
    }

    /* allocate ring_buffer */
    ring_buffer = (uint8_t*) malloc(size * sizeof(uint8_t));
    if (ring_buffer == NULL){
        printf("Allocating ring_buffer failed, Storage exceeded\n");
        return -2;
    }
    /* allocate innter_ring_buffer */
    inner_ring_buffer = (uint8_t*) malloc(size * sizeof(uint8_t));
    if (inner_ring_buffer == NULL){
        printf("Allocating ring_buffer failed, Storage exceeded\n");
        return -2;
    }
    /* set ring storage */
    ring_size = size;
    storage_offset = 0;
    /* set manifest and storage */
    manifest_ring_buffer = manifest;
    storage_ring_buffer = storage;
    /* set pages */
    new_data_page = page_new;
    old_data_page = page_old;
    old_data_start_page = page_old;

    return 0;
}

int write_ring_buffer(uint8_t* data, uint8_t length) {
    for (int i = 0; i < length; i++) {
        ring_buffer[ptr_ring] = data[i];
        ptr_ring++;
        if (ptr_ring == ring_size){
            /* patch the data */
            if (!__init_own_bsdiff) {
                buffer_header = (uint8_t*) malloc(LEN_DIFF_PATCH * SIZE_BUFFER_HEADER * sizeof(uint8_t));
                if (buffer_header == NULL) {
                    printf("ERROR init buffer_header\n");
                    return -1;
                }
                memcpy(buffer_header, ring_buffer, LEN_DIFF_PATCH);
                if (init_own_bsdiff() != 0) {
                    printf("ERROR: init own bsdiff\n");
                    return -1;
                }
                size_buffer_header_counter++;
            }
            else if (size_buffer_header_counter < SIZE_BUFFER_HEADER) {
                memcpy(&buffer_header[size_buffer_header_counter*LEN_DIFF_PATCH], ring_buffer, LEN_DIFF_PATCH);
                size_buffer_header_counter++;
            }
            /* check controlblock */
            if (newpos < newsize && i_loop_done) {
                if (own_bsdiff_ctrlblock() !=0) {
                    printf("ERROR controlblock\n");
                }
            }
            /* calculate data from diff, read until old_data is read */
            if (own_bspatch(ring_buffer) != 0) {
                printf("ERROR own bsdiff\n");
            }
            /* reset ring_buffer */
            ptr_ring = 0;
        }
        load_extra_data = 0;
    }
    return 0;
}

void free_pointers(void) {
    free(ring_buffer);
    free(inner_ring_buffer);
    free(extra_pointers);
    free(buffer_header);
}

int finish_write_ring_buffer(void) {
    if (ptr_inner_ring == 0) {
        printf("nothing to finish\n");
        storage_offset = 0;
        free_pointers();
        return 0;
    }
    else {
        uint8_t data = 0;
        while (newsize+256 > storage_offset) {
            write_ring_buffer(&data, 1);
        }
        if (ptr_inner_ring != 0){
            printf("ERROR finish went wrong\n");
            return -1;
        }
        storage_offset = 0;
        ptr_ring = 0;
        free_pointers();
        return 0;
    }
}

int suit_coap_get_blockwise(sock_udp_ep_t *remote, const char *path,
                            coap_blksize_t blksize,
                            coap_blockwise_cb_t callback, void *arg)
{
    /* mmmmh dynamically sized array */
    uint8_t buf[64 + (0x1 << (blksize + 4))];
    sock_udp_ep_t local = SOCK_IPV6_EP_ANY;
    coap_pkt_t pkt;

    /* HACK: use random local port */
    local.port = 0x8000 + (xtimer_now_usec() % 0XFFF);

    sock_udp_t sock;
    int res = sock_udp_create(&sock, &local, remote, 0);
    if (res < 0) {
        return res;
    }


    const uint32_t magic_pay = 0xa6d0aa74; /* header for heatshrink */
    //const uint8_t magic_pay_diff[4] = {0x4d, 0x42, 0x53, 0x44}; /* header for minibsdiff */

    uint8_t out_tmp[64];

    size_t n;
    uint8_t *inpos;

    int more = 1;
    size_t num = 0;
    res = -1;

    // getting manifest and storage
    suit_manifest_t *manifest = (suit_manifest_t *)arg;
    suit_component_t *comp = &manifest->components[manifest->component_current];
    suit_storage_t* storage = comp->storage_backend;


    /* getting flash-page from old_data */
    uint8_t slot = riotboot_slot_current();
    printf("Curr slot: %d\n", slot);
    uint32_t start_addr_old =  !slot ? SLOT0_OFFSET + 256 : SLOT1_OFFSET + 256;
    uint32_t start_addr_new =   slot ? SLOT0_OFFSET + 256 : SLOT1_OFFSET + 256;
    printf("Start_addr_old %lx\n", start_addr_old);
    printf("Start_addr_new %lx\n", start_addr_new);
    unsigned page_old = flashpage_page((const void *)start_addr_old);
    unsigned page_new = flashpage_page((const void *)start_addr_new);
    printf("Page_old: %d\n",page_old);
    printf("Page_new: %d\n",page_new);

    detect_patch = 0;

    while (more == 1) {
        //printf("fetching block %u\n", (unsigned)num);
        res = _fetch_block(&pkt, buf, &sock, path, blksize, num);
        //LOG_INFO("res=%i\n", res);

        if (!res) {
            coap_block1_t block2;
            coap_get_block2(&pkt, &block2);
            more = block2.more;

            /* decompress the data */
            n = pkt.payload_len;
            inpos = (uint8_t*)pkt.payload;

            /* check if patch packages are received, after header transmission */
            if (block2.offset == 256 && !detect_patch){
                uint32_t header_check = pkt.payload[0]<<24 | pkt.payload[1]<<16 |
                                        pkt.payload[2]<< 8 | pkt.payload[3];
                /* allocate space for decompression and patching */
                if(header_check == magic_pay){
                    detect_patch = 1;

                    heatshrink_decoder_reset(&_decoder);

                    if (init_ring_buffer(LEN_DIFF_PATCH, storage, manifest, page_old, page_new) != 0){
                        printf("INIT ring_buffer failed\n");
                        return -1;
                    }

                    printf("DECOMPRESSING!\n");
                    storage_offset = 256;
                }
            }
            /* start decompressing package and patching firmware */
            if (!strncmp(&path[strlen(path) - 8], "riot.bin", 8) && detect_patch){
                printf("fetching block %u\n", (unsigned)num);

                /* decompress the data */
                size_t written = 0;
                while(1) {
                    size_t n_sunk = 0;
                    if (n) {
                        heatshrink_decoder_sink(&_decoder, inpos, n, &n_sunk);
                        if (n_sunk) {
                            inpos += n_sunk;
                            n -= n_sunk;
                        }
                        heatshrink_decoder_poll(&_decoder, out_tmp, DECODER_POLL, &written);
                        write_ring_buffer(out_tmp, written);
                        written = 0;
                    }
                    else {
                        while (heatshrink_decoder_finish(&_decoder) == HSDR_FINISH_MORE) {
                            heatshrink_decoder_poll(&_decoder, out_tmp, DECODER_POLL, &written);
                            write_ring_buffer(out_tmp, written);
                            written = 0;
                        }
                        break;
                    }
                }
            }
            /* get normal data */
            else{
                if (callback(arg, block2.offset, pkt.payload, pkt.payload_len, more)) {
                    DEBUG("callback res != 0, aborting.\n");
                    res = -1;
                    goto out;
                }
            }
        }
        else {
            DEBUG("error fetching block\n");
            res = -1;
            goto out;
        }

        num += 1;
    }

    if (detect_patch){

        /* Finish ring buffer */
        if (finish_write_ring_buffer() != 0){
            printf("FINISH ring buffer failed\n");
        }
    }

out:
    printf("Num: %d\n", num);
    sock_udp_close(&sock);
    return res;
}

int suit_coap_get_blockwise_url(const char *url,
                                coap_blksize_t blksize,
                                coap_blockwise_cb_t callback, void *arg)
{
    char hostport[CONFIG_SOCK_HOSTPORT_MAXLEN];
    char urlpath[CONFIG_SOCK_URLPATH_MAXLEN];
    sock_udp_ep_t remote;

    if (strncmp(url, "coap://", 7)) {
        LOG_INFO("suit: URL doesn't start with \"coap://\"\n");
        return -EINVAL;
    }

    if (sock_urlsplit(url, hostport, urlpath) < 0) {
        LOG_INFO("suit: invalid URL\n");
        return -EINVAL;
    }

    if (sock_udp_str2ep(&remote, hostport) < 0) {
        LOG_INFO("suit: invalid URL\n");
        return -EINVAL;
    }

    if (!remote.port) {
        remote.port = COAP_PORT;
    }

    return suit_coap_get_blockwise(&remote, urlpath, blksize, callback, arg);
}

typedef struct {
    size_t offset;
    uint8_t *ptr;
    size_t len;
} _buf_t;

static int _2buf(void *arg, size_t offset, uint8_t *buf, size_t len, int more)
{
    (void)more;

    _buf_t *_buf = arg;
    if (_buf->offset != offset) {
        return 0;
    }
    if (len > _buf->len) {
        return -1;
    }
    else {
        memcpy(_buf->ptr, buf, len);
        _buf->offset += len;
        _buf->ptr += len;
        _buf->len -= len;
        return 0;
    }
}

ssize_t suit_coap_get_blockwise_url_buf(const char *url,
                                        coap_blksize_t blksize,
                                        uint8_t *buf, size_t len)
{
    _buf_t _buf = { .ptr = buf, .len = len };
    int res = suit_coap_get_blockwise_url(url, blksize, _2buf, &_buf);

    return (res < 0) ? (ssize_t)res : (ssize_t)_buf.offset;
}

static void _suit_handle_url(const char *url)
{
    LOG_INFO("suit_coap: downloading \"%s\"\n", url);
    ssize_t size = suit_coap_get_blockwise_url_buf(url, CONFIG_SUIT_COAP_BLOCKSIZE,
                                                   _manifest_buf,
                                                   SUIT_MANIFEST_BUFSIZE);
    if (size >= 0) {
        LOG_INFO("suit_coap: got manifest with size %u\n", (unsigned)size);

#ifdef MODULE_SUIT
        suit_manifest_t manifest;
        memset(&manifest, 0, sizeof(manifest));

        manifest.urlbuf = _url;
        manifest.urlbuf_len = SUIT_URL_MAX;

        int res;
        if ((res = suit_parse(&manifest, _manifest_buf, size)) != SUIT_OK) {
            LOG_INFO("suit_parse() failed. res=%i\n", res);
            return;
        }

#endif
#ifdef MODULE_SUIT_STORAGE_FLASHWRITE
        if (res == 0) {
            const riotboot_hdr_t *hdr = riotboot_slot_get_hdr(
                riotboot_slot_other());
            riotboot_hdr_print(hdr);
            xtimer_sleep(1);

            if (riotboot_hdr_validate(hdr) == 0) {
                LOG_INFO("suit_coap: rebooting...\n");
                pm_reboot();
            }
            else {
                LOG_INFO("suit_coap: update failed, hdr invalid\n ");
            }
        }
#endif
    }
    else {
        LOG_INFO("suit_coap: error getting manifest\n");
    }
}

int suit_storage_helper(void *arg, size_t offset, uint8_t *buf, size_t len,
                        int more)
{
    suit_manifest_t *manifest = (suit_manifest_t *)arg;

    uint32_t image_size;
    nanocbor_value_t param_size;
    size_t total = offset + len;
    suit_component_t *comp = &manifest->components[manifest->component_current];
    suit_param_ref_t *ref_size = &comp->param_size;

    /* Grab the total image size from the manifest */
    if ((suit_param_ref_to_cbor(manifest, ref_size, &param_size) == 0) ||
            (nanocbor_get_uint32(&param_size, &image_size) < 0)) {
        /* Early exit if the total image size can't be determined */
        return -1;
    }

    if (image_size < offset + len) {
        /* Extra newline at the start to compensate for the progress bar */
        LOG_ERROR(
            "\n_suit_coap(): Image beyond size, offset + len=%u, "
            "image_size=%u\n", (unsigned)(total), (unsigned)image_size);
        return -1;
    }

    if (!more && image_size != total) {
        LOG_INFO("Incorrect size received, got %u, expected %u\n",
                 (unsigned)total, (unsigned)image_size);
        return -1;
    }

    _print_download_progress(manifest, offset, len, image_size);

    int res = suit_storage_write(comp->storage_backend, manifest, buf, offset, len);
    if (!more) {
        LOG_INFO("Finalizing payload store\n");
        /* Finalize the write if no more data available */
        res = suit_storage_finish(comp->storage_backend, manifest);
    }
    return res;
}

static void *_suit_coap_thread(void *arg)
{
    (void)arg;

    LOG_INFO("suit_coap: started.\n");
    msg_t msg_queue[4];
    msg_init_queue(msg_queue, 4);

    _suit_coap_pid = thread_getpid();

    msg_t m;
    while (true) {
        msg_receive(&m);
        DEBUG("suit_coap: got msg with type %" PRIu32 "\n", m.content.value);
        switch (m.content.value) {
            case SUIT_MSG_TRIGGER:
                LOG_INFO("suit_coap: trigger received\n");
                _suit_handle_url(_url);
                break;
            default:
                LOG_WARNING("suit_coap: warning: unhandled msg\n");
        }
    }
    return NULL;
}

void suit_coap_run(void)
{
    thread_create(_stack, SUIT_COAP_STACKSIZE, SUIT_COAP_PRIO,
                  THREAD_CREATE_STACKTEST,
                  _suit_coap_thread, NULL, "suit_coap");
}

static ssize_t _version_handler(coap_pkt_t *pkt, uint8_t *buf, size_t len,
                                void *context)
{
    (void)context;
    return coap_reply_simple(pkt, COAP_CODE_205, buf, len,
                             COAP_FORMAT_TEXT, (uint8_t *)"NONE", 4);
}

#ifdef MODULE_RIOTBOOT_SLOT
static ssize_t _slot_handler(coap_pkt_t *pkt, uint8_t *buf, size_t len,
                             void *context)
{
    /* context is passed either as NULL or 0x1 for /active or /inactive */
    char c = '0';

    if (context) {
        c += riotboot_slot_other();
    }
    else {
        c += riotboot_slot_current();
    }

    return coap_reply_simple(pkt, COAP_CODE_205, buf, len,
                             COAP_FORMAT_TEXT, (uint8_t *)&c, 1);
}
#endif

static ssize_t _trigger_handler(coap_pkt_t *pkt, uint8_t *buf, size_t len,
                                void *context)
{
    (void)context;
    unsigned code;
    size_t payload_len = pkt->payload_len;
    if (payload_len) {
        if (payload_len >= SUIT_URL_MAX) {
            code = COAP_CODE_REQUEST_ENTITY_TOO_LARGE;
        }
        else {
            code = COAP_CODE_CREATED;
            LOG_INFO("suit: received URL: \"%s\"\n", (char *)pkt->payload);
            suit_coap_trigger(pkt->payload, payload_len);
        }
    }
    else {
        code = COAP_CODE_REQUEST_ENTITY_INCOMPLETE;
    }

    return coap_reply_simple(pkt, code, buf, len,
                             COAP_FORMAT_NONE, NULL, 0);
}

void suit_coap_trigger(const uint8_t *url, size_t len)
{
    memcpy(_url, url, len);
    _url[len] = '\0';
    msg_t m = { .content.value = SUIT_MSG_TRIGGER };
    msg_send(&m, _suit_coap_pid);
}

static const coap_resource_t _subtree[] = {
#ifdef MODULE_RIOTBOOT_SLOT
    { "/suit/slot/active", COAP_METHOD_GET, _slot_handler, NULL },
    { "/suit/slot/inactive", COAP_METHOD_GET, _slot_handler, (void *)0x1 },
#endif
    { "/suit/trigger", COAP_METHOD_PUT | COAP_METHOD_POST, _trigger_handler,
      NULL },
    { "/suit/version", COAP_METHOD_GET, _version_handler, NULL },
};

const coap_resource_subtree_t coap_resource_subtree_suit =
{
    .resources = &_subtree[0],
    .resources_numof = ARRAY_SIZE(_subtree)
};
