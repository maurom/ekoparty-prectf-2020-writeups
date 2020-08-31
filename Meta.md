Meta
====

Challenge

> Data
>
> Attachment
> [Meta](https://github.com/estebancano-dev/CTF-Writeups/blob/master/20200626%20Ekoparty%20Pre-CTF/Files/Meta?raw=true)

Category: Forensics

El título lo dice todo.

    $ file Meta
    Meta: 7-zip archive data, version 0.4
    $ 7z l Meta
    ...
    
    Scanning the drive for archives:
    1 file, 525142 bytes (513 KiB)
    
       Date      Time    Attr         Size   Compressed  Name
    ------------------- ----- ------------ ------------  ------------------------
    2020-07-03 18:30:20 ....A       525153       525012  ekoctf.jpg
    ------------------- ----- ------------ ------------  ------------------------
    2020-07-03 18:30:20             525153       525012  1 files

    $ 7z x Meta ekoctf.jpg

Un 7zip que posee dentro un jpeg, veamos ahora los **metadatos**

    $ exiftool ekoctf.jpg
    ExifTool Version Number         : 11.16
    File Name                       : ekoctf.jpg
     ...
    Comment                         : EKO{C4nt_t0uch_th1s}
     ...

Flag

    EKO{C4nt_t0uch_th1s}

-- [maurom](https://maurom.com/)
