Anon
====

Challenge

> This group es too paranoid
>
> http://paste.ubuntu.com/p/HnGHwGk4rQ/

Category: Misc

Indeed, muy paranoicos.

Son un montón de pastebins enlazados unos con otros formando un árbol, y
básicamente hay que hacer un crawler que recorra los links a medida que van
apareciendo a partir del primero:

    http://paste.ubuntu.com/p/HnGHwGk4rQ/

Algunos de los enlaces dan 404, otros tienen más enlaces.

Codeando rápidamente un crawler, adjunto en [anon-crawl.py](./code/anon-crawl.py),
se obtuvieron todos los archivos correspondientes al contenido de cada enlace.

    $ mkdir cache
    $ python3 anon-crawl.py
    Visitados:
    Pendientes:
        http://paste.ubuntu.com/p/HnGHwGk4rQ/
    Obteniendo  http://paste.ubuntu.com/p/HnGHwGk4rQ/
    Match: [...]
    Visitados:
        http://paste.ubuntu.com/p/HnGHwGk4rQ/
    Pendientes:
        http://paste.ubuntu.com/p/DO8r2xL0oD/
        http://paste.ubuntu.com/p/KzO5PgXYsE/
        http://paste.ubuntu.com/p/KpD0XPSZ0s/
    ...

Va a demorar un buen rato.

Una vez que termine, si hacemos un listado del caché vemos que hay un
archivo de longitud distinta del resto:

    $ ls -lSr ./cache/
    total 2000
    -rw-r--r-- 1 user user  745 ago 27 22:30 ZzyU5h6yg3
    -rw-r--r-- 1 user user  745 ago 27 22:32 ztpHSTOxpe
    -rw-r--r-- 1 user user  745 ago 27 22:30 ZSJyLg6VkD
       ...
    -rw-r--r-- 1 user user 1276 ago 27 22:31 3txh6ZzMpb
    -rw-r--r-- 1 user user 1276 ago 27 22:32 34CZm7RNHg
    -rw-r--r-- 1 user user 1307 ago 27 22:32 j7XwD37y8H

Este último archivo, que corresponde al contenido del pastebin
<http://paste.ubuntu.com/p/j7XwD37y8H/>, posee además de los enlaces,
la siguiente cadena en base64:

Contenido de j7XwD37y8H

    http://paste.ubuntu.com/p/p804DB7ddO/
     http://paste.ubuntu.com/p/ifWqPPi1X3/
     http://paste.ubuntu.com/p/jdLgsdjsmg/
     http://paste.ubuntu.com/p/PXkacdF2Bc/
     UlV0UGUzQmhjM1JsY0dGemRHVndZWE4wWlM0dUxuQmhjM1JsTGk0dWMzVjRmUT09Cg==

Por lo que decodificamos la cadena dos veces seguidas para obtener la flag

    $ python3
    >>> base64.b64decode('UlV0UGUzQmhjM1JsY0dGemRHVndZWE4wWlM0dUxuQmhjM1JsTGk0dWMzVjRmUT09Cg==')
    b'RUtPe3Bhc3RlcGFzdGVwYXN0ZS4uLnBhc3RlLi4uc3V4fQ==\n'
    >>> base64.b64decode(b'RUtPe3Bhc3RlcGFzdGVwYXN0ZS4uLnBhc3RlLi4uc3V4fQ==\n')
    b'EKO{pastepastepaste...paste...sux}'

Flag

    EKO{pastepastepaste...paste...sux}

-- [maurom](https://maurom.com/)
