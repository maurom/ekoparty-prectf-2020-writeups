Ropfan
======

Challenge

> If you can run this binary, you will have the flag.
>
> Attachment:
> [Ropfan](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Ropfan?raw=true)

Category: Reversing

Como siempre...

    $ file Ropfan
    Ropfan: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked,
    interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.24,
    BuildID[sha1]=9b343d01e7dfb6abc4070b0ed39270996502ff59, stripped

Decompilar Ropfan; leyendo el código, parece utilizar `dlsym()` y pinta
que falla pues utiliza llamadas a funcion mediante hardcoded offsets
desde el inicio de la libc.

La primera llamada a funcion deberia ser `puts` o `fputs`.

La segunda llamada a funcion deberia ser `putc`, `fputc` o `putchar`.

Lo interesante es que hay que encontrar qué versión de libc se utilizó para
compilar (en realidad, hay que encontrar específicamente el archivo de esa
misma librería) y hacer que el ejecutable utilice esa biblioteca.

Veamos que podemos obtener

    $ strings -a Ropfan
    /lib64/ld-linux-x86-64.so.2
    libdl.so.2
    __gmon_start__
    _Jv_RegisterClasses
    dlsym
    libc.so.6
    __stack_chk_fail
    __libc_start_main
    GLIBC_2.2.5
    GLIBC_2.4
    fff.
    l$ L
    t$(L
    |$0H
    __libc_start_main
    Take your flag
    ;*3$"
    GCC: (suxsuxsuxsuxsuxsuxsuxsuxsuxs) 0.0.0
    .shstrtab
    .interp
     ...

Por los strings, parece que fue compilado con alguna versión
vieja de GCC. No es posible saber cual pues la versión que se
indica en el binario está pisada por `suxsuxsux...`

    GCC: (suxsuxsuxsuxsuxsuxsuxsuxsuxs) 0.0.0

Malditos!

Del binario se pueden obtener estos datos:

    offset      funcion
    0x00000     __libc_start_main
    0x4e470     puts o fputs o printf o fprintf
    0x4f080     putchar, putc o fputc

Para obtener el offset de alguna funcion en libc se puede utilizar

    readelf -s libc.so.6 | grep funcion

Por ejemplo, los offsets en la versión de Debian Buster (libc6 2.28-10) son

    $ strings -a  /usr/lib/x86_64-linux-gnu/libc.so.6 | grep 2.28
    GNU C Library (Debian GLIBC 2.28-10) stable release version 2.28.

    $ readelf -s /usr/lib/x86_64-linux-gnu/libc.so.6 | grep putc
       51: 0000000000073360    50 FUNC    GLOBAL DEFAULT   13 putchar_unlocked@@GLIBC_2.2.5
       96: 000000000007a170    42 FUNC    WEAK   DEFAULT   13 putc_unlocked@@GLIBC_2.2.5
      161: 0000000000078160   299 FUNC    GLOBAL DEFAULT   13 _IO_putc@@GLIBC_2.2.5
      363: 000000000007a080    42 FUNC    GLOBAL DEFAULT   13 fputc_unlocked@@GLIBC_2.2.5
      386: 0000000000078160   299 FUNC    WEAK   DEFAULT   13 putc@@GLIBC_2.2.5  <--
      496: 0000000000073260   241 FUNC    GLOBAL DEFAULT   13 putchar@@GLIBC_2.2.5
     1114: 00000000000778b0   299 FUNC    GLOBAL DEFAULT   13 fputc@@GLIBC_2.2.5

    $ readelf -s /usr/lib/x86_64-linux-gnu/libc.so.6 | grep puts
       194: 0000000000071910   413 FUNC    GLOBAL DEFAULT   13 _IO_puts@@GLIBC_2.2.5
       426: 0000000000071910   413 FUNC    WEAK   DEFAULT   13 puts@@GLIBC_2.2.5  <--
       501: 00000000000fdfb0  1240 FUNC    GLOBAL DEFAULT   13 putspent@@GLIBC_2.2.5
       685: 00000000000ffa90   680 FUNC    GLOBAL DEFAULT   13 putsgent@@GLIBC_2.10
      1153: 0000000000070490   338 FUNC    WEAK   DEFAULT   13 fputs@@GLIBC_2.2.5
      1694: 0000000000070490   338 FUNC    GLOBAL DEFAULT   13 _IO_fputs@@GLIBC_2.2.5
      2332: 000000000007a460   151 FUNC    WEAK   DEFAULT   13 fputs_unlocked@@GLIBC_2.2.5

Para buscar la libc correspondiente, se puede utilizar el buscador
<https://libc.blukat.me/>, pero en esta oportunidad se optó por otra estrategia.

Se descargó [libc-database](https://github.com/niklasb/libc-database) para
obtener una base de varias glibc de ubuntu.

    git clone https://github.com/niklasb/libc-database

Ejecutando `./get` se obtienen las bibliotecas de los ubuntus (exceptuando los
mas modernos) y es posible su tabla de símbolos y offsets. Esto popula el
directorio `libc-database/db/` con archivos `.so`, `.symbols` y `.url`

Sabiendo que los offsets relativos a `__libc_start_main` del binario Ropfan son

    0x00000     __libc_start_main
    0x4e470     puts o fputs o printf o fprintf
    0x4f080     putchar, putc o fputc

codifiqué un script en python [relative.py](./code/relative.py) que
para cada archivo en `db/*.symbols` obtiene los offsets de cada función
y luego calcula el offset relativo a `__libc_start_main` en la que se
encuentra cada función de la tabla de símbolos.

A medida que los va calculando, si encuentra alguno que coincide con
`0x4e470` o `0x4f080` imprime el nombre de la función allí ubicada.

Al ejecutar `./relative.py`, se encontró que en el archivo
`libc6_2.15-0ubuntu10.18_amd64.symbols`, en los offsets `0x4e470` y `0x4f080`
se encuentran las siguientes funciones, que son bastante apropiadas para
lo que realizan en el binario.

Se obtuvo el .deb que contiene la libreria libc6 para esa versión desde

   https://launchpad.net/ubuntu/precise/amd64/libc6/2.15-0ubuntu10.18

o bien

   http://us.archive.ubuntu.com/ubuntu/pool/main/e/eglibc/

En particular nos interesa éste:

   http://us.archive.ubuntu.com/ubuntu/pool/main/e/eglibc/libc-bin_2.15-0ubuntu10.18_amd64.deb

Se creó un chroot específico con la biblioteca vieja, el binario y un
busybox estático para actuar como shell (también se puso un gdb estático
por las dudas). Esto está documentado en [test-libc6.sh](./code/test-libc6.sh)

Ahora ingresamos al chroot y ejecutamos el binario

    # /usr/sbin/chroot ./mnt /bin/busybox ash
    $ ./bin/Ropfan
    EKO{LIBC/0lder\th4n^you}

Hubiera sido más fácil instalar Ubuntu Precise Pangolin de 64 bits,
que es la versión de Ubuntu que utiliza esta versión de la librería
libc6, pero bueh.

Nota: el gdb estático lo conseguí en <https://github.com/hugsy/gdb-static>
y el busybox estático se instala en el sistema operativo real mediante
`apt install busybox-static`

Flag

    EKO{LIBC/0lder\th4n^you}


-- [maurom](https://maurom.com/)
