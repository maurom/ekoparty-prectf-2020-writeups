#!/usr/bin/env python3
#
# gifexam.py
#
# Mauro A. Meloni <com.gmail@maumeloni>
#
# gifexam is a tool to analyse the internal structures of a animated gif file
#
# This was coded under the influence of substances. You've been warned.
#
from collections import OrderedDict
import json
from os import fstat
from pprint import pprint, pformat
from sys import argv
from struct import unpack

from PIL import Image
from PIL import GifImagePlugin


class PrintableOrderedDict(OrderedDict):

    def __repr__(self):
        indent = 4
        retval = '{\n'
        for key, value in self.items():
            if isinstance(value, PrintableOrderedDict):
                valuestr = str(value).replace('\n', '\n' + ' ' * indent)
            elif isinstance(value, dict):
                valuestr = '\n' + ' ' * indent * 2 + pformat(value).replace('\n', '\n' + ' ' * indent * 2)
            elif isinstance(value, list):
                valuestr = '\n' + ' ' * indent * 2 + pformat(value).replace('\n', '\n' + ' ' * indent * 2)
            else:
                valuestr = repr(value)
            retval += ' ' * indent + "'%s': %s,\n" % (key, valuestr)
        retval += '}\n'
        return retval


def pillow_analyze(filename):
    gif = Image.open(filename)
    for elem in dir(gif):
        attr = getattr(gif, elem)
        if not callable(attr):
            rattr = repr(attr)
            if len(rattr) < 200:
                print('%s: %s' % (elem, attr))
            else:
                print('%s: %s  . . .  %s' % (elem, rattr[:200], rattr[-200:]))

    palette = gif.global_palette.getdata()   # global
    print(palette)
    with open('palette.raw', 'wb') as fh:
        fh.write(palette[1])

    # Display individual frames from the loaded animated GIF file
    for frame in range(0,gif.n_frames):
        gif.seek(frame)
        #gif.show()

    gif.close()



def read_color_table(fh, num_colors):
    gif_color = '=BBB'
    color_table = {}
    for i in range(num_colors):
        triple = unpack(gif_color, fh.read(3))
        hexcolor = '#%02X%02X%02X' % triple
        color_table[i] = (triple, hexcolor)
    return color_table


def read_image_data(fh, num_colors):
    gif_lzw_min_code_size = '=B'
    gif_block_size = '=B'
    lzw_min_code_size = unpack(gif_lzw_min_code_size, fh.read(1))[0]
    next_block_size = unpack(gif_block_size, fh.read(1))[0]
    data = [lzw_min_code_size]
    while next_block_size != 0:
        data.append(fh.read(next_block_size))
        next_block_size = unpack(gif_block_size, fh.read(1))[0]
    return data


def read_graphic_control_ext(fh):
    gif_gce_header = '=BB'
    gif_gce_body = '=BBHB'
    gif_gce_trailer = '=B'
    gce_header = unpack(gif_gce_header, fh.read(2))
    if gce_header[0] != 0x21:
        raise ValueError('Expected Extension Introducer (0x21), got 0x%02x' % gce_header[0])
    if gce_header[1] != 0xF9:
        raise ValueError('Expected Graphic Control Label (0xF9), got 0x%02x' % gce_header[1])
    gce = PrintableOrderedDict(block_type='graphic_control_ext_block')
    gce['extension_introducer'], gce['graphic_control_label'] = gce_header
    gce_body = unpack(gif_gce_body, fh.read(5))
    gce['block_size'], packed, \
        gce['delay_time'], \
        gce['transparent_color_index'] = gce_body
    #gce['reserved'] = bin((packed & 0b11100000) >> 5)
    gce['reserved'] = bin((packed & 0b11100000))
    gce['disposal_method'] = packed & 0b00011100
    gce['user_input_expected'] = bool(packed & 0b00000010)
    gce['transparent_color_used'] = bool(packed & 0b00000001)
    gce_trailer = unpack(gif_gce_trailer, fh.read(1))
    if gce_trailer[0] != 0x00:
        raise ValueError('Expected Block Terminator (0x00), got 0x%02x' % gce_trailer[0])
    return gce


