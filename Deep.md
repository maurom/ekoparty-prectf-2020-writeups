Deep
====

Challenge

> Where is the flag?
>
> Attachment
> [Deep](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Deep?raw=true)

Category: Misc

File nos dice que es una imagen

    $ file Deep
    Deep: JPEG image data, JFIF standard 1.01, resolution (DPI), density 96x96,
    segment length 16, baseline, precision 8, 875x471, components 3

Que básicamente es una foto de alguna Ekoparty pasada con varios dígitos
binarios superpuestos en la esquina inferior derecha.

Usando Cyberchef, pasamos los digitos binarios a ASCII, obteniendo `Hi_Baby`.

Como esta mano viene de esteganografía, probamos varias alternativas, entre
ellas `steghide`. La primera fue probarlo con la clave `Hi_Baby`, pero no hubo
suerte:

    $ LANG=C steghide extract -sf Deep
    Enter passphrase: Hi_Baby
    steghide: could not extract any data with that passphrase!

Podría haber seguido un rato más, pero a mi novia se le ocurrió que no era
necesario que tuviera password, o que podía estar en blanco (yo ni idea de que
se podía). En cualquier caso, la idea es dar Enter luego del prompt, y listo:

    $ LANG=C steghide extract -sf Deep.jpg
    Enter passphrase: (ninguno)
    wrote extracted data to "flag.enc".
    $ file flag.enc
    $ head -3 flag.enc
    /9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcG
    BwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwM
    DAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCADTAPcDASIA

Pinta ser un base64

    $ base64 -d flag.enc > base64decoded
    $ file base64decoded
    base64decoded: JPEG image data, JFIF standard 1.01, resolution (DPI), density
    96x96, segment length 16, baseline, precision 8, 247x211, components 3

Obteniendo algo que parece ser una imagen, que nos arenga diciendo "WTF?".
Eso mismo: WTF, chango!

Veamos si hay algo más, y esta vez sí utilizamos el `Hi_Baby` del comienzo

    $ LANG=C steghide extract -sf base64decoded
    Enter passphrase: Hi_Baby
    wrote extracted data to "flag.txt".
    $ cat flag.txt
    EKO{H1DD3N^2}

Es decir, hidden * hidden

    EKO{H1DD3N^2}

-- [maurom](https://maurom.com/)
