/**
 * brute-pipe.c
 * a bruteforce code purposely written for the Pipe challenge of the Ekoparty Pre-CTF 2020
 *
 * this was coded in a rush; you've been warned
 */
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/md5.h>
#include <ctype.h>

#define START 0xf7000000      // we should start at 0, but it will take a lot of time
#define BLOCK_SIZE 38

void printhex(unsigned char *str, int n) {
    int i;
    for (i=0; i < n; i++)
        printf("%02x", str[i]);
    printf("   ");
    for (i=0; i < n; i++)
        putchar(isprint(str[i]) ? str[i] : '.');
    putchar(10);
}

int main (int argc, char argv[]) {
    unsigned char cVar1;
    uint uVar2;
    int i;
    unsigned char input[BLOCK_SIZE] = "\xd7\x40\xa5\xdc\x60\x7f\x78\xfb\xff\xe5\x20\xef\xc7\xca\xeb\xd2\x13\x79\x40\xdd\xb2\x6c\x30\xc2\xfd\x37\xed\x74\x3b\x77\x03\x8d\x32\x6a\x9c\x7e\x7e\x80";
    unsigned char output[BLOCK_SIZE];
    unsigned char hash[MD5_DIGEST_LENGTH];
    unsigned char expected_hash[MD5_DIGEST_LENGTH] = "\x08\x0d\x5c\xaa\xed\x95\xaf\x9a\xb0\x72\xc4\x1d\xe3\xa7\x3c\x24";
    uint seed;

    for (seed = START; seed < UINT_MAX; seed++) {
        srand(seed);
        if (!(seed & 0x000fffff)) {
            printf("\r  Seed: 0x%08x (%u)", seed, seed);
            fflush(stdout);
        }
        for (i = 0; i < BLOCK_SIZE; i++) {
            cVar1 = input[i];
            uVar2 = rand();
            output[i] = ((int)cVar1 ^ uVar2 & 0xff);
        }
        MD5(output, BLOCK_SIZE, hash);
        if (!memcmp(hash, expected_hash, MD5_DIGEST_LENGTH)) {
            printf("\rFound matching MD5 with seed 0x%08x (%u)\n", seed, seed);
            printf("Output: %.*s\n", BLOCK_SIZE, output);

            printf(" Input: "); printhex(input, BLOCK_SIZE);
            printf("Output: "); printhex(output, BLOCK_SIZE);
            printf("Target: "); printhex(expected_hash, MD5_DIGEST_LENGTH);
            printf("  Hash: "); printhex(hash, MD5_DIGEST_LENGTH);

            break;
        }
    }
}

