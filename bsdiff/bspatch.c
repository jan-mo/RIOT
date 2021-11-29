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

#include "bspatch.h"

#include "bzlib.h"
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

int64_t counter_patch = 0;

static int64_t offtin(uint8_t *buf)
{
	int64_t y;

	y=buf[7]&0x7F;
	y=y*256;y+=buf[6];
	y=y*256;y+=buf[5];
	y=y*256;y+=buf[4];
	y=y*256;y+=buf[3];
	y=y*256;y+=buf[2];
	y=y*256;y+=buf[1];
	y=y*256;y+=buf[0];

	if(buf[7]&0x80) y=-y;

	return y;
}

int read_buffer(uint8_t* bufin, uint8_t* bufout, int size) {
    printf("counter: %d\n", counter_patch);
    for (int64_t i = 0; i < size; i++){
        bufout[i] = (bufin+counter_patch)[i];
    }
    counter_patch += size;
    return 0;
}

int bspatch(const uint8_t* old, int64_t oldsize, uint8_t* new, int64_t newsize, uint8_t* patch)
{
	uint8_t buf[8];
	int64_t oldpos,newpos;
	int64_t ctrl[3];
	int64_t i;


	oldpos=0;newpos=0;
	while(newpos<newsize) {
		/* Read control data */
        printf("newpos: %d\n", newpos);
        printf("oldpos: %d\n", oldpos);
		for(i=0;i<=2;i++) {
			if (read_buffer(patch, buf, 8))
				return -1;
            printf("buffer: %x %x %x %x %x %x %x %x \n", buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7]);
			ctrl[i]=offtin(buf);
            printf("ctrl %d: ", i);
            printf("%llx ", ctrl[i]);
            printf("\n");
		};

		/* Sanity-check */
		if(newpos+ctrl[0]>newsize){
			printf("Sanity-check\n");
            return -1;
        }

		/* Read diff string */
		if (read_buffer(patch, new + newpos, ctrl[0]))
			return -1;

		/* Add old data to diff string */
		for(i=0;i<ctrl[0];i++)
			if((oldpos+i>=0) && (oldpos+i<oldsize))
				new[newpos+i]+=old[oldpos+i];

		/* Adjust pointers */
		newpos+=ctrl[0];
		oldpos+=ctrl[0];

		/* Sanity-check */
		if(newpos+ctrl[1]>newsize)
			return -1;

		/* Read extra string */
		if (read_buffer(patch, new + newpos, ctrl[1]))
			return -1;

		/* Adjust pointers */
		newpos+=ctrl[1];
		oldpos+=ctrl[2];
	};

	return 0;
}

//#include <bzlib.h>
//#include <err.h>
//#include <unistd.h>
//#include <fcntl.h>

/*static int bz2_read(const struct bspatch_stream* stream, void* buffer, int length)
{
	int n;
	int bz2err;
	BZFILE* bz2;

	bz2 = (BZFILE*)stream->opaque;
	n = BZ2_bzRead(&bz2err, bz2, buffer, length);
	if (n != length)
		return -1;

	printf("Buffer");
	uint8_t* buf = (uint8_t*)buffer;
	for (int i = 1; i <= length; i++) {
		printf("%x", buf[i]);
		if (i%8 == 0)
			printf("\n");
		else if (i%2 == 0)
			printf(" ");
	}

	return 0;
}
*/

int main()
{
    uint8_t header_size = 24;
	FILE * f;
	int fd;
	uint8_t header[header_size];
	int64_t newsize;

	/* Check for appropriate magic */
	if (memcmp(patchfile, "PEAR/BSDIFF43", 13) != 0)
		printf("Corrupt patch\n");

	/* Read lengths from header */
	newsize=offtin(patchfile+13);
	if(newsize<0)
		printf("Corrupt patch\n");

    printf("Newsize: %d\n", newsize);
    if (newsize != Old_Size){
        printf("Sizes not the same!");
        return -1;
    }

    unsigned char dest[newsize+header_size];
    unsigned int destLen = newsize+header_size;
    uint8_t* source = patchfile;
    unsigned int sourceLen = Patch_Size;
    int small = 1;
    int verbosity = 4;


    int err = BZ2_bzBuffToBuffDecompress(dest, &destLen, source + 13 + 8, sourceLen, small, verbosity);
    if (err == BZ_OUTBUFF_FULL)
        printf("Buffer Full\n");

    if (err == -5){
        printf("return: %d\n", err);
        printf("BAD MAGIC\n");
        return 0;
    }
    if (err != BZ_OK){
        printf("return: %d\n", err);
        return 0;
    }

    /* do patch process */
    uint8_t new_file[newsize];
    int error = bspatch(oldfile, Old_Size, new_file, newsize, dest);
    if (error != 0){
        printf("error\n");
        return -1;
    }

    /* save output to file */
    FILE* fp;
    fp = fopen("test_final.bin", "wb");
    /* write to file */
    fwrite(new_file, newsize, 1, fp);
    fclose(fp);
    printf("\nwrote to FILE!\n");

	return 0;
}
