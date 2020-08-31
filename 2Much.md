2Much
=====

Challenge

> Can you recover the flag?
>
> Archivo: [2Much](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/2Much?raw=true)

Category: Forensics

Primero lo primero

    $ file 2Much
    2Much: gzip compressed data, was "for0.img", last modified: Thu Jun 25 02:45:23 2020, from Unix, original size 20971520
    $ gunzip < 2Much > for0.img
    $ file for0.img
    gunzipped: SGI XFS filesystem data (blksz 4096, inosz 256, v2 dirs)

En este caso, se trata de un archivo comprimido, que dentro contiene
una imagen de filesystem XFS.

Montamos la imagen

    # mkdir test
    # mount -o loop,ro filesystem test

    $ cd test
    $ ls -l | head
    total 4000
    -rw-r--r-- 1 root root 16 ago  1  2016 data.1
    -rw-r--r-- 1 root root 16 ago  1  2016 data.10
    -rw-r--r-- 1 root root 16 ago  1  2016 data.100
        ...
    -rw-r--r-- 1 root root 16 ago  1  2016 data.997
    -rw-r--r-- 1 root root 16 ago  1  2016 data.998
    -rw-r--r-- 1 root root 16 ago  1  2016 data.999

Son 1000 archivos, de 16 bytes cada uno, que van del 1 al 1000

    $ cat data.1
    ZH8Em5WVmpYfl53B
    $ cat data.999
    uhTsV5IzcKM5oHSV

Probé buscar por archivos borrados y demás, pero no hubo éxito.

Con frecuencia, si hay un filesystem involucrado, es porque hay que
analizar tanto los archivos internos, como también los metadatos o el
contenido propio del filesystem, tal como los archivos borrados, etc.
Si lo importante fueran los archivos, habrían mandado un .tar.gz o un zip.

Suele suceder, por ejemplo con NTFS, que se encuentran datos interesantes.
Usemos, para XFS, la utilidad `attr`:

    # apt install attr

    $ find . -exec attr -l "{}" \;
    Attribute "f" has a 1 byte value for ./data.5
    Attribute "f" has a 1 byte value for ./data.21
    Attribute "f" has a 1 byte value for ./data.30
     ...
    Attribute "f" has a 1 byte value for ./data.896
    Attribute "f" has a 1 byte value for ./data.907
    Attribute "f" has a 1 byte value for ./data.959

Interesante! Algunos de los archivos tienen un atributo `"f"` y otros
(los que no aparecen en el listado) no tienen ningún atributo.
Aquellos que tienen datos, es sólo un byte.

Veamos qué hay en el atributo extendido `"f"`

    $ find . -exec attr -g f "{}" \; 2> /dev/null
    Attribute "f" had a 1 byte value for ./data.5:
    R
    Attribute "f" had a 1 byte value for ./data.21:
    U
    Attribute "f" had a 1 byte value for ./data.30:
    t
     ...
    Attribute "f" had a 1 byte value for ./data.907:
    0
    Attribute "f" had a 1 byte value for ./data.959:
    =

El signo `=` al final del texto ya debería sonarnos conocido,
al igual que el los primeros bytes `RUt`.

Ya que el nombre de la imagen es `for0.img`, usemos `for` para
concatenar todos los bytes

    $ for I in `seq 1 1000`; do attr -q -g f data.$I; done 2> /dev/null
    RUtPe0RvX3lvdV9jaGVja19leHRlbmRlZF9hdHRyaWJ1dGVzP30=

O bien, para concatenar y guardarlos, `find` y `tee`

    $ find . -exec attr -q -g f "{}" \; 2> /dev/null  |  tee ../salida.txt
    RUtPe0RvX3lvdV9jaGVja19leHRlbmRlZF9hdHRyaWJ1dGVzP30=

Listo, sólo queda

    base64 -d ../salida.txt

Flag

    EKO{Do_you_check_extended_attributes?}

PD: siempre monten filesystems desconocidos en una máquina virtual;
tiempo atrás los parsers de headers de sistemas de archivos eran
un queso gruyere.

-- [maurom](https://maurom.com/)