def read_application_ext(fh):
    gif_app_header = '=BB'
    gif_app_body = '=B8s3sB'
    gif_app_trailer = '=B'
    app_header = unpack(gif_app_header, fh.read(2))
    if app_header[0] != 0x21:
        raise ValueError('Expected Extension Introducer (0x21), got 0x%02x' % app_header[0])
    if app_header[1] != 0xFF:
        raise ValueError('Expected Application Extension Label (0xFF), got 0x%02x' % app_header[1])
    app = PrintableOrderedDict(block_type='application_extension_block')
    app['extension_introducer'], app['app_extension_label'] = app_header
    app_body = unpack(gif_app_body, fh.read(13))
    app['block_size'], \
        app['application_identifier'], \
        app['app_authentication_code'], \
        app['length_of_data_subblock'] = app_body
    if app['block_size'] != 0x0B:
        raise ValueError('Expected Application Block Size (0x0B), got 0x%02x' % app['block_size'])
    gif_netscape_app_data = '=BH'
    data = unpack(gif_netscape_app_data, fh.read(3))
    app['data'] = {
        'byte': data[0],
        'loop_count': data[1],
    }
    if app['data']['byte'] != 0x01:
        raise ValueError('Expected App Data Byte (0x01), got 0x%02x' % app['data']['byte'])
    app_trailer = unpack(gif_app_trailer, fh.read(1))
    if app_trailer[0] != 0x00:
        raise ValueError('Expected Block Terminator (0x00), got 0x%02x' % app_trailer[0])
    return app    


def read_plain_text_ext(fh):
    gif_text_header = '=BB'
    gif_text_body = '=BHHHHBBBB'
    gif_text_trailer = '=B'
    text_header = unpack(gif_text_header, fh.read(2))
    if text_header[0] != 0x21:
        raise ValueError('Expected Extension Introducer (0x21), got 0x%02x' % text_header[0])
    if text_header[1] != 0x01:
        raise ValueError('Expected Plain Text Label (0x01), got 0x%02x' % text_header[1])
    text = PrintableOrderedDict(block_type='plain_text_extension_block')
    text['extension_introducer'], text['text_extension_label'] = text_header
    text_body = unpack(gif_text_body, fh.read(13))
    text['block_size'], \
        text['text_grid_left_pos'], \
        text['text_grid_top_pos'], \
        text['text_grid_width'], \
        text['text_grid_height'], \
        text['character_cell_width'], \
        text['character_cell_height'], \
        text['text_foreground_color_index'], \
        text['text_background_color_index'] = text_body
    next_block_size = unpack(gif_text_trailer, fh.read(1))[0]
    data = []
    while next_block_size != 0:
        data.append(fh.read(next_block_size))
        next_block_size = unpack(gif_text_trailer, fh.read(1))[0]
    text['data'] = data
    if next_block_size != 0x00:
        raise ValueError('Expected Block Terminator (0x00), got 0x%02x' % next_block_size)
    return text    


def read_comment_ext(fh):
    gif_comment_header = '=BB'
    gif_comment_trailer = '=B'
    comment_header = unpack(gif_comment_header, fh.read(2))
    if comment_header[0] != 0x21:
        raise ValueError('Expected Extension Introducer (0x21), got 0x%02x' % comment_header[0])
    if comment_header[1] != 0xFE:
        raise ValueError('Expected Comment Label (0xFE), got 0x%02x' % comment_header[1])
    comment = PrintableOrderedDict(block_type='comment_extension_block')
    comment['extension_introducer'], comment['comment_label'] = comment_header
    next_block_size = unpack(gif_comment_trailer, fh.read(1))[0]
    data = []
    while next_block_size != 0:
        data.append(fh.read(next_block_size))
        next_block_size = unpack(gif_comment_trailer, fh.read(1))[0]
    comment['data'] = data
    if next_block_size != 0x00:
        raise ValueError('Expected Block Terminator (0x00), got 0x%02x' % next_block_size)
    return comment


def read_image_descriptor(fh, framenum, gct_colors):
    gif_imgdesc = '=BHHHHB'
    descriptor = unpack(gif_imgdesc, fh.read(10))
    image = PrintableOrderedDict(block_type='image_descriptor_block', frame_number=framenum)
    image['separator'], \
        image['left'], image['top'], \
        image['width'], image['height'], \
        packed = descriptor
    if image['separator'] != 0x2C:
        raise ValueError('Expected Image Separator (0x2C), got 0x%02x' % image['separator'])
    image['local_color_table_present'] = bool(packed & 0b10000000)
    image['is_interlaced'] = bool(packed & 0b01000000)
    image['lct_is_sorted'] = bool(packed & 0b00100000)
    # image['reserved' ] = bin((packed & 0b00011000) >> 3)
    image['reserved' ] = bin((packed & 0b00011000))
    image['local_color_table_size'] = packed & 0b00000111
    if image['local_color_table_present']:
        image['_local_color_table_num_colors'] = 2 ** ((packed & 0b00000111) + 1)
        image['local_color_table'] = read_color_table(fh, image['_local_color_table_num_colors'])
    else:
        image['_local_color_table_num_colors'] = 0
        image['local_color_table'] = None
    num_colors = image['_local_color_table_num_colors']
    if num_colors == 0:
        num_colors = gct_colors        
    # image['data'] = read_image_data(fh, num_colors)
    read_image_data(fh, num_colors)
    return image


