Esrom
=====

Challenge

> This is a real challenge for you!
>
> . ---- -- --- / -- --- / . ---- - / --.- -.-- -. ..- /
> .-.. ... --. / -. -.- - / -.-- ... ... .-. -- .- ..- /
> --.- ... -.- ...--- / .. ... -.- --- - .. ... -.- --- -
>
> The format of the flag is: EKO{lowercase_flag}

Category: Crypto

Esrom es morse al revés, y los que son radioaficionados saben
que en [Morse](https://en.wikipedia.org/wiki/Morse_code) no hay
secuencia `----` (bah, en realidad sí existe pero no se suele
utilizar porque es la letra "ch"); sin embargo, sí es usual
la secuencia `....` ("h").

Entonces básicamente hay que usar
[CyberChef](https://gchq.github.io/CyberChef/) para reemplazar
`.` por `-` y `-` por `.` y pasar a texto
(<a href="https://gchq.github.io/CyberChef/#recipe=Substitute('.-','-.')From_Morse_Code('Space','Forward%20slash')&input=LiAtLS0tIC0tIC0tLSAvIC0tIC0tLSAvIC4gLS0tLSAtIC8gLS0uLSAtLi0tIC0uIC4uLSAvIC4tLi4gLi4uIC0tLiAvIC0uIC0uLSAtIC8gLS4tLSAuLi4gLi4uIC4tLiAtLSAuLSAuLi0gLyAtLS4tIC4uLiAtLi0gLi4uLS0tIC8gLi4gLi4uIC0uLSAtLS0gLSAuLiAuLi4gLS4tIC0tLSAt">receta</a>).

    "THIS IS THE FLAG YOU ARE LOOKING FOR: MORSEMORSE"

O también bien en línea de comandos

    # apt install morse2ascii
    $ tr '.-' '-.' < esrom.txt > morse.txt
    $ morse2ascii morse.txt
    - decoded morse data:
    this  is  the  flag  you  are  looking  for:: morsemorse

Convertir al formato `EKO{lowercase_flag}`:

    EKO{morsemorse}

-- [maurom](https://maurom.com/)
