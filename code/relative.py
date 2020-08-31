#!/usr/bin/python3

from glob import glob
from os.path import basename
from sys import argv


def findrel(symbols_filename):
    offsets = {}
    functions = {}
    with open(symbols_filename, 'r') as fh:
        for line in fh:
            function, offset_str = line.strip().split(' ')
            offset_dec = int(offset_str, 16)
            if function in offsets:
                pass  # print('Redefined offset for %s: %s' % (function, offset_str))
            else:
                offsets[function] = offset_dec
            if offset_dec in functions:
                functions[offset_dec].append(function)
            else:
                functions[offset_dec] = [function]
    base = offsets['__libc_start_main']
    buscadas = ('__libc_start_main', 'putc', 'puts', 'putchar', 'printf')
    # 0x4e470     puts o fputs o printf o fprintf
    # 0x4f080     putchar, putc o fputc
    print(basename(symbols_filename))
    # este bucle es mas conveniente pues muestra las funciones que estan en esos offsets
    for f in offsets:
        relative = hex(offsets[f] - base)
        if relative in ('0x4e470', '0x4f080'):
            print(f, relative)


#libc6_2.15-0ubuntu10.18_amd64.symbols <---
#_IO_puts 0x4e470
#puts 0x4e470
#putchar 0x4f080

if __name__ == '__main__':
    dbfolder = '/tmp/libc-database/db'
    dbfolder = 'libc6'
    for fname in glob(dbfolder + '/*.symbols'):
        findrel(fname)
