Rick
====

Challenge

> Never gonna give you up, never gonna let you down ♪♫♫
>
> Attachment
> Archivo: [Rick.gif](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Rick.gif?raw=true)

Category: Misc

Buscamos por un montón de posibilidades. Y cuando digo un montón, es
UN MONTÓN. Hasta armé un visor de estructura GIF [gifexam.py](./code/gifexam.py)
por si había bytes entre los bytes reservados de la estructura, pero
por más que le di vueltas, no encontré nada.

Una posible alternativa era se utilizaran los colores duplicados
en la paleta. Armamos 1 gif animado por cada indice de color y nada.

Luego buscamos herramientas de esteganografía para gif y encontramos
varias pero ninguna funcionaba, así que seguimos probando con la
herramienta casera, sin éxito.

Volvimos a la red, a ver si había alguna otra alternativa.
Una posibilidad que veíamos viable fue esta:

    https://github.com/raffg/steganography

por lo que seguimos por esa vía.

Al final caímos en la página de la herramienta
[gifshuffle](http://www.darkside.com.au/gifshuffle/)

La bajamos, compilamos y, maravillosamente, funcionó.

Gifshuffle aplica una forma MUY interesante de esteganografía,
ya que no añade ningún bit al archivo. Lo que hace es codificar la
información a ocultar en el orden (efectivamente, define el orden)
de la paleta de colores de la animación (la global, creo), y luego
ajusta los índices de los píxeles en los frames de la animación
para que coincidan con los colores anteriores.

De esta forma, el orden de la paleta no afecta en lo más mínimo a
la animación (no se pierde información, no le quita calidad), es
prácticamente indistinguible de un archivo gif común (salvo, por
supuesto, que uno posea el .gif original, que yo intenté buscar
por todos lados y no encontré). Me quedo pensando si no provee
incluso plausible deniability.

En cualquier caso, lo gracioso es que la herramienta estaba en
Debian y yo no la había encontrado. Todo hubiera sido más sencillo

    # apt install gifshuffle

    $ gifshuffle Rick.gif
    EKO{R1ck_rollll3d}

la próxima, estimado lector, haga lo siguiente antes de buscar
en Internet:

    $ aptitude search "~dstega"
    i   gifshuffle     - Steganography program to gif images
    p   mat2           - Metadata anonymisation toolkit v2
    p   outguess       - universal steganographic tool
    p   python-stepic  - Python Steganography in Images
    p   samhain        - Sistema de alerta de intrusiones e integridad de datos
    p   snowdrop       - plain text watermarking and watermark recovery
    i   steghide       - steganography hiding tool
    p   steghide-doc   - steganography hiding tool - documentation files
    i   stegosuite     - steganography tool to hide information in image files
    p   stegsnow       - steganography using ASCII files
    p   stepic         - Python 3 Steganography in Images

Flag

    EKO{R1ck_rollll3d}

-- [maurom](https://maurom.com/)

---

Otras cosas que no funcionaron:

- https://en.wikipedia.org/wiki/Steganography_tools
- https://towardsdatascience.com/steganography-how-spies-rickroll-each-other-6a831d7df39e
- https://www.boiteaklou.fr/Basic-Steganography-Vous-navez-pas-les-bases-NDH16.html
- http://users.skynet.be/glu/sgpo.htm
- github.com stegpy
- github.com stegoveritas
- Message hiding in animated GIF using multibit assignment method  
  <https://www.researchgate.net/publication/315914996_Message_hiding_in_animated_GIF_using_multibit_assignment_method>
- https://github.com/vipyne/giffy
- https://github.com/ctfs/write-ups-2014/tree/master/plaid-ctf-2014/doge-stege
