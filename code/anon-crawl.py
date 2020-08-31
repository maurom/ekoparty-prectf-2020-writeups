#!/usr/bin/env python3
#
# anon-crawl.py
# quick & dirty crawler purposely written for the Anon challenge of the Ekoparty Pre-CTF 2020


from os import makedirs
from os.path import exists
import re
import requests


def getid(url):
    _, pasteid = url.rstrip('/').rsplit('/', 1)
    return pasteid


def save(pasteid, buffr):
    with open('cache/' + pasteid, 'wb') as fh:
        fh.write(buffr)


def readfile(pasteid):
    with open('cache/' + pasteid, 'rb') as fh:
        return fh.read()


def main():
    s = requests.session()
    visited = []
    pending = ['http://paste.ubuntu.com/p/HnGHwGk4rQ/']
    makedirs('cache')
    while pending:
        print('Visitados:')
        for u in visited:
            print('   ', u)
        print('Pendientes:')
        for u in pending:
            print('   ', u)
        url = pending.pop(0)
        if url in visited:
            continue
        pasteid = getid(url)
        visited.append(url)
        if exists('cache/' + pasteid):
            print('Recuperando', url)
            buffr = readfile(pasteid)
        else:
            print('Obteniendo ', url)
            buffr = s.get(url).content
            save(pasteid, buffr)
        if b'The Paste you are looking for does not currently exist.' in buffr:
            print('404')
            continue
        links = re.findall(r'http://paste.ubuntu.com/p/.*', buffr.decode('utf-8'))
        print('Match:', links)
        if not links:
            print('Possible flag: ', url)
            print(buffr)
            raise RuntimeError('Termine')
        for newurl in links:
            if newurl not in visited and newurl not in pending:
                pending.append(newurl)


if __name__ == '__main__':
    main()

