#!/usr/bin/env python

import os
import argparse


def is_tex(filename):
    '''True if filename has LaTeX extension'''
    return os.path.splitext(filename)[1] == '.tex'


def main(args):

    # get artist list
    artist_folder = './artists'
    artist_list = os.listdir(artist_folder)
    artist_list.sort()

    # apply blacklist
    blacklist = []
    if args.blacklist_file:
        with open(args.blacklist_file) as fd:
            blacklist = fd.read().splitlines()

    # prepare main songbook document
    content = []
    for artist in artist_list:
        # add artist to document
        artist_name = artist.replace('_', ' ')
        content.append("%--------------------------------")
        content.append("\\newpage")
        content.append("\\addcontentsline{toc}{section}{" + artist_name + "}")

        # add artist's songs
        song_folder = os.path.join(artist_folder, artist)
        songs = [s for s in os.listdir(song_folder) if (
            is_tex(s) and s not in blacklist)]
        songs.sort()
        for i, song in enumerate(songs):
            command = '\include' if i != 0 else '\input'
            content.append('%s{%s/%s/%s}' % (
                command, artist_folder, artist, os.path.splitext(song)[0]))

    with open('base.tex') as f:
        tex_file = f.read()
        tex_file = tex_file.replace('CONTENT', '\n'.join(content))
        with open('songbook.tex', 'w') as f:
            f.write(tex_file)

    # compile latex document
    build_commands = [
        'latex songbook.tex',
        'latex songbook.tex',
        'makeindex songbook.idx -o songbook.ind',
        'latex songbook.tex']
    for bc in build_commands:
        ret = os.system(bc)
        if ret != 0:
            exit(ret)
    if args.use_ps:
        os.system('dvips songbook.dvi -o songbook.ps')
    else:
        os.system('dvipdfm songbook.dvi')

    # clean up
    temp_files = ['songbook.aux', 'songbook.out', 'songbook.toc',
                  'songbook.idx', 'songbook.ilg', 'songbook.ind',
                  'songbook.log']
    for f in temp_files:
        if os.path.exists(f):
            os.remove(f)
    os.system('find . -name "*.aux" -delete')

    # open viewer
    if args.show_view:
        ext = 'ps' if args.use_ps else 'pdf'
        os.system('%s songbook.%s' % (args.viewer, ext))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make the Songbook')
    parser.add_argument('--ps', dest='use_ps', action='store_true',
                        help='output PS file')
    parser.add_argument('--show', dest='show_view', action='store_true',
                        help='open view for PS/PDF file')
    parser.add_argument('--view', dest='viewer', default='evince',
                        help='specify viewer to show file')
    parser.add_argument('--blacklist', dest='blacklist_file',
                        help='file containing blacklist [song_file_name.ext]')
    args = parser.parse_args()
    main(args)
