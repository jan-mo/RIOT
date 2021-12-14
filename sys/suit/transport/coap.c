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




#include "suit/bspatch.h"
#include "heatshrink_decoder.h"

bool detect_patch = 0;

uint8_t* buffer_decomp;
uint8_t* buffer_firmware;
uint8_t size_full_paylad;


uint8_t ring_size = 0;
uint8_t ptr_ring = 0;
uint8_t* ring_buffer;

size_t storage_offset = 0;

suit_storage_t* storage_ring_buffer = NULL;
suit_manifest_t* manifest_ring_buffer = NULL;


static heatshrink_decoder _decoder;

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

int init_ring_buffer(uint8_t size, suit_storage_t* storage, suit_manifest_t* manifest){
    if (manifest == NULL && storage == NULL){
        printf("Error manifest and storage equal NULL\n");
        return -1;
    }

    ring_buffer = (uint8_t*) malloc(size * sizeof(uint8_t));
    if (ring_buffer == NULL){
        printf("Allocating ring_buffer failed, Storage exceeded\n");
        return -2;
    }
    ring_size = size;

    manifest_ring_buffer = manifest;
    storage_ring_buffer = storage;

    storage_offset = 0;

    return 0;
}

void __print_bin_data(uint8_t* data, size_t start, size_t end){
    if (end%16 != 0)
        end = end + end%16;
    for (size_t ptr = start; ptr < end; ptr = ptr+16) {
        printf("%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x\n",
            data[ptr],data[ptr+1],data[ptr+2],data[ptr+3],data[ptr+4],data[ptr+5],data[ptr+6],data[ptr+7],
            data[ptr+8],data[ptr+9],data[ptr+10],data[ptr+11],data[ptr+12],data[ptr+13],data[ptr+14],data[ptr+15]);
    }
}

int write_ring_buffer(uint8_t* data, uint8_t length){
    if (storage_ring_buffer == NULL || manifest_ring_buffer == 0){
        printf("Ring buffer storage and manifest not initialized\n");
        return -2;
    }
    for (int i = 0; i < length; i++){
        ring_buffer[ptr_ring] = data[i];
        ptr_ring++;
        if (ptr_ring == ring_size){
            if (suit_storage_write(storage_ring_buffer, manifest_ring_buffer, ring_buffer, storage_offset, ring_size) != SUIT_OK){
                printf("Write Buffer to Storage failed!\n");
                return -1;
            }
            storage_offset += ring_size;
            ptr_ring = 0;
        }
    }
    return 0;
}

int finish_write_ring_buffer(void){
    if (ptr_ring == 0) {
        printf("nothing to finish\n");
        storage_offset = 0;
        return 0;
    }
    else {
        for (int i = 0; ptr_ring != 0; i++) {
            uint8_t data = 0;
            write_ring_buffer(&data, 1);
        }
        if (ptr_ring != 0){
            printf("finish went wrong\n");
            return -1;
        }
        storage_offset = 0;
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


    static uint32_t magic_pay = 0xa6d0aa74; /* header for heatshrink */
    static uint32_t magic_pay_diff = 0x4d425344; /* header for minibsdiff */

    (void) magic_pay_diff;


    uint8_t out_tmp[64];

    size_t n;
    uint8_t *inpos;

    int more = 1;
    size_t num = 0;
    res = -1;
    while (more == 1) {
        DEBUG("fetching block %u\n", (unsigned)num);
        res = _fetch_block(&pkt, buf, &sock, path, blksize, num);
        DEBUG("res=%i\n", res);

        if (!res) {
            coap_block1_t block2;
            coap_get_block2(&pkt, &block2);
            more = block2.more;


            /* decompress the data */
            n = pkt.payload_len;
            inpos = (uint8_t*)pkt.payload;

            /* check if patch packages are received */
            if (block2.offset == 0 && !detect_patch){
                uint32_t header_check = pkt.payload[0]<<24 | pkt.payload[1]<<16 |
                                        pkt.payload[2]<< 8 | pkt.payload[3];
                /* allocate space for decompression and patching */
                if(header_check == magic_pay){
                    detect_patch = 1;
                    buffer_decomp = (uint8_t*)malloc( 1 * pkt.payload_len * sizeof(uint8_t) );
                    buffer_firmware = (uint8_t*)malloc( 4 * pkt.payload_len * sizeof(uint8_t) );

                    size_full_paylad = offtin(pkt.payload+24);
                    printf("Full payload: %d\n", size_full_paylad);
                    heatshrink_decoder_reset(&_decoder);

                    // getting manifest and storage
                    suit_manifest_t *manifest = (suit_manifest_t *)arg;
                    suit_component_t *comp = &manifest->components[manifest->component_current];
                    suit_storage_t* storage = comp->storage_backend;
                    if (init_ring_buffer(pkt.payload_len, storage, manifest) != 0){
                        printf("INIT ring_buffer failed\n");
                        return -1;
                    }

                    printf("DECOMPRESSING!\n");
                }
            }
            /* start decompressing package and patching firmware */
            if (!strncmp(&path[strlen(path) - 8], "riot.bin", 8) && detect_patch){

                if (buffer_decomp == NULL || buffer_firmware == NULL)
                    printf("ERROR allocation!\n");

                /* decompress the data */
                /* decompress */
                size_t written = 0;
                while(1) {
                    size_t n_sunk = 0;
                    if (n) {
                        heatshrink_decoder_sink(&_decoder, inpos, n, &n_sunk);
                        if (n_sunk) {
                            inpos += n_sunk;
                            n -= n_sunk;
                        }
                        heatshrink_decoder_poll(&_decoder, out_tmp, ring_size, &written);
                        write_ring_buffer(out_tmp, written);
                        written = 0;
                    }
                    else {
                        while (heatshrink_decoder_finish(&_decoder) == HSDR_FINISH_MORE) {
                            heatshrink_decoder_poll(&_decoder, out_tmp, ring_size, &written);
                            write_ring_buffer(out_tmp, written);
                            written = 0;
                        }
                        break;
                    }
                }

                /* write calculated firmware data to storage */
                /*if (callback(arg, block2.offset, pkt.payload, pkt.payload_len, more)) {
                    DEBUG("callback res != 0, aborting.\n");
                    res = -1;
                    goto out;
                }
                */
                /* TODO: updating image_size of manifest at the end !!! */
                /* patch done */
                //detect_patch = 0;
                //free(buffer_decomp);
                //free(buffer_firmware);
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

    printf("FINISH ring buffer\n");
    if (finish_write_ring_buffer() != 0){
        printf("FINISH ring buffer failed\n");
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
