MultiAlg
========

Challenge

> Could you crack these algorithms used by old apps?
>
> 02232F7410045B254F5C5D091118
>
> c784da5c2a2083b3

Category: Crypto

Con este estuve largo rato.

Podría ser un ciphertext y la clave?

Analicemos...

    $ python3
    import base64

    a = '02232F7410045B254F5C5D091118'                      # (28 bytes, 224 bits)
    bytes.fromhex(a) = b'\x02#/t\x10\x04[%O\\]\t\x11\x18'   # (14 bytes, 112 bits)
    base64.b64decode(a) = b'\xd3m\xb7\xd8^\xf8\xd7M8\xe4\x1d\xb9\xe0^B\xe4==\xd7]|'  # (21 bytes, 168 bits)
    base64.b64decode(a).hex() = 'd36db7d85ef8d74d38e41db9e05e42e43d3dd75d7c'         # (42 bytes, 336 bits)

    c = 'c784da5c2a2083b3' (16 bytes, 128 bits)
    bytes.fromhex(c) = b'\xc7\x84\xda\\* \x83\xb3'                # (8 bytes, 64 bits)
    base64.b64decode(c) = b's\xbf8u\xae\\\xd9\xad\xb4\xf3v\xf7'   # (12 bytes, 96 bits)
    base64.b64decode(c).hex() = '73bf3875ae5cd9adb4f376f7'        # (25 bytes, 192 bits)

Dada la longitud del primer valor, que pasado de hex a bytes son 112,
podría ser una _two-key triple DES key_ sin paridad?

    Two-key triple DES is option 2 where we encrypt with K1, then decrypt with K2
    and finally encrypt again with K1. The keyspace is thus 2 x 56 = 112 bits.

    For example, with K1=0x0123456789ABCDEF and K2=0xFEDCBA9876543210 you would
    set the triple DES key to be 0x0123456789ABCDEFFEDCBA98765432100123456789ABCDEF.

      0123456789ABCDEF FEDCBA9876543210 0123456789ABCDEF
      |<------K1------>|<------K2------>|<------K3------>|
    
      E(K1, D(K2, E(K1, P))) = C

Fuente: [Triple DES cryptography software](https://www.cryptosys.net/3des.html)

Según [DES key parity bit calculator](https://limbenjamin.com/articles/des-key-parity-bit-calculator.html)

    0x02232f7410045b with even parity is 0x0210cbef408010b6   <-- este es el algoritmo de paridad de DES
    0x02232f7410045b with odd  parity is 0x0311caee418111b7

Entonces hice varios tests para decodificar mediante DES con las posibles
combinaciones de las posibles claves, pero les ahorro el tiempo de lectura:
todo fue infructuoso.

Todo esto fue una distracción. Ahora la posta.

La otra posibilidad es que fueran storages inseguros utilizados por algunas
aplicaciones para almacenar claves (aplicaciones que usen las claves para algo,
por ejemplo versiones viejas de filezilla, winscp, incluso msn).

Esto me llevó a la búsqueda en Google de

- backup password decrypt
- insecure storage decrypt
- site:github.com backup password decrypt

Y entre las posibilidades (que indico más abajo), al final todo el bardo,
resulta que el primer valor es el resultado cifrado de una clave
[Cisco IOS Type 7](https://www.infosecmatter.com/cisco-password-cracking-and-decrypting-guide/)
que se descifra/crackea con
[IFM Cisco Password Cracker](https://www.ifm.net.nz/cookbooks/passwordcracker.html)
o bien con [Cisco Type 7 Password Decrypter](https://github.com/theevilbit/ciscot7)

    # https://github.com/theevilbit/ciscot7
    $ python3 ciscot7.py -d -p 02232F7410045B254F5C5D091118
    Decrypted password: EKO{b4dcr4pto

El segundo valor es una clave cifrada de VNC en formato Hexa que
se decifra con un Cracker de password de VNC tal como
[VNC Password Decrypt](https://github.com/trinitronx/vncpasswd.py)

    # https://github.com/trinitronx/vncpasswd.py
    $ python2 vncpasswd.py -d -H c784da5c2a2083b3
    Decrypted Bin Pass= '_vncsux}'
    Decrypted Hex Pass= '5f766e637375787d'

Concatenando ambos valores, el flag final queda:

    EKO{b4dcr4pto_vncsux}

-- [maurom](https://maurom.com/)

---

Otras cosas probadas y que no funcionaron

- https://github.com/justinbeatz/Stockpile
- http://www.routerpwn.com/Generators/
- https://github.com/frizb/PasswordDecrypts
- https://www.ibm.com/support/knowledgecenter/SSAW57_8.5.5/com.ibm.websphere.nd.multiplatform.doc/ae/csec_pwdencode.html
- https://github.com/palmerc/AESCrypt2
- https://github.com/gerard-/draytools
- Ruby library and executable to (de)crypt various router vendors (JunOS, IOS, NXOS) password.  
  <https://github.com/ytti/router_crypt>
- https://github.com/haseebT/mRemoteNG-Decrypt
