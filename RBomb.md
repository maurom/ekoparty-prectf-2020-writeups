R-Bomb
======

Challenge

> This is a corrupted bomb file, be careful or the disk will fill up!
>
> Attachment
> [R-Bomb](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/R-Bomb?raw=true)

Category: Forensics

Veamos de que se trata

    $ file R-Bomb
    R-Bomb: data
    $ hd R-Bomb | head -6
    00000000  1a 07 01 00 c9 bd e4 fa  10 01 05 0c 00 0b 01 01  |................|
    00000010  bb d2 85 80 80 80 80 80  00 48 35 70 ec 2f 02 03  |.........H5p./..|
    00000020  0b f2 d1 85 80 80 80 00  04 b0 9c 91 b4 86 80 00  |................|
    00000030  a0 10 2d dc 82 3a 80 43  00 08 66 6c 61 67 2e 74  |..-..:.C..flag.t|
    00000040  78 74 0a 03 02 9e e4 d4  b7 7c 51 d6 01 89 be 63  |xt.......|Q....c|
    00000050  0e 33 55 04 02 f8 32 4b  09 83 23 02 4e 41 88 5e  |.3U...2K..#.NA.^|
    $ hd R-Bomb | tail -6
    00016950  51 4f e6 b0 9e 0b 39 00  a6 d2 05 34 48 35 70 ec  |QO....9....4H5p.|
    00016960  2f 02 03 0b f2 d1 85 80  80 80 00 04 b0 9c 91 b4  |/...............|
    00016970  86 80 00 a0 10 2d dc 82  3a 80 43 00 08 66 6c 61  |.....-..:.C..fla|
    00016980  67 2e 74 78 74 0a 03 02  9e e4 d4 b7 7c 51 d6 01  |g.txt.......|Q..|
    00016990  1d 77 56 51 03 05 04 00                           |.wVQ....|
    00016998

Parece una especie de contenedor, filesystem o comprimido, porque aparece un
nombre de archivo `flag.txt` sumamente sugestivo, y aparece tanto en el inicio
como en el final. Algunos formatos de comprimido suelen usar header y trailer,
creo que .zip era uno de ellos (por el tema del cambio de disquettes? qué
épocas aquellas).

Bueno, ahora qué formato será? .zip? .7z? .arj? .cab?

Mi novia sugirió buscar los primeros 4 bytes (`1a0700cf`) en Internet,
y dimos con un francés que explica el uso de cifrado en la descompresión
de zip, rar y 7z:

- USAGE DE LA CRYPTOGRAPHIE PAR LES FORMATS D'ARCHIVES ZIP, RAR ET 7Z  
  <https://connect.ed-diamond.com/MISC/MISC-092/Usage-de-la-cryptographie-par-les-formats-d-archives-ZIP-RAR-et-7z>

Y en su artículo...

    >btype hello_nopw_store.rar
    0x000000:  52617221 1a0700cf 90730000 0d000000    Rar!.....s......
    0x000010:  00000000 02b97420 902e0017 00000017    ......t ........
    0x000020:  00000002 ba83e8ef 73593449 14300900    ........sY4I.0..
    0x000030:  20000000 68656c6c 6f2e7478 7400f03f     ...hello.txt..?

La secuencia `1a0700cf` es la que sigue al magic `Rar!`. Todo pinta que
el R-Bomb es un RAR al cual le falta el header Rar!, y hay que agregárselo
no sobrescribiendo sino concatenando.

Entonces (y ojo, no olviden el `-n` para evitar el salto de línea)

    $ echo -n "Rar!" > header
    $ cat header R-Bomb > r-bomb.rar
    $ file r-bomb.rar
    r-bomb.rar: RAR archive data, v5

Bueno, ya tenemos un rar. Peeeero...

    $ unrar l r-bomb.rar
    Archive: r-bomb.rar
    Details: RAR 5
    
     Attributes      Size     Date    Time   Name
    ----------- ---------  ---------- -----  ----
        .CA.... 1719946800  2020-07-03 17:58  flag.txt
    ----------- ---------  ---------- -----  ----
               1719946800                    1

dentro de este comprimido hay un archivo `flag.txt` enooooorme
(bah, no tan grande, es de 2 gb mas o menos, pero rebalsa la
pobre SSD de mi portátil).

Lo bueno, es que unrar tiene un parámetro `-p` que te permite, en vez de
descomprimir a disco, descomprimir a pantalla por lo que es tan sencillo
como hacer

    $ unrar p r-bomb.rar | head -c 1000
    Extracting from r-bomb.rar
    
    ------ Printing flag.txt
    
      99%EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}
    EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}
    EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}
    EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}
    EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}
    EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}
    EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}EKO{RarrrRRrr!}
      ...

Flag

    EKO{RarrrRRrr!}

-- [maurom](https://maurom.com/)
