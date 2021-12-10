/*
 * Copyright (C) 2019 Koen Zandberg
 *               2020 Inria
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
 * @brief       SUIT Handlers for the command sequences in the common section of
 *              a SUIT manifest.
 *
 * This file contains the functions to handle command sequences from a SUIT
 * manifest. This includes both directives and conditions.
 *
 * @author      Koen Zandberg <koen@bergzand.net>
 *
 * @}
 */

#include <inttypes.h>
#include <nanocbor/nanocbor.h>
#include <assert.h>

#include "fmt.h"

#include "bspatch.h"
#include "heatshrink_decoder.h"

#include "hashes/sha256.h"

#include "kernel_defines.h"
#include "suit/conditions.h"
#include "suit/handlers.h"
#include "suit/policy.h"
#include "suit/storage.h"
#include "suit.h"

#ifdef MODULE_SUIT_TRANSPORT_COAP
#include "suit/transport/coap.h"
#endif
#include "suit/transport/mock.h"

#include "log.h"


#define ring_size 64
uint8_t ptr_ring = 0;
uint8_t ring_buffer[ring_size];

suit_storage_t* storage_ring_buffer = NULL;
suit_manifest_t* manifest_ring_buffer = NULL;
size_t storage_offset = 0;

static int _get_component_size(suit_manifest_t *manifest,
                               suit_component_t *comp,
                               uint32_t *img_size)
{
    nanocbor_value_t param_size;
    if ((suit_param_ref_to_cbor(manifest, &comp->param_size, &param_size) == 0)
            || (nanocbor_get_uint32(&param_size, img_size) < 0)) { return
        SUIT_ERR_INVALID_MANIFEST;
    }
    return SUIT_OK;
}

static suit_component_t *_get_component(suit_manifest_t *manifest)
{
    /* Out-of-bounds check has been done in the _dtv_set_comp_idx, True/False
     * not handled here intentionally */
    assert(manifest->component_current < CONFIG_SUIT_COMPONENT_MAX);
    return &manifest->components[manifest->component_current];
}

static int _validate_uuid(suit_manifest_t *manifest,
                          suit_param_ref_t *ref,
                          uuid_t *uuid)
{
    const uint8_t *uuid_manifest_ptr;
    size_t len = sizeof(uuid_t);
    nanocbor_value_t it;

    if ((suit_param_ref_to_cbor(manifest, ref, &it) == 0) ||
            (nanocbor_get_bstr(&it, &uuid_manifest_ptr, &len) < 0)) {
        return SUIT_ERR_INVALID_MANIFEST;
    }

    char uuid_str[UUID_STR_LEN + 1];
    char uuid_str2[UUID_STR_LEN + 1];
    uuid_to_string((uuid_t *)uuid_manifest_ptr, uuid_str);
    uuid_to_string(uuid, uuid_str2);
    LOG_INFO("Comparing %s to %s from manifest\n", uuid_str2, uuid_str);

    return uuid_equal(uuid, (uuid_t *)uuid_manifest_ptr)
           ? SUIT_OK
           : SUIT_ERR_COND;
}

static int _cond_vendor_handler(suit_manifest_t *manifest,
                                int key,
                                nanocbor_value_t *it)
{
    (void)key;
    (void)it;
    LOG_INFO("validating vendor ID\n");
    suit_component_t *comp = _get_component(manifest);
    int rc = _validate_uuid(manifest, &comp->param_vendor_id,
                            suit_get_vendor_id());
    if (rc == SUIT_OK) {
        LOG_INFO("validating vendor ID: OK\n");
        manifest->validated |= SUIT_VALIDATED_VENDOR;
    }
    return rc;
}

static int _cond_class_handler(suit_manifest_t *manifest,
                               int key,
                               nanocbor_value_t *it)
{
    (void)key;
    (void)it;
    LOG_INFO("validating class id\n");
    suit_component_t *comp = _get_component(manifest);
    int rc = _validate_uuid(manifest, &comp->param_class_id,
                            suit_get_class_id());
    if (rc == SUIT_OK) {
        LOG_INFO("validating class id: OK\n");
        manifest->validated |= SUIT_VALIDATED_CLASS;
    }
    return rc;
}

