Pipe
====

Challenge

> My secrets are safe after running this tool:
>
> cat secrets.txt | ./Pipe
> d740a5dc607f78fbffe520efc7caebd2137940ddb26c30c2fd37ed743b77038d326a9c7e7e80
>
> You could need this:
> MD5(secrets.txt)=080d5caaed95af9ab072c41de3a73c24
>
> Attachment
> [Pipe](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Pipe?raw=true)

Category: Reversing

Comenzamos

    $ file Pipe
    Pipe: ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV),
    dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.24,
    BuildID[sha1]=cd439ea515ecfbb1280cfacd93e0703ed9c4d38c, not stripped

Decompilando el binario con GHIDRA obtenemos esta función main() (o algo así)

```c
void main(void) {
  char cVar1;
  uint uVar2;
  undefined4 uVar3;
  int in_GS_OFFSET;
  int local_98;
  char local_94 [128];

  srand((uint)main);
  fgets(local_94,0x80,stdin);
  local_98 = 0;
  while ((local_94[local_98] != '\0' && (local_94[local_98] != '\n'))) {
    cVar1 = local_94[local_98];
    uVar2 = rand();
    sprintf("%02x",(int)cVar1 ^ uVar2 & 0xff);
    local_98 = local_98 + 1;
  }
  putchar(10);
}
```

Por lo que puede verse, el algoritmo hace XOR a la serie de bytes
recibida por entrada estándar, contra una sucesión de valores
pseudo-aleatorios que se generan a partir de una semilla cuyo valor
es la posición de memoria de un símbolo (la propia función `main()`).
El problema es que no sabemos cual es la posición de main, ergo,
cuál es la semilla.

Así que lo que pensamos con mi novia fue extraer el algoritmo y armar
un proceso que, por fuerza bruta, va obteniendo las sucesiones de las
distintas semillas posibles (entero sin signo), hasta que el resultado
comience o contenga `EKO{`.

Al inicio tuvimos un algún positivo pues no recuerdo ahora qué seed
particular daba como resultado `EKO{` y continuaba con basura.
Estuvimos largo rato para tratar de entender qué sucedía y luego
nos dimos por vencidos y lo dejamos asentar.

Bueno, como ustedes se habrán dado cuenta, el MD5 estaba para algo:
como es posible que varias de las cadenas obtenidas contengan la
secuencia `EKO{`, una buena forma de darse cuenta cual es la correcta
es hacer MD5 al resultado del XOR.

Entonces reemplazamos la condición de que sea "EKO{" por que coincida
con el MD5 buscado. En realidad no recuerdo ahora si mantuvimos la
condición de que contenga "EKO{" a fin de abortar rápidamente si el
resultado no coincidía para nada. Lo que sí hicimos fue cotejar luego
contra el MD5 consignado, a fin de evitar los falsos positivos.

Hicimos varias versiones del mismo código, pero una que nos funcionó
es [brute-pipe.c](./code/brute-pipe.c)

Instalamos dependencias y compilamos

    apt install libssl-dev:i386
    gcc -s -m32 -lcrypto brute-pipe.c -o brute-pipe

Luego de varios minutos de procesamiento, dio la respuesta:

    $ ./brute-pipe
     ...
    Found matching MD5 with seed 0xf775c66c (4151690860)
    Output: The flag is EKO{bullshit_PIE_over_x86}
     Input: d740a5dc607f78fbffe520efc7caebd2137940ddb26c30c2fd37ed743b77038d326a9c7e7e80   .@..`.x... ......y@..l0..7.t;w..2j.~~.
    Output: 54686520666c616720697320454b4f7b62756c6c736869745f5049455f6f7665725f7838367d   The flag is EKO{bullshit_PIE_over_x86}
    Target: 080d5caaed95af9ab072c41de3a73c24   ..\......r....<$
      Hash: 080d5caaed95af9ab072c41de3a73c24   ..\......r....<$

Flag

    EKO{bullshit_PIE_over_x86}

-- [maurom](https://maurom.com/)