def find_duped_colors(color_table):
    colors = {}
    for triple, hexcolor in color_table.values():
        try:
            colors[hexcolor] += 1
        except KeyError:
            colors[hexcolor] = 1
    colors = sorted(colors.items(), key=lambda x: x[1])
    return [color for color in colors if color[1] > 1]


def custom_analyze(filename):
    # https://www.w3.org/Graphics/GIF/spec-gif89a.txt
    # http://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html

    def peek(fh, size=1):
        filepos = fh.tell()
        buffr = fh.read(size)
        fh.seek(filepos)
        return buffr

    gif = open(filename, 'rb')
    gif_header = '=3s3s'
    gif_lsd = '=HHBBB'

    info = PrintableOrderedDict(_filename=filename)

    header = unpack(gif_header, gif.read(6))
    info['signature'], info['version'] = header

    lsd = unpack(gif_lsd, gif.read(7))
    info['logical_screen_width'], \
        info['logical_screen_height'], \
        packed, \
        info['background_color_index'], \
        info['pixel_aspect_ratio'] = lsd
    info['global_color_table_present'] = bool(packed & 0b10000000)
    info['color_resolution'] = packed & 0b01110000
    info['gcd_is_sorted'] = bool(packed & 0b000010000)
    info['global_color_table_size'] = packed & 0b00000111
    info['_global_color_table_num_colors'] = 2 ** ((packed & 0b00000111) + 1)

    if info['global_color_table_present']:
        info['global_color_table'] = read_color_table(gif, info['_global_color_table_num_colors'])
        info['_redundant_colors'] = find_duped_colors(info['global_color_table'])
    else:
        info['global_color_table'] = None

    info['blocks'] = []
    info['frames'] = 0

    while True:
        nextbyte = peek(gif)
        if peek(gif, 2) == b'\x21\xFF':     # application extension
            info['blocks'].append(read_application_ext(gif))
        elif peek(gif, 2) == b'\x21\xF9':   # graphic control extension
            info['blocks'].append(read_graphic_control_ext(gif))
        elif peek(gif, 2) == b'\x21\x01':   # plaint text extension
            info['blocks'].append(read_plain_text_ext(gif))
        elif peek(gif, 2) == b'\x21\xFE':   # comment extension
            info['blocks'].append(read_comment_ext(gif))
        elif nextbyte == b'\x2C':           # image descriptor 
            info['blocks'].append(read_image_descriptor(gif, info['frames'], info['_global_color_table_num_colors']))
            info['frames'] += 1
        elif nextbyte == b'\x3B':           # trailer
            filesize = fstat(gif.fileno()).st_size
            info['_gif_expected_size'] = gif.tell() + 1
            info['_remaining_bytes'] = filesize - info['_gif_expected_size']
            break
        else:
            raise ValueError('Expected Extension, Image Descriptor or Trailer, got 0x%02x' % nextbyte)
        #print(info['blocks'][-1])

    print(info)

    gif.close()


def export_replaced_colors(filename):
    with open(filename, 'rb') as fh:
        buffr = bytearray(fh.read())
    for i in range(256):
        filename = 'output/index_%03d.gif' % i
        output = buffr[:]
        for b in range(256):
            if b == i:
                output[0x0D + b * 3 + 0] = 0xFF
                output[0x0D + b * 3 + 1] = 0x00
                output[0x0D + b * 3 + 2] = 0x00
            else:
                output[0x0D + b * 3 + 0] = 0xFF
                output[0x0D + b * 3 + 1] = 0xFF
                output[0x0D + b * 3 + 2] = 0xFF
        with open(filename, 'wb') as fh:
            fh.write(output)
        print('Wrote %s' % filename)


if __name__ == '__main__':
    if len(argv) <= 1:
       print('Usage: %s GIFIMAGE.GIF' % argv[0])
    else:
       filename = argv[1]
    # pillow_analyze(filename)
    # print('-' * 80)
    custom_analyze(filename)
    # export_replaced_colors(filename)
