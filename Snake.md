Snake
=====

Challenge

> Ouch!, I lost my source code!
>
> Attachment
> [Snake](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Snake?raw=true)

Category: Reversing

Comenzamos

    $ file Snake
    Snake: data

no dice mucho

    $ strings -a Snake
    uf-_
    snake.py
    <listcomp>
    byte_xor.<locals>.<listcomp>)
    bytes
    zip)
    ba1Z
    ba2r
    byte_xor
    ZQSw)
    path
    basename
    __file__
    open
    read
    cflag
    printr
    <module>

Suena conocido, no?

    $ hd Snake
    00000000  55 0d 0d 0a 00 00 00 00  75 66 2d 5f 12 01 00 00  |U.......uf-_....|
    00000010  e3 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000020  00 04 00 00 00 40 00 00  00 73 40 00 00 00 64 00  |.....@...s@...d.|
    ...
    000000f0  2e 30 5a 02 5f 61 5a 02  5f 62 72 02 00 00 00 72  |.0Z._aZ._br....r|
    00000100  02 00 00 00 fa 08 73 6e  61 6b 65 2e 70 79 da 0a  |......snake.py..|
    00000110  3c 6c 69 73 74 63 6f 6d  70 3e 06 00 00 00 73 04  |<listcomp>....s.|
    00000120  00 00 00 06 00 06 00 7a  1c 62 79 74 65 5f 78 6f  |.......z.byte_xo|
    00000130  72 2e 3c 6c 6f 63 61 6c  73 3e 2e 3c 6c 69 73 74  |r.<locals>.<list|
    00000140  63 6f 6d 70 3e 29 02 da  05 62 79 74 65 73 da 03  |comp>)...bytes..|
    00000150  7a 69 70 29 02 5a 03 62  61 31 5a 03 62 61 32 72  |zip).Z.ba1Z.ba2r|
    00000160  02 00 00 00 72 02 00 00  00 72 04 00 00 00 da 08  |....r....r......|
    00000170  62 79 74 65 5f 78 6f 72  05 00 00 00 73 02 00 00  |byte_xor....s...|
    00000180  00 00 01 72 08 00 00 00  da 02 72 62 73 18 00 00  |...r......rbs...|
    00000190  00 66 6a 60 0e 01 41 59  51 1b 1d 1c 08 5d 29 54  |.fj`..AYQ....])T|
    000001a0  18 48 07 37 0d 5a 51 53  77 29 0b da 02 6f 73 72  |.H.7.ZQSw)...osr|
    000001b0  08 00 00 00 da 04 70 61  74 68 da 08 62 61 73 65  |......path..base|
    000001c0  6e 61 6d 65 da 08 5f 5f  66 69 6c 65 5f 5f da 02  |name..__file__..|
    000001d0  66 6e da 04 6f 70 65 6e  da 04 72 65 61 64 da 01  |fn..open..read..|
    000001e0  6b 5a 05 63 66 6c 61 67  da 05 70 72 69 6e 74 72  |kZ.cflag..printr|
    000001f0  02 00 00 00 72 02 00 00  00 72 02 00 00 00 72 04  |....r....r....r.|
    00000200  00 00 00 da 08 3c 6d 6f  64 75 6c 65 3e 03 00 00  |.....<module>...|
    00000210  00 73 0a 00 00 00 08 02  08 03 0c 02 0e 02 04 02  |.s..............|

Totalmente. Es un [.pyc](https://tutorial.python.org.ar/en/latest/modules.html#archivos-compilados-de-python).
Reniego mucho con los .pyc; me molestan mal.

Bueno, es posible ir .pyc a .py; veamos cómo. Buscamos en google
`decompyle python pyc` y nos lleva al paquete
[uncompyle6](https://pypi.org/project/uncompyle6/) que es un
_Python cross-version byte-code decompiler_. Perfecto!

    $ pip3 install uncompyle6
    $ uncompyle6 Snake
    # no luck
    $ cp Snake Snake.pyc
    $ uncompyle6 Snake.pyc

Obtenemos

```python
# uncompyle6 version 3.7.3
# Python bytecode 3.8 (3413)
# Decompiled from: Python 3.7.3 (default, Jul 25 2020, 13:03:44) 
# [GCC 8.3.0]
# Embedded file name: snake.py
# Compiled at: 2020-08-07 11:34:29
# Size of source mod 2**32: 274 bytes
import os

def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])


fn = os.path.basename(__file__)
print(fn)
fn = os.path.basename('Snake')
k = open(fn, 'rb').read()
cflag = b'fj`\x0e\x01AYQ\x1b\x1d\x1c\x08])T\x18H\x077\rZQSw'
print(k)
print(cflag)
print(byte_xor(cflag, k))
# okay decompiling Snake.pyc
```

Ahá. Básicamente hace XOR de

    b'fj`\x0e\x01AYQ\x1b\x1d\x1c\x08])T\x18H\x077\rZQSw'

contra los primeros bytes del mismo archivo fuente.

Entonces

    $ uncompyle6 Snake.pyc > uncompyled.py
    $ python3 uncompyled.py
    b'EJ\x15`b.4!bqy>}_1j;nXczb}@'

Mmm... no, claro, el fuente que obtuvimos decompilado no es
necesariamente el mismo fuente que se compiló, por supuesto.
El código original probablemente no arranca con los
comentarios iniciales. Probemos removiendo los comentarios y
dejando sólo `import os`?

    $ sed '/^#/d' uncompyled.py > 5mments.py
    $ python3 uncompyled.py
    b'\x0f\x07\x10as5y>h\x17\x16l8Otz1sRR">!_'

Nope, tampoco.

Pero qué es lo clásico que se pone en los archivos .py?
el shebang! (con env, of course)

    #!/usr/bin/env python3

    import os
    ...

    $ python3 uncompyled.py
    b'EKO{r3v3rs3m3_th1s_b4bY}'

Por otro lado, mi novia ya había arrancado haciendo la inversa,
es decir, hacer

    b'fj`\x0e\x01AYQ\x1b\x1d\x1c\x08])T\x18H\x077\rZQSw' XOR b'EKO{'

y ya estaba llegando a b'#!/u', así que era cuestión de tiempo.

Flag

    EKO{r3v3rs3m3_th1s_b4bY}

-- [maurom](https://maurom.com/)

