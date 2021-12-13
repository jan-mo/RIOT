/*-
 * Copyright 2003-2005 Colin Percival
 * Copyright 2012 Matthew Endsley
 * All rights reserved
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted providing that the following conditions 
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
 * IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <limits.h>
#include <stdio.h>
#include "suit/bspatch.h"

#include "fmt.h"

#include "suit/storage.h"

int64_t counter_patch = 0;

int read_buffer(uint8_t* bufin, uint8_t* bufout, int64_t size) {
    printf("counter: \n");
    print_u64_dec(counter_patch);
    printf("\n");
    for (int64_t i = 0; i < size; i++){
        bufout[i] = (bufin+counter_patch)[i];
    }
    counter_patch += size;
    return 0;
}

int write_storage(uint8_t* bufin, suit_storage_t* storage, int64_t offset, int64_t size)
{
    const uint8_t* buffer = bufin;
    suit_storage_write(storage, NULL, buffer, (size_t)offset, (size_t)size);
    return 0;
}

void read_storage(suit_storage_t* storage, uint8_t* bufout, int64_t offset, int64_t size)
{
    suit_storage_read(storage, bufout, offset, size);
}

int bspatch(const uint8_t* old, int64_t oldsize, suit_storage_t* new, int64_t newsize, uint8_t* payload)
{
    uint8_t buf[8];
    int64_t oldpos,newpos;
    int64_t ctrl[3];
    int64_t i;

    oldpos=0;newpos=0;
    while(newpos<newsize) {
        /* Read control data */
        for(i=0;i<=2;i++) {
            if (read_buffer(payload, buf, 8))
                return -1;
            ctrl[i]=offtin(buf);
        };

        /* Sanity-check */
        if (ctrl[0]<0 || ctrl[0]>INT_MAX ||
            ctrl[1]<0 || ctrl[1]>INT_MAX ||
            newpos+ctrl[0]>newsize)
            return -1;

        /* Read diff string */
        if (write_storage(payload, new, newpos, ctrl[0])){
            return -1;
        }
        printf("write at ");
        print_u64_dec(counter_patch);
        printf("\n");

        /* Add old data to diff string */
        uint8_t tmp;
        uint8_t i = 0;
        for(i=0;i<ctrl[0];i++)
            if((oldpos+i>=0) && (oldpos+i<oldsize)) {
                read_storage(new, &tmp, newpos+1, 1);
                tmp += old[oldpos+1];
                write_storage(&tmp, new, newpos+1, 1);
                if (i < 10){
                    printf("write at ");
                    print_u64_dec(counter_patch);
                    printf("\n");
                }
                i++;
                //new[newpos+i]+=old[oldpos+i];
            }

        /* Adjust pointers */
        newpos+=ctrl[0];
        oldpos+=ctrl[0];

        /* Sanity-check */
        if(newpos+ctrl[1]>newsize)
            return -1;

        /* Read extra string */
        if (write_storage(payload, new, newpos, ctrl[1])){
            return -1;
        }
        printf("write at ");
        print_u64_dec(counter_patch);
        printf("\n");

        /* Adjust pointers */
        newpos+=ctrl[1];
        oldpos+=ctrl[2];
    };

    return 0;
}
