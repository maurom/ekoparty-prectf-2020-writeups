Incognito
=========

Challenge

> We have no idea about this file. May you help us?
>
> Attachment [Incognito](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Incognito?raw=true)

Category: Crypto

Primera acción de casi todo CTF, preguntarle a file de qué se trata el archivo:

    $ file Incognito
    Incognito: gzip compressed data, was "Incognito", last modified: Fri Jun 26
    18:00:51 2020, from Unix, original size 825959

Descomprimir y ver de qué se trata

    $ gunzip < Incognito > gunzipped
    $ file gunzipped
    gunzipped: ASCII text
    $ head -3 gunzipped
    vuk:eJs4+BAAN/<MCG4DC"hgBAi"WGEAAAl%W>,SAA:CL3OypB2evoWKAA5F,PPb%AXLwy[>KfBA
    AAkA)5U.BA@wSA*hwz8M5wo_AAr([ZzDlHo&e>)B}q5Uo[,}/P6,M9A&.qQd{gN(271,O14pY,R!
    iN!nRSSR%W`ppDqN>j.IfBsj`j4>x[DSf:"Zo%dC|Z4[2y"C:INv>j2w>Q8|sB_vYY73HO)skY+"

No parece base64, pero por las dudas lo validamos

    $ base64 -d gunzipped
    base64: entrada inválida

Nope. No es base64. Sin embargo podemos tratar de determinar el histograma.

Cada fila en esta lista es la cantidad de veces que aparece cada caracter
(la frecuencia y el código ASCII en decimal) en el archivo:

    $ od -vtu1 -An -w1 gunzipped | sort -n | uniq -c
      10727   10
       8716   33
       7883   34
       8996   35
       8975   36
        ...
       9032  124
       8878  125
       9522  126

    # o si queremos ver los caracteres
    $ od -vtc -An -w1 gunzipped | sort -n | uniq -c
       8716    !
       7883    "
       8996    #
        ...
       8796    7
       8970    8
       8984    9

Pero en resumen, el conjunto de caracteres (charset) es el siguietne:

    ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxuz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"
    (91 caracteres)

Buscando el charset en Google, caemos en esta útil página:

- Binary-to-text coding  
  <https://helpful.knobs-dials.com/index.php/Binary-to-text_coding>

donde encontramos que el encoding parece ser Base91, así que a github
para ver si hay algún decoder, porque en "las baterías" de python no viene...

- base91-python  
  <https://github.com/aberaud/base91-python>

bajamos el decoder y luego...

    $ python3 base91.py gunzipped salida
    $ file salida
    salida: PNG image data, 855 x 738, 8-bit/color RGB, non-interlaced
    $ xdg-open salida

Que es una imagen con la flag:

    EKO{B91_just_another_encoder}

-- [maurom](https://maurom.com/)