static int _cond_comp_offset(suit_manifest_t *manifest,
                             int key,
                             nanocbor_value_t *it)
{
    (void)manifest;
    (void)key;
    uint32_t offset;
    uint32_t report;

    suit_component_t *comp = _get_component(manifest);

    /* Grab offset from param */
    if (nanocbor_get_uint32(it, &report) < 0) {
        LOG_WARNING("_cond_comp_offset(): expected None param\n");
        return SUIT_ERR_INVALID_MANIFEST;
    }
    nanocbor_value_t param_offset;
    suit_param_ref_to_cbor(manifest, &comp->param_component_offset,
                           &param_offset);
    nanocbor_get_uint32(&param_offset, &offset);

    if (!suit_storage_has_offset(comp->storage_backend)) {
        return SUIT_ERR_COND;
    }

    LOG_INFO("Comparing manifest offset %"PRIx32" with other slot offset\n",
             offset);

    return suit_storage_match_offset(comp->storage_backend, offset) ?
        SUIT_OK : SUIT_ERR_COND;
}

static int _dtv_set_comp_idx(suit_manifest_t *manifest,
                             int key,
                             nanocbor_value_t *it)
{
    (void)key;
    bool index = false;
    uint32_t new_index;

    /* It can be a bool, meaning all or none of the components */
    if (nanocbor_get_bool(it, &index) >= 0) {
        new_index = index ?
            SUIT_MANIFEST_COMPONENT_ALL : SUIT_MANIFEST_COMPONENT_NONE;
    }
    /* It can be a positive integer, meaning one of the components */
    else if (nanocbor_get_uint32(it, &new_index) < 0) {
        return SUIT_ERR_INVALID_MANIFEST;
    }
    /* And if it is an integer it must be within the allowed bounds */
    else if (new_index >= CONFIG_SUIT_COMPONENT_MAX) {
        return SUIT_ERR_INVALID_MANIFEST;
    }

    suit_component_t *component = &manifest->components[new_index];
    char name[CONFIG_SUIT_COMPONENT_MAX_NAME_LEN];

    suit_storage_t *storage = component->storage_backend;
    char separator = suit_storage_get_separator(storage);

    /* Done this before in the component stage, shouldn't be different now */
    suit_component_name_to_string(manifest, component,
                                  separator, name, sizeof(name));

    suit_storage_set_active_location(storage, name);

    /* Update the manifest context */
    manifest->component_current = new_index;

    LOG_INFO("Setting component index to %d\n",
              (int)manifest->component_current);
    return 0;
}

static int _dtv_run_seq_cond(suit_manifest_t *manifest,
                             int key,
                             nanocbor_value_t *it)
{
    (void)key;
    LOG_DEBUG("Starting conditional sequence handler\n");
    return suit_handle_manifest_structure_bstr(manifest, it,
            suit_command_sequence_handlers, suit_command_sequence_handlers_len);
}

static int _dtv_try_each(suit_manifest_t *manifest,
                         int key, nanocbor_value_t *it)
{
    (void)key;
    LOG_DEBUG("Starting suit-directive-try-each handler\n");
    nanocbor_value_t container;

    if ((nanocbor_enter_array(it, &container) < 0) &&
        (nanocbor_enter_map(it, &container) < 0)) {
        return SUIT_ERR_INVALID_MANIFEST;
    }

    int res = SUIT_ERR_COND;
    while (!nanocbor_at_end(&container)) {
        nanocbor_value_t _container = container;
        /* `_container` should be CBOR _bstr wrapped according to the spec, but
         * it is not */
        res = suit_handle_manifest_structure_bstr(manifest, &_container,
                suit_command_sequence_handlers,
                suit_command_sequence_handlers_len);

        nanocbor_skip(&container);

        if (res != SUIT_ERR_COND) {
            break;
        }
    }

    return res;
}

