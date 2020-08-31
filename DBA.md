DBA
===

Challenge

> A DBA dumped his old disk
>
> FLAG format: EKO{upper(text)}
>
> Attachment
> [Data](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/DBA?raw=true)

Category: Forensics

Con `file` nos damos cuenta de que DBA es un gzip

    $ gunzip < DBA > salida
    $ file salida
    salida: Linux rev 1.0 ext4 filesystem data, UUID=bd360c21-014e-4f4a-ad8b-
    ed1be266de0e (extents) (large files) (huge files)

Otro filesystem (como en el caso de 2Much), pero esta vez es ext4

    $ mv salida dba.img
    $ mkdir temp
    $ mount dba.img -o ro,loop temp
    $ ls temp/
    dba.dmp  lost+found

Dos archivos... sólo eso? Nope, hay algo más

    $ ls temp/ -a
    .  ..  .mysql_history  dba.dmp	lost+found

Obvio que revisamos los atributos extendidos como en 2Much, y buscamos
archivos borrados con `extundelete`, `ext3grep`, `ext4magic` y hasta
`foremost`, pero no había mucho más.

    $ cd temp
    $ head dba.dmp
    -- MySQL dump 10.13  Distrib 5.7.31, for Linux (x86_64)
    --
    -- Host: localhost    Database: dba
    -- ------------------------------------------------------
    -- Server version	5.7.31-0ubuntu0.16.04.1
    
    /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
    /*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
     ...
    --
    -- Dumping data for table `data`
    --
    
    LOCK TABLES `data` WRITE;
    /*!40000 ALTER TABLE `data` DISABLE KEYS */;
    INSERT INTO `data` VALUES (2,_binary 'Y...

El archivo `dba.sql` es tal cual su extensión, un dump de una base MySQL
con una sola tabla, y una sola fila con dos columnas: un id entero y un
BLOB enorme.

El archivo `.mysql_history` contiene, tal cual su nombre, el listado de
los últimos comandos ejecutados por el DBA en el cliente mysql

    $ head .mysql_history
    SELECT DECRYPT(usermame, '8YtNukU9ceaqs') from users;
    SELECT DECRYPT(usermame, 'jvXl1yK98Cgbf') from users;
    SELECT DECRYPT(usermame, 'IPENSdHqzssTZ') from users;
    SELECT DECRYPT(usermame, 'yxh2syOv9T6qy') from users;
    SELECT DECRYPT from users;
    SELECT DECRYPT(usermame, 'G3KDRCGp4Ch4o') from users;
    SELECT DECRYPT(usermame, 'cYViPMEIflaWy') from users;
    SELECT DECRYPT(usermame, '1r1jomBXIvnCw') from users;
    DELETE FROM users WHERE id=30768;
    SELECT DECRYPT(usermame, '64pgdAIR0wlQB') from users;

Bueno, comencemos por el dump de base de datos. Instalar mysql / mariadb,
crear una tabla vacía que aloje los valores, luego recuperar los registros
y renombrar la tabla a `users` para que coincida con los SELECTs del
archivo de historia:

    $ mysql
    > create database eko;
    > create table data (id integer, usermame longblob);
    > load dba.sql
    > alter table data set name users;

Nótese la estructura de la tabla: (id, usermame), para hacer coincidir
también la columna referida en los SELECTs del archivo de historia.

Buscamos por todos lados la función DECRYPT, pero nunca fue implementada
en MySQL. Hay ENCRYPT(), que es una función obsoleta que aplica la función
de Unix crypt(), pero no hay decrypt().

Mi novia tenía la corazonada de que DECRYPT() es en realidad AES_DECRYPT(),
y bueno, por qué no probar.

Básicamente, tomar cada línea del archivo de historia y donde diga
DECRYPT, reemplazarlo por AES_DECRYPT y probar las distintas claves
hasta que algo dé resultado.

Codeamos un breve script en python que lee todo el `.mysql_history` buscando
cadenas con el formato

    SELECT id, AES_DECRYPT(usermame, CLAVE)

luego extrae cada clave, prueba descifrar con ella lo que está en el único
registro de la tabla `users` y genera un archivo con el nombre de la
clave y la extensión `.raw` por cada decodificación exitosa. Algo así:

```python
#!/usr/bin/env python3

import pymysql

# conectar a la base local que aloja la unica tabla con el unico registro
conn = pymysql.connect(host="localhost", port=3306, user="eko", passwd="ekoparty", db="eko")
cursor = conn.cursor()
with open('.mysql_history', 'r') as fh:
    function = 'AES_DECRYPT'   # puede ser AES_DECRYPT o bien DES_DECRYPT
    for i, line in enumerate(fh):
        if line.startswith('SELECT DECRYPT(usermame'):
            key = line.split("'")[1]
            # nevermind the sql injection; this is running on a disposable machine
            # and i'm too lazy to use prep stmts at this time
            sql = "SELECT id, %s(usermame, '%s') FROM users;" % (function, key)
            cursor.execute(sql)
            uid, decrypted = cursor.fetchall()[0]
            if decrypted is not None:
                print(i, key, uid, len(decrypted), decrypted[:10])
                with open('%s.raw' % key, 'wb') as outfh:
                    outfh.write(decrypted)
conn.close()
```

Son muchos archivos, y muchos megas de datos.

Como no sabíamos qué podía haber, recurrimos al viejo y querido file,
quitando todo lo desconocido (`.raw: data`) y quedándonos con el resto:

    $ file *.raw | grep -v ".raw: data" | sort -k2
    ZuuP2X0ohaNu8.raw: apollo a88k COFF executable not stripped - version 8349
    Odv00ZCjNlK9k.raw: ARC archive data, uncompressed
    8SWlYBgjqZ7Dh.raw: ASCII text, with very long lines, with no line terminators
    DDt4KWUASBnAA.raw: basic-16 executable
    A2PBOMxEhtOjM.raw: COM executable for DOS
    AOCtvpjn2MRDx.raw: COM executable for DOS
    c33Lo8QhEByqU.raw: COM executable for DOS
    cuGIrWWxHFJtP.raw: COM executable for DOS
    DnuIlL59kjrPt.raw: COM executable for DOS
    F7Pgh3WOa9n9l.raw: COM executable for DOS
     ...

Todo basura, salvo esto que suena raro:

    8SWlYBgjqZ7Dh.raw: ASCII text, with very long lines, with no line terminators

Descifrar AES con una clave ASCII y que devuelva ASCII es MUY raro.

    $ hd -n 128 8SWlYBgjqZ7Dh.raw
    00000000  35 32 34 39 34 36 34 36  37 30 30 32 30 32 30 30  |5249464670020200|
    00000010  35 37 34 31 35 36 34 35  36 36 36 44 37 34 32 30  |57415645666D7420|
    00000020  31 30 30 30 30 30 30 30  30 31 30 30 30 31 30 30  |1000000001000100|
    00000030  32 41 32 42 30 30 30 30  32 41 32 42 30 30 30 30  |2A2B00002A2B0000|
    00000040  30 31 30 30 30 38 30 30  36 34 36 31 37 34 36 31  |0100080064617461|
    00000050  35 30 30 32 30 32 30 30  38 30 38 31 38 35 38 38  |5002020080818588|
    00000060  38 42 38 44 38 43 38 38  38 31 37 38 36 46 36 35  |8B8D8C8881786F65|
    00000070  35 45 35 41 35 41 35 46  36 41 37 39 38 41 39 43  |5E5A5A5F6A798A9C|
     ...

Los bytes de `8SWlYBgjqZ7Dh.raw` son todos números hexadecimales.
Pasando los primeros cuatro (`52 49 46 46`) a ASCII obtenemos algo sumamente
familiar: `RIFF`; para los que hemos lidiado con archivos de video/audio,
el contenedor RIFF es uno de los más clásicos para audio.

Así que hay que convertir todos los hexa del archivo a bytes, con cyberchef
o a manopla:

```python
with open('8SWlYBgjqZ7Dh.raw', 'r') as fh:
    hexstring = fh.read()
with open('riff.wav', 'wb') as fh:
    fh.write(bytes.fromhex(hexstring))
```

    $ file riff.wav
    riff.wav: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 8 bit, mono 11050 Hz
    $ aplay riff.wav

Y morse otra vez (que tiempo atrás fui radioaficionado, hombre!)

Ahora a decodificarlo. Usamos la página Morse Code Adaptive Audio Decoder  
<https://morsecode.world/international/decoder/audio-decoder-adaptive.html>

que gloriosamente acepta un .wav, y todo el audio es `"M111SQLBL000B"`

La flag, en el formato solicitado: EKO{upper(text)}

    EKO{M111SQLBL000B}

-- [maurom](https://maurom.com/)
