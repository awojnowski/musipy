#!/usr/bin/env python

import os
import re
import requests
import sys
import urllib

download_path = '/Users/Aaron/Downloads/'
itunes_path = '/Applications/iTunes.app/'

possible_arguments = [
   '-r', # removes remixes
    '--noremix'
];

include_remixes = True


class Song:

    URL = None
    name = None
    bitrate = None
    duration = None
    size = None

    def __init__(self, input=None, parse_remix=True):

        if input:
            self.parse_song(input)

    def parse_song(self, input, parse_remix=True):

        # remove newlines and tabs
        input = input.replace('\t', '')
        input = input.replace('\n', '')

        # parse the URL
        regex = re.compile('<a href="(.*)" rel="nofollow" target="_blank" style="color:green;">Download</a></div>')
        match = regex.search(input)
        if match:
            self.URL = match.group(1)

        #parse the name
        regex = re.compile('<div style="font-size:15px;"><b>(.*)</b></div>')
        match = regex.search(input)
        if match:
            self.name = match.group(1)

        #parse other metadata
        regex = re.compile('<div class="left"><!-- info mp3 here -->(.*)<br />(.*)<br />(.*)</div><div id="right_song">')
        match = regex.search(input)
        if match:
            self.bitrate = match.group(1)
            self.duration = match.group(2)
            self.size = match.group(3)

        if not self.URL or not self.name or not self.bitrate or not self.duration or not self.size:
            return False

        url = self.URL
        url = urllib.quote(url.encode("utf-8"))
        url = url.replace('%3A//', '://')
        self.URL = url

        duration = self.duration
        self.duration = duration.replace(' ', '')

        if not parse_remix:
            if self.name.lower().find("remix") != -1:
                return False

        return True


def main():

    print '### Welcome to Musi.py ###'

    arguments = sys.argv
    del arguments[0]

    if "-r" in arguments or "--noremix" in arguments:
        print 'Remixes will not be included in this search.'
        include_remixes = False
    else:
        include_remixes = True

    arguments = [a for a in arguments if not a in possible_arguments];

    search_term = ' '.join(arguments)

    if len(search_term) == 0:
        print 'Hey bro, we need a search term here.'
        exit(0)

    print '\nSearching for song named "%s".' % search_term

    mp3_skull_url = 'http://mp3skull.com/mp3/%s.html' % search_term

    print 'Beginning request with URL: %s' % mp3_skull_url

    request = requests.get(mp3_skull_url)

    print 'Request completed.'

    response = request.text
    if response.find('The content was removed due to copyrights owners\' request.') != -1:
        print 'Content unavailable.  The content was removed due to the copyright owners\' request.'
        exit(0)

    raw_songs = response.split('<div id="song_html"')
    del raw_songs[0]

    songs = []
    for rawSong in raw_songs:

        song = Song()
        result = song.parse_song(rawSong, include_remixes)

        if result:
            songs.append(song)

    if len(songs) == 0:
        print 'No songs were found matching your search "%s".' % search_term
        exit(0)

    # sort songs by bitrate
    songs = sorted(songs, key=lambda x: int(x.bitrate.split(' ')[0]), reverse=True)

    for song in songs:

        print '\n' + song.name
        print '%s | %s | %s' % (song.bitrate, song.duration, song.size)
        response = raw_input('Download this song? (y/n/q): ')

        print '\n'

        if response == 'y':
            name = re.sub(r'\W+', '', song.name) + '.mp3'

            print 'Downloading...\n%s\n%s\n' % (song.URL, name)

            command = 'curl --output "%s%s" --url "%s" --location' % (download_path, name, song.URL)
            os.system(command)
            os.system('open -a %s %s%s' % (itunes_path, download_path, name))

            exit(0)
        elif response == 'q':
            print 'Quitting.\n'
            exit(0)
        else:
            print 'Skipping'

    print 'No more songs left to show.  Try refining your search term.'

if __name__ == '__main__':
    main()