static int _dtv_set_param(suit_manifest_t *manifest, int key,
                          nanocbor_value_t *it)
{
    (void)key;
    /* `it` points to the entry of the map containing the type and value */
    nanocbor_value_t map;

    nanocbor_enter_map(it, &map);

    suit_component_t *comp = _get_component(manifest);

    while (!nanocbor_at_end(&map)) {
        /* map points to the key of the param */
        int32_t param_key;
        if (nanocbor_get_int32(&map, &param_key) < 0) {
            return SUIT_ERR_INVALID_MANIFEST;
        }
        LOG_DEBUG("param_key=%" PRIi32 "\n", param_key);
        unsigned int type = nanocbor_get_type(&map);
        /* Filter 'complex' types and only allow int, nint, bstr and tstr types
         * for parameter values */
        if (type > NANOCBOR_TYPE_TSTR) {
            return SUIT_ERR_INVALID_MANIFEST;
        }
        suit_param_ref_t *ref;
        switch (param_key) {
            case SUIT_PARAMETER_VENDOR_IDENTIFIER:
                ref = &comp->param_vendor_id;
                break;
            case SUIT_PARAMETER_CLASS_IDENTIFIER:
                ref = &comp->param_class_id;
                break;
            case SUIT_PARAMETER_IMAGE_DIGEST:
                ref = &comp->param_digest;
                break;
            case SUIT_PARAMETER_COMPONENT_OFFSET:
                ref = &comp->param_component_offset;
                break;
            case SUIT_PARAMETER_IMAGE_SIZE:
                ref = &comp->param_size;
                break;
            case SUIT_PARAMETER_URI:
                ref = &comp->param_uri;
                break;
            default:
                LOG_DEBUG("Unsupported parameter %" PRIi32 "\n", param_key);
                return SUIT_ERR_UNSUPPORTED;
        }

        suit_param_cbor_to_ref(manifest, ref, &map);

        /* Simple skip is sufficient to skip non-complex types */
        nanocbor_skip(&map);
    }
    return SUIT_OK;
}

static int _start_storage(suit_manifest_t *manifest, suit_component_t *comp)
{
    uint32_t img_size = 0;
    char name[CONFIG_SUIT_COMPONENT_MAX_NAME_LEN];
    char separator = suit_storage_get_separator(comp->storage_backend);

    if (_get_component_size(manifest, comp, &img_size) < 0) {
        return SUIT_ERR_INVALID_MANIFEST;
    }

    /* Done this before in the component stage, shouldn't be different now */
    suit_component_name_to_string(manifest, comp,
                                  separator, name, sizeof(name));

    suit_storage_set_active_location(comp->storage_backend, name);

    return suit_storage_start(comp->storage_backend, manifest, img_size);
}

static int _dtv_fetch(suit_manifest_t *manifest, int key,
                      nanocbor_value_t *_it)
{
    (void)key; (void)_it;
    LOG_DEBUG("_dtv_fetch() key=%i\n", key);

    const uint8_t *url;
    size_t url_len;

    /* Check the policy before fetching anything */
    int res = suit_policy_check(manifest);
    if (res) {
        return SUIT_ERR_POLICY_FORBIDDEN;
    }

    suit_component_t *comp = _get_component(manifest);

    /* Deny the fetch if the component was already fetched before */
    if (suit_component_check_flag(comp, SUIT_COMPONENT_STATE_FETCHED)) {
        LOG_ERROR("Component already fetched before\n");
        return SUIT_ERR_INVALID_MANIFEST;
    }

    nanocbor_value_t param_uri;
    suit_param_ref_to_cbor(manifest, &comp->param_uri,
                           &param_uri);
    int err = nanocbor_get_tstr(&param_uri, &url, &url_len);
    if (err < 0) {
        LOG_DEBUG("URL parsing failed\n)");
        return err;
    }
    memcpy(manifest->urlbuf, url, url_len);
    manifest->urlbuf[url_len] = '\0';

    LOG_DEBUG("_dtv_fetch() fetching \"%s\" (url_len=%u)\n", manifest->urlbuf,
              (unsigned)url_len);

    if (_start_storage(manifest, comp) < 0) {
        LOG_ERROR("Unable to start storage backend\n");
        return SUIT_ERR_STORAGE;
    }

    res = -1;

    if (0) {}
#ifdef MODULE_SUIT_TRANSPORT_COAP
    else if (strncmp(manifest->urlbuf, "coap://", 7) == 0) {
        res = suit_coap_get_blockwise_url(manifest->urlbuf, CONFIG_SUIT_COAP_BLOCKSIZE,
                                          suit_storage_helper,
                                          manifest);
    }
#endif
#ifdef MODULE_SUIT_TRANSPORT_MOCK
    else if (strncmp(manifest->urlbuf, "test://", 7) == 0) {
        res = suit_transport_mock_fetch(manifest);
    }
#endif
    else {
        LOG_WARNING("suit: unsupported URL scheme!\n)");
        return res;
    }

    suit_component_set_flag(comp, SUIT_COMPONENT_STATE_FETCHED);

    if (res) {
        suit_component_set_flag(comp, SUIT_COMPONENT_STATE_FETCH_FAILED);
        /* TODO: The leftover data from a failed fetch should be purged. It
         * could contain potential malicious data from an attacker */
        LOG_INFO("image download failed with code %i\n", res);
        return res;
    }

    LOG_DEBUG("Update OK\n");
    return SUIT_OK;
}

