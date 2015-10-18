#!/usr/bin/env python3
import re
import os
import string
from jinja2 import Environment, PackageLoader

MAX_LINE_LENGTH = 60


class HTMLMaker(object):

    chord_regex = re.compile(r'.*\[([^]]+)\].*')

    def make_valid_file_name(self, artist, title):
        '''reduce filename to valid ASCII letters'''
        artist, title = map(
            lambda x: ''.join(
                [a for a in x if a in string.ascii_letters]),
            [artist, title])
        return '{}_{}.html'.format(artist, title)

    def substitute_latex_stuff(self, line):
        '''substitute LaTeX commands'''
        line = line.replace(r'\ldots{}', '..')
        line = line.replace(r'\qquad', '&nbsp;&nbsp;&nbsp;')
        line = line.replace(r'\quad', '&nbsp;&nbsp;')
        line = re.sub(r'(\[[^\]]+\]){}$', r'&nbsp;&nbsp;\1', line)
        line = re.sub(r'([^\[])(\[[^\]]+\]){}', r'\2\1', line)
        line = re.sub(r'^{}', r'&nbsp;', line)
        line = line.replace(r'\ ', '&nbsp;')
        line = re.sub(r'\\chords{([^}]+)}', r'\1', line)
        line = line.replace(r'\#', '#')
        return line

    def is_latex(self, line):
        '''True if LateX command line'''
        return line and line[0] == '\\'

    def readin_file(self, filename):
        '''read-in file and split into lines'''
        lines = []
        with open(filename) as fd:
            for line in fd.readlines():
                # skip empty
                if lines and line == '\n' and lines[-1] == '\n':
                    continue
                if not self.is_latex(line):
                    line = self.substitute_latex_stuff(line)
                # find white space line break point
                line_length = MAX_LINE_LENGTH
                #while (line_length > 0 and len(line) > line_length and
                #    line[line_length] != ' '):
                #    line_length -= 1
                ## split line
                #if not self.is_latex(line) and len(line) > line_length:
                #    lines.append(line[:line_length])
                #    line = '  ' + line[line_length:]
                lines.append(line)
        return lines

    def create_html_file(self, filename):
        '''create HTML representation of the LaTeX file'''
        output_lines = []
        title = 'kein Titel'
        artist = 'kein Artist'
        for line in self.readin_file(filename):
            if self.is_latex(line):
                # extract artist and title information
                if line.startswith('\\subsection'):
                    end = line.find('\\index{')
                    title = line[13:end]
                    start = line.find('\\small ') + len('\\small ')
                    artist = line[start:-3]
                continue
            # add empty line to have space for the chords
            #if self.chord_regex.match(line):
            #    output_lines.append('')
            # include chords HTML command
            line = re.sub(
                r'\[([^]]+)\]',
                r'<span>\1</span>',
                line)
            output_lines.append(line)

        # write song to file using template
        env = Environment(loader=PackageLoader('htmlmaker', 'templates'))
        html_filename = self.make_valid_file_name(artist, title)
        with open(os.path.join('pages', html_filename), 'w') as fd:
            fd.write(env.get_template('song.html').render(
                title=title,
                artist=artist,
                chords='<br/>\n'.join(output_lines)))
        return artist, title, html_filename

    def run(self, artists_folder):
        # get list of all songs
        all_files = []
        for root, _, files in os.walk(artists_folder):
            all_files.extend([os.path.join(root, f) for f in files if (
                os.path.splitext(f)[1] == '.tex')])

        # create index
        index = {}
        for f in all_files:
            artist, title, html_filename = self.create_html_file(f)
            entry = index.setdefault(artist, [])
            entry.append((title, html_filename))

        # create index page
        alphabetic_index = {
            'a': 'A-E', 'f': 'F-K', 'l': 'L-P', 'q': 'Q-V', 'w': 'W-Z'}
        with open('pages/index.html', 'w') as fd:
            env = Environment(loader=PackageLoader('htmlmaker', 'templates'))
            full_index = []
            last = ''
            for artist, songs in sorted(index.items()):
                if (artist[0].lower() in alphabetic_index and
                        last != artist[0].lower()):
                    last = artist[0].lower()
                    # set anchor for page index
                    full_index.append(
                        '<span class="anchor" id="{}"></span>\n'.format(last))
                for title, path in songs:
                    full_index.append(
                        '<a href="{0}">{1} - {2}</a><br/>\n'.format(
                            path, artist, title))
            fd.write(env.get_template('index.html').render(
                alphabetic_index=[
                    (k, v) for k, v in sorted(alphabetic_index.items())],
                index=''.join(full_index)))
