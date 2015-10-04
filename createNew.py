#!/usr/bin/env python
# -*- coding: utf-8

import os
import argparse
import logging


def rm_special_chars(input_string):
    '''remove special characters from string'''
    special_chars = {u' ': '_', u'ü': u'ue', u'ä': 'ae',
                     u'ö': 'oe', u'ß': 'ss'}
    for k, v in special_chars.items():
        input_string = input_string.replace(k, v)
    return input_string


def main(args):
    band_name = args.artist
    song_name = args.song

    band_name_clean = rm_special_chars(band_name)
    song_name_clean = rm_special_chars(song_name)

    # create artist folder
    path = os.mkdir(os.path.join('artists', band_name_clean))
    if not os.path.isdir(path):
        for alreadyThere in os.listdir('artists'):
            if alreadyThere.lower() == band_name_clean.lower():
                logging.warning(
                    ('Es gibt schon den Artists {}. '
                     'Werde diesen stattdessen verwenden.'.format(
                        alreadyThere)))
                band_name_clean = alreadyThere
                break
        os.mkdir(path)

    # check that song does not already exist
    path = os.path.exists(reduce(
        lambda x, y: os.path.join(x, y),
        ['artists', band_name_clean, song_name_clean + '.tex']))
    if os.path.exists(path):
        logging.error("Oha, den Song {} gibt's irgendwie schon!".format(
            path))
        logging.error("   --> besser du schaust mal nach, was da geht..")
        exit(1)

    # creat song's LaTeX file from template
    out_filename = 'artists/{}/{}.tex'.format(band_name_clean, song_name_clean)
    with open('template.tex') as fd_src:
        with open(out_filename, 'w') as fd_dest:
            for l in fd_src:
                l = l.replace('ADDHERETITLE', song_name)
                l = l.replace('ADDHEREBAND', band_name)
                fd_dest.write(l)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create new song ')
    parser.add_argument('--artist', dest='artist', required=True,
                        help='artist of the song')
    parser.add_argument('--song', dest='song', required=True,
                        help='name of the song')
    args = parser.parse_args()
    main(args)