static int _get_digest(nanocbor_value_t *bstr, const uint8_t **digest, size_t
                       *digest_len)
{
    /* Bstr is a byte string with a cbor array containing the type and the
     * digest */

    const uint8_t *digest_struct;
    size_t digest_struct_len;
    uint32_t digest_type;
    nanocbor_value_t digest_it;
    nanocbor_value_t arr_it;

    nanocbor_get_bstr(bstr, &digest_struct, &digest_struct_len);

    nanocbor_decoder_init(&digest_it, digest_struct, digest_struct_len);
    nanocbor_enter_array(&digest_it, &arr_it);
    nanocbor_get_uint32(&arr_it, &digest_type);
    return nanocbor_get_bstr(&arr_it, digest, digest_len);
}

static int write_ring_buffer(uint8_t* data, uint8_t length){
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

static int finish_write_ring_buffer(void){
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

static void print_bin_data(uint8_t* data, size_t start, size_t end){
    if (end%16 != 0)
        end = end + end%16;
    for (size_t ptr = start; ptr < end; ptr = ptr+16) {
        printf("%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x\n",
            data[ptr],data[ptr+1],data[ptr+2],data[ptr+3],data[ptr+4],data[ptr+5],data[ptr+6],data[ptr+7],
            data[ptr+8],data[ptr+9],data[ptr+10],data[ptr+11],data[ptr+12],data[ptr+13],data[ptr+14],data[ptr+15]);
    }
}

static int _validate_payload(suit_component_t *component, const uint8_t *digest,
                             size_t payload_size, suit_manifest_t* manifest)
{
    uint8_t payload_digest[SHA256_DIGEST_LENGTH];
    suit_storage_t *storage = component->storage_backend;

    if (suit_storage_has_readptr(storage)) {
        /* Direct read possible */
        const uint8_t *payload = NULL;
        size_t payload_len = 0;

        suit_storage_read_ptr(storage, &payload, &payload_len);
        if (payload_size != payload_len) {
            return SUIT_ERR_STORAGE_EXCEEDED;
        }
        sha256(payload, payload_len, payload_digest);
    }
    else {
        /* Piecewise feeding */
        sha256_context_t ctx;
        sha256_init(&ctx);
        size_t pos = 0;
        while (pos < payload_size) {
            uint8_t buf[64];

            size_t read_len = (payload_size - pos) > sizeof(buf) ?
                              sizeof(buf) : payload_size - pos;

            suit_storage_read(storage, buf, pos, read_len);
            sha256_update(&ctx, buf, read_len);

            pos += read_len;
        }
        sha256_final(&ctx, payload_digest);
    }

    if (memcmp(digest, payload_digest, SHA256_DIGEST_LENGTH) == 0){
        return SUIT_OK;
    }

    else {
        /* payload magic */
        //uint8_t magic_pay[4] = {0x50, 0x45, 0x41, 0x52}; /* header for bsdiff */
        //uint8_t magic_pay[4] = {0x44, 0x45, 0x46, 0x30}; /* header for  miniz */
        uint8_t magic_pay[4] = {0xa6, 0xd0, 0xaa, 0x74}; /* header for heatshrink */
        uint8_t magic_pay_diff[4] = {0x4d, 0x42, 0x53, 0x44}; /* header for minibsdiff */

        /* read payload */
        printf("PayloadSize: %d\n", payload_size);
        //#define size_buffer_max 1024
        //payload_size = payload_size > size_buffer_max ? size_buffer_max : payload_size;
        //uint8_t payload[size_buffer_max];

        uint8_t* payload;
        payload = (uint8_t*) malloc( payload_size * sizeof(uint8_t) );

        bool payload_to_big = 0;
        if (payload == NULL) {
            printf("NULL pointer!!\n");
            printf("to much payload, create new component!\n");
            payload_to_big = 1;

            printf("For now only use 1024 for payload\n");
            payload_size = 1024;
            payload = (uint8_t*) malloc( payload_size * sizeof(uint8_t) );


            /*printf("Switch component\n");
            printf("Comp current %d\n", manifest->component_current);
            if (manifest->component_current < CONFIG_SUIT_COMPONENT_MAX-1)
                manifest->component_current++;
            printf("Comp current %d\n", manifest->component_current);

            suit_component_t* new = _get_component(manifest);
            suit_storage_t* storage_new = new->storage_backend;

            printf("Copy payload.\n");
            int retur = suit_storage_start(storage, manifest, payload_size);
            printf("START: %d\n", retur);

            uint8_t pay_buffer[64];
            for (size_t i = 0;; i = i + 64){
                suit_storage_read(storage, pay_buffer, i, 64);
                suit_storage_write(storage_new, manifest, pay_buffer, i, 64);
            }


            retur = suit_storage_finish(storage, manifest);
            printf("FINISH: %d\n", retur);

            printf("Validate reading\n");
            storage = storage_new;
            */

        }
        if (suit_storage_read(storage, payload, 0, payload_size) != SUIT_OK){
            printf("Error reading storage\n");
        }

        /* modify compression payload */
        /* first 4 byte are different (depending on bsdiff) */
        payload[0] = magic_pay[0];
        payload[1] = magic_pay[1];
        payload[2] = magic_pay[2];
        payload[3] = magic_pay[3];

        /* print payload content */
        //size_t size_buf = (payload_size >= 16*25) ? 16*25 : payload_size;
        print_bin_data(payload, 0, 256);
        printf("\n");
        printf("\n");
        print_bin_data(payload, payload_size-256, payload_size);

        /* calc checksum to verify compression */
        sha256(payload, payload_size, payload_digest);
        if (payload_to_big || memcmp(digest, payload_digest, SHA256_DIGEST_LENGTH) == 0) {
            if (!payload_to_big)
                printf("Checksum PASSED\n");
            else
                printf("Skip Checksum\n");

            printf("Compression detected!\n");

            /* decompress payload */
            int64_t oldsize, newsize;

            /* first decompress data (miniz) */
            //mz_ulong length = 2048;
            //unsigned char dest[length];

            //int error = mz_uncompress(dest, &length, (const unsigned char*) payload, (mz_ulong)payload_size);
            //if (error != MZ_OK) {
            //   printf("Error MZ: %d\n", error);
            //    return -1;
            //}

            printf("Testing RINGBUFFER\n");

            int retur = suit_storage_start(storage, manifest, 1024);
            printf("START: %d\n", retur);


            storage_ring_buffer = storage;
            manifest_ring_buffer = manifest;

            uint8_t data[640];
            for (int i = 0; i < 640; i++){
                data[i] = i%256;
            }

            write_ring_buffer(data, 32);
            write_ring_buffer(data, 32);
            write_ring_buffer(data, 64);
            write_ring_buffer(data, 10);
            write_ring_buffer(data, 10);
            write_ring_buffer(data, 10);
            write_ring_buffer(data, 10);
            write_ring_buffer(data, 10);
            write_ring_buffer(data, 10);
            write_ring_buffer(data, 10);
            write_ring_buffer(data, 15);
            write_ring_buffer(data, 43);
            write_ring_buffer(data, 120);


            finish_write_ring_buffer();
            retur = suit_storage_finish(storage, manifest);
            printf("FINISH: %d\n", retur);

            uint32_t img_size;
            _get_component_size(manifest, component, &img_size);
            printf("COMPONENT Size: %ld\n", img_size);

            suit_storage_read(storage, data, 0, 640);
            printf("data from ringBuffer:\n");
            print_bin_data(data, 0, 640);


            printf("Starting decompression!!!!!\n");
            retur = suit_storage_start(storage, manifest, 102400);
            printf("START: %d\n", retur);


            static heatshrink_decoder _decoder;

            heatshrink_decoder_reset(&_decoder);

            uint8_t out_tmp[64];

            size_t n = payload_size;
            uint8_t *inpos = (uint8_t*)payload;
            uint8_t *outpos = out_tmp;

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
                    heatshrink_decoder_poll(&_decoder, outpos, ring_size, &written);
                    write_ring_buffer(outpos, written);
                    written = 0;
                }
                else {
                    while (heatshrink_decoder_finish(&_decoder) == HSDR_FINISH_MORE) {
                        heatshrink_decoder_poll(&_decoder, outpos, ring_size, &written);
                        write_ring_buffer(outpos, written);
                        written = 0;
                    }
                    break;
                }
            }

            finish_write_ring_buffer();
            retur = suit_storage_finish(storage, manifest);
            printf("FINISH: %d\n", retur);


            /* read Decompressed data */
            unsigned int buf_len = 2048;
            uint8_t old_test[buf_len];
            suit_storage_read(storage, old_test, 0, buf_len);
            /* applying magic diff*/
            old_test[0] = magic_pay_diff[0];
            old_test[1] = magic_pay_diff[1];
            old_test[2] = magic_pay_diff[2];
            old_test[3] = magic_pay_diff[3];

            /* print storage data */
            printf("Decompressed data:\n");
            print_bin_data(old_test, 0, buf_len);


            /* patch data with minibsdiff */
            printf("Read header!\n");

            /* Check for appropriate magic */
            if (memcmp(old_test, "MBSDIF43", 8) != 0){
                puts("Error header patch-file!\n");
                return -1;
            }

            /* get newsize */
            size_t ctrllen=offtin(old_test+8);
            size_t datalen=offtin(old_test+16);
            newsize=offtin(old_test+24);
            printf("ctrllen:\n");
            print_u64_dec(ctrllen);
            printf("\n");
            printf("datalen:\n");
            print_u64_dec(datalen);
            printf("\n");
            printf("newsize:\n");
            print_u64_dec(newsize);
            printf("\n");


            /* writing to storage */
            // first suit_storage_start() with newsize
            // second suit_storage_write() with 64 byte Blocks
            // third suit_storage_finish()


            int ret = suit_storage_start(storage, manifest, 1024);
            printf("START: %d\n", ret);

            uint8_t data_[64] = {0};
            ret = suit_storage_write(storage, manifest, data_, 0, 64);
            printf("DATA: %d\n", ret);

            /*
            uint16_t offset = 0;
            for (uint16_t i = 0; i < size_test_write/buffer_size; i++){
                offset = i*buffer_size + overhead_header;
                printf("Offset: %d\n", offset);
                ret = suit_storage_write(storage, manifest, buffer, offset, buffer_size);
                if (ret != SUIT_OK){
                    printf("ERROR WRITE: %d\n", ret);
                }
            }
            */

            ret = suit_storage_finish(storage, manifest);
            printf("FINISH: %d\n", ret);


            /* patch the data */
            oldsize = 1024;
            bspatch((const uint8_t*)old_test, oldsize, storage, oldsize, payload);
            /* print patched data */
            suit_storage_read(storage, old_test, 0, oldsize);
            printf("New data:\n");
            print_bin_data(old_test, 0, oldsize);

            return SUIT_OK;
        }
        else {
            printf("checksum FAILED\n");
            uint8_t buf_[16];
            for (size_t i = 0; i < payload_size; i = i+16){
                suit_storage_read(storage, buf_, i, 16);
                if(memcmp(buf_, &payload[i], 16) != 0){
                    printf("Wrong payload at %d:\n", i);
                    printf("%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x\n",
                        payload[i],payload[i+1],payload[i+2],payload[i+3],payload[i+4],payload[i+5],payload[i+6],payload[i+7],
                        payload[i+8],payload[i+9],payload[i+10],payload[i+11],payload[i+12],payload[i+13],payload[i+14],payload[i+15]);
                    printf("%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x\n",
                        buf_[i],buf_[i+1],buf_[i+2],buf_[i+3],buf_[i+4],buf_[i+5],buf_[i+6],buf_[i+7],
                        buf_[i+8],buf_[i+9],buf_[i+10],buf_[i+11],buf_[i+12],buf_[i+13],buf_[i+14],buf_[i+15]);
                    printf("\n");
                }
            }
            return SUIT_ERR_DIGEST_MISMATCH;
        }
    }
}

