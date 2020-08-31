Cryptor
=======

Challenge

> Real crypto always win.
>
> Attachment
> [Cryptor](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Cryptor?raw=true)

Category: Reversing

Comenzamos

    $ file Cryptor
    Cryptor: PE32+ executable (console) x86-64, for MS Windows

Cryptor es un ejecutable de Windows x64. Obviamente, para correrlo hay
que renombrar Cryptor a Cryptor.exe.

Ya arrancamos mal. No tengo mucha experiencia en reversing y menos
aún de reversing en Windows. Pero anyway...

Entre los strings hay tres cosas interesantes:

    $ strings -a Cryptor
    ...
    RutPE8RisVNfmXNfbM09X7i7NH9=
    Great job! Your flag is 
    Bad boy!
    ...
    /rustc/c7087fe00d2ba919df1d813c040a5d47e43b0fe7\src\liballoc\vec.rs
    ...
    Rust panics must be rethrown
    note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
    ...

Por los strings, parece estar compilado con Rustc. Si nos fijamos en
el hash `c7087fe00d2ba919df1d813c040a5d47e43b0fe7` y lo buscamos en
los [releases de rust en github](https://github.com/rust-lang/rust/releases),
encontraremos que el hash corresponde al release
[1.44.1 (c7087fe)](https://github.com/rust-lang/rust/commit/c7087fe00d2ba919df1d813c040a5d47e43b0fe7).

Si tuviéramos IDA, con FLIRT podríamos ver qué cornos hacen las funciones
que tiene. Yo probé analizarlo con Ghidra, pero por desconocimiento no pude
lograr que tome los prototipos de las funciones, y la cantidad de funciones
era tal que no dio mucho resultado.

Utilizando [x64dbg](https://x64dbg.com/) es posible ejecutar el binario.
Analizando los imports, se ve que utiliza `ReadConsoleW` y `WriteConsoleW`.
Encontramos con mi novia que el programa espera un texto que finalice con
Ctrl+Z (o algo así).

Analizando lo que sucede luego de la llamada a `ReadConsoleW`, hay una
función de encoding que convierte lo ingresado a algo similar a Base64,
luego se coteja contra el string mencionado arriba y se recibe el
`Bad Boy` cuando es diferente. Podríamos nopear o cambiar el salto,
pero con eso no ganamos nada.

Cómo se resolvió? por fuerza bruta.

Con el símbolo ">" se indica el prompt para ingresar comandos del debugger.

Establecer un breakpoint en `00007FF6AC3C6E97`
(justo antes de la llamada a la función de encoding)

    > bp 00007FF6AC3C6E86

    00007FF6AC3C6E86 | 48:8D4D 20               | lea rcx,qword ptr ss:[rbp+20]                             |

Agregué watch en los argumentos que recibe y entrega la función

    > addwatch [...] (dirección donde está el objetivo RutPE...)
    > addwatch [RBP-40]
    > addwatch [RBP+20]

luego reemplacé el salto siguiente

    00007FF6AC3C6E97 | EB 00                    | jmp cryptor.7FF6AC3C6E99                                  |

por

    00007FF6AC3C6E97 | EB ED                    | jmp cryptor.7FF6AC3C6E86                                  |

    > asm 00007FF6AC3C6E97, "jmp cryptor.7FF6AC3C6E86"

o bien

    > 1:00007FF6AC3C6E97 = ED

(es indistinto)

Y ejecuté el binario, ingresando `AAAAAAAAAAAAAAAAAAAAAAAAA`, Enter y Ctrl+Z

Cuando llegó al breakpoint, fui variando los valores en `[RBP-40]` byte a byte
y reejecutando una y otra vez. Cuando hallaba que el inicio de la cadena
coincidía con lo buscado, modificaba el byte siguiente de la entrada.

    > inc 1:[[RBP-40]+n]; erun

donde n es el indice del caracter a variar; esto incrementa el primer byte.

Fuimos modificando y ejecutando hasta que en `[RBP+20]` apareció
`RutPE8RisVNfmXNfbM09X7i7NH9=`, que daba la pauta de dimos con el flag
esperado (aunque en realidad no funcionó, pero tenía pinta de flag).

En Windows no pude hacer andar el flag. Sin embargo, en Linux se puede
probar con wine:

    echo -n EKO{THIS_1s_not_b64} | wine Cryptor.exe

El siguiente script es un boceto (que NO funciona) de lo que se
utilizaría en x64dbg para hacer fuerza bruta:

```
// x64dbg script

bpd
bp 00007FF6AC3C6E86

addwatch [RBP-40]
addwatch [RBP+20]

asm 00007FF6AC3C6E97, "jmp cryptor.7FF6AC3C6E86"
erun

1:[[RBP-40]] = 20
// 2:[[RBP-40]] = 2020
loop1:
  erun
  log plaintext={s:[RBP-40]}
  log encoded={s:[RBP+20]}
  inc 1:[[RBP-40]+0]
  // inc 2:[[RBP-40]] ; erun
  // inc 1:[[RBP-40]] ; erun
  cmp [[RBP-40]], 30
  jne loop1:

quit:
  msg "finished"
  ret
```

Flag

    EKO{THIS_1s_not_b64}

-- [maurom](https://maurom.com/)
