BlowPez
=======

Challenge

> Decrypt the flag! The web source has the key
>
> k2KBEayCajXh0hzoxO5Mp3x8kheeopN9

Category: Crypto

Este challenge fue resuelto primero por los chicos de SexyAllPacks y
fernetInjection en tiempo. Yo llegué post cierre del CTF luego de leer el
writeup de `_BrOoDkIlLeR_` y darme cuenta que iba perfecto salvo por dos
problemas, que menciono al final de este writeup. Sólo diré **hay que
prestar atención al código que uno baja de github**.

De cualquier manera, es útil la aproximación.

Por el nombre del challenge hay una alta probabilidad de que se trate de un
ciphertext resultado de aplicar Blowfish a la flag con una clave para la cual
"the web source has the key".

Con esa idea, bajé [crypto_identifier.py](https://github.com/Acceis/crypto_identifier)
y le agregué un parámetro `--keysource` para que, dado un archivo de texto
cualquiera, genere un diccionario de claves en memoria utilizando un clásico
proceso de ventana deslizante.

Vale decir, si un archivo tiene el siguiente texto

    HOLA MUNDO este es un archivo inocuo

vamos tomando fragmentos de longitud 4 y desplazando un byte:

    [HOLA] MUNDO este... --> posible clave "HOLA"
    H[OLA ]MUNDO este... --> posible clave "OLA "
    HO[LA M]UNDO este... --> posible clave "LA M"
       ...
    ...[inoc]uo --> posible clave "inoc"
    ...i[nocu]o --> posible clave "nocu"
    ...in[ocuo] --> posible clave "ocuo"

así hasta el final del archivo, luego repetimos con fragmentos de longitud 5:

    [HOLA ]MUNDO este... --> posible clave "HOLA "
    H[OLA M]UNDO este... --> posible clave "OLA M"
    HO[LA MU]NDO este... --> posible clave "LA MU"

Etcétera. El diccionario resultante, para claves entre 4 y 56 caracteres, sería

    HOLA
    OLA 
    LA M
    A MU
     ...
     ...
    HOLA MUNDO este es un archivo inocuo

Por eficiencia, aproveché los `set()` de python para evitar duplicados
(aunque honestamente no hice profiling para verificar si era más eficiente o no).
Una desventaja de los sets, a diferencia de usar `dict()`, es que el listado
resultante no estará ordenado por longitud de clave sino por el texto de la
clave en sí.

El código es más o menos así:

```python
def sliding_window_set(buffr, keylength):
    # esto se puede optimizar un monton, pero a los fines practicos, funca
    keys = set()
    maxlen = len(buffr) - keylength
    position = 0
    while position < maxlen:
        key = buffr[position:position+keylength]
        # key = key.replace('\n', '')   # opcionalmente, remover newlines
        keys.add(key)
        position += 1
    return keys

def create_keys(filename):
    buffr = open(filename, 'rb').read()
    keys = set()
    for keylength in range(4, 56):
        keys.update(sliding_window_set(buffr, keylength))
    return keys

keys = create_keys('ctf_tasks.html')
```

Las claves obtenidas pueden utilizarse directamente o almacenarse en un .txt
y pasárselas a `crypto_identifier.py` con el parámetro `--keys`, previo
corregir el tema de los saltos de línea (\n). Hay que advertir, sin embargo,
que los archivos son un tanto gorditos, dependiendo del HTML original
(los que obtuve estaban entre los 10 y 100 MB).

Desconocemos el modo de Blowfish utilizado, podemos suponer ECB pues no
requiere IV, pero también podría ser CBC, CBF, OFB, con algún vector de
inicialización particular. El conjunto de IVs posibles que elegí fue

    (None, "\x00" * 8, "ekoparty", "EKOPARTY")

Así que agregué a `crypto_identifier.py` la posibilidad de usar IVs de un set.

Por (des)fortuna, se me ocurrió modificar la rutina que agregué a
`crypto_identifier.py` para que el valor del parámetro `--keysource` pueda
ser una URL, de forma tal que haga GET del recurso y genere el diccionario
de claves al vuelo, a partir del HTML.

Bueno, ahora a qué "web source" se refiere? al sitio web
[The Web Source](http://www.thewebsource.ca/)? al sitio web de la Ekoparty,
al del CTF? A qué página?

La mayor parte de las pruebas las realicé utilizando los HTMLs del sitio web
principal de la Ekoparty; dediqué pocas pruebas al sitio del CTF, y eso en
parte me llevó a no resolverlo en tiempo. Veamos...

La línea de comando utilizada, por ejemplo, era

    $ python3 crypto_identifier.py --input k2KBEayCajXh0hzoxO5Mp3x8kheeopN9 \
        --algo Blowfish --keysource https://eoparty.org/ --printable

En el medio hice varias pruebas esperando si el resultado era "imprimible" o
no, vale decir, si tenía caracteres de control o no. Crypto_identifier hace
sencilla la búsqueda de tales resultados con el parámetro `--printable`.
Por algún motivo,
[eliminaron el parámetro](https://github.com/Acceis/crypto_identifier/commit/e4d7f811b762859b146857a09ede6e61245f49c0)
`--grep` que me hubiera venido perfecto, pero un `| grep EKO` o un
`startswith(b'EKO{')` en python funcionaba igual y de hecho lo usé así durante
un buen rato.

Probé incluso en el sitio web del CTF:

    $ python3 crypto_identifier.py --input k2KBEayCajXh0hzoxO5Mp3x8kheeopN9 \
        --algo Blowfish --keysource https://ctf.eoparty.org/tasks \
        --printable | grep EKO

No les suena raro algo acá?

Al agregar el `--keysource URL` olvidé (inserte aquí un emoji de facepalm)
agregarle las cookies a la petición. Ergo, lo que obtenía era el HTML
deslogueado y no me había dado cuenta. Bah, había realizado algunas pruebas
antes con el HTML dentro del CTF, pero justo no el de `/tasks`. Y cuando probé
esta última ruta, lo hice ya con la "maldita función de descarga que puse".

Cuál es el problema? hay que usar el código fuente del sitio del CTF,
(del que ``_BrOoDkIlLeR_` nos dejó copia [en la variable `$htmlencoded` de su
writeup](https://github.com/estebancano-dev/CTF-Writeups/tree/master/20200626%20Ekoparty%20Pre-CTF/Crypto/BlowPez)).
En ese código HTML, uno de los divs, creo que el que arma la tabla del
Top 5, tiene la clase `table-top10`. Y esa tabla sólo figura en la página
cuando ya se ha iniciado sesión (obviamente!). El HTML que obtuve siempre
fue el del formulario de login (**primer error**).

Pero de todas maneras, había otro problema subyacente, y que dio por tierra
todo el esfuerzo: la versión de `crypto_identifier.py` que utilicé calcula mal
el padding que agrega a las claves. En la función `set_key_length(self, key)`,
por algún motivo anexa un NUL (`\x00`) de más, algo que advertí cuando hice un
script desde cero utilizando pyCryptoDome. Moraleja: **ojo con lo que uno baja
de Internet**, jajaj. A veces es mejor hacer la rutina a mano.

De hecho la que estuvo más cerca de resolverlo fue mi novia, que abrió el
código del CTF con las herramientas del desarrollador de Firefox y fue probando
una a una en Cyberchef varias de las palabras que encontraba en el source.
Lo que se dice, un ataque de diccionario manual, lo suyo.

Anyway, con el archivo correcto (que ustedes deberían bajar de algún lado)
y el script con el padding corregido ([con estos parches](./patches/)):

    $ python3 crypto_identifier.py --input k2KBEayCajXh0hzoxO5Mp3x8kheeopN9 \
        --algo Blowfish --keysource keyfiles/ctf_tasks.html --printable
    Creating keys from keyfiles/ctf_tasks.html ... 324024 unique keys
    Saving new keys into keyfiles/ctf_tasks.html.txt
    BlowfishCipher (ECB) : 'table-top10' : b'EKO{Cust0m_D1ct}'

pero la RPMQLRMP!

Flag

    EKO{Cust0m_D1ct}

Hats off a los que pudieron resolverlo en tiempo y forma.

-- [maurom](https://maurom.com/)