static int _dtv_verify_image_match(suit_manifest_t *manifest, int key,
                                   nanocbor_value_t *_it)
{
    (void)key; (void)_it;
    LOG_DEBUG("dtv_image_match\n");
    const uint8_t *digest;
    size_t digest_len;
    suit_component_t *comp = _get_component(manifest);

    uint32_t img_size;
    if (_get_component_size(manifest, comp, &img_size) < 0) {
        return SUIT_ERR_INVALID_MANIFEST;
    }

    /* Only check the component if it is fetched, but not failed */
    if (!suit_component_check_flag(comp, SUIT_COMPONENT_STATE_FETCHED) ||
            suit_component_check_flag(comp,
                                      SUIT_COMPONENT_STATE_FETCH_FAILED)) {
        LOG_ERROR("Fetch failed, or nothing fetched, nothing to check: %u\n",
                  comp->state);
        return SUIT_ERR_INVALID_MANIFEST;
    }

    LOG_INFO("Verifying image digest\n");
    nanocbor_value_t _v;
    if (suit_param_ref_to_cbor(manifest, &comp->param_digest, &_v) == 0) {
        return SUIT_ERR_INVALID_MANIFEST;
    }

    int res = _get_digest(&_v, &digest, &digest_len);

    if (res < 0) {
        LOG_DEBUG("Unable to parse digest structure\n");
        return SUIT_ERR_INVALID_MANIFEST;
    }

    /* TODO: replace with generic verification (not only sha256) */
    LOG_INFO("Starting digest verification against image\n");
    res = _validate_payload(comp, digest, img_size, manifest);
    if (res == SUIT_OK) {
        LOG_INFO("Install correct payload\n");
        suit_storage_install(comp->storage_backend, manifest);
    }
    else {
        LOG_INFO("Erasing bad payload\n");
        if (comp->storage_backend->driver->erase) {
            suit_storage_erase(comp->storage_backend);
        }
    }
    return res;
}

/* begin{code-style-ignore} */
const suit_manifest_handler_t suit_command_sequence_handlers[] = {
    [SUIT_COND_VENDOR_ID]        = _cond_vendor_handler,
    [SUIT_COND_CLASS_ID]         = _cond_class_handler,
    [SUIT_COND_IMAGE_MATCH]      = _dtv_verify_image_match,
    [SUIT_COND_COMPONENT_OFFSET] = _cond_comp_offset,
    [SUIT_DIR_SET_COMPONENT_IDX] = _dtv_set_comp_idx,
    [SUIT_DIR_TRY_EACH]          = _dtv_try_each,
    [SUIT_DIR_SET_PARAM]         = _dtv_set_param,
    [SUIT_DIR_OVERRIDE_PARAM]    = _dtv_set_param,
    [SUIT_DIR_FETCH]             = _dtv_fetch,
    [SUIT_DIR_RUN_SEQUENCE]      = _dtv_run_seq_cond,
};
/* end{code-style-ignore} */

const size_t suit_command_sequence_handlers_len =
        ARRAY_SIZE(suit_command_sequence_handlers);
