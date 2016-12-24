# -*- coding: utf-8 -*-
# Copyright 2016, Tigran Kostandyan <t.kostandyan1@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

""" Runs local http server for MusicBrainz web tagger and handles users' requests """

from __future__ import division, absolute_import, print_function

try:
    from SocketServer import BaseRequestHandler, ThreadingMixIn, TCPServer
except ImportError:  # python 3
    from socketserver import BaseRequestHandler, ThreadingMixIn, TCPServer
from threading import Thread
import webbrowser
from urllib.parse import urlencode
from urllib import unquote_plus
from beets.plugins import BeetsPlugin
from beets.ui.commands import PromptChoice
from beets import ui
from beets import config

PORT = config['web_tagger']['port'].as_number() or 8000


class Server(BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        return data

    def parse(self, data):
        data = data.splitlines()
        s = data[0].decode()
        url = ''
        for char in s[5:]:
            if char != ' ':
                url += char
            else:
                break
        return url


class ThreadedServer(ThreadingMixIn, TCPServer):
    pass


class MBWeb(BeetsPlugin):
    def __init__(self):
        super(MBWeb, self).__init__()
        self.port = PORT
        self.register_listener('before_choose_candidate', self.prompt)
        self.register_listener('pluginload', self.run)

    def run(self):
        thread = ThreadedServer(('', PORT), Server)
        thread.serve_forever()

    def prompt(self, session, task):
        return [PromptChoice('l', 'Lookup', self.choice)]

    def choice(self, session, task):
        artist = ui.input_('Artist')
        realise = ui.input_('Album')
        track = ui.input_('Track')
        if not (artist, realise, track):
            ui.print_('Please, fill the search query')
            return self.prompt
        else:
            query = {'tport': self.port,
                     'artist': artist,
                     'track': track,
                     'realise': realise,
                     }

            url = 'http://musicbrainz.org/taglookup?{0}'.format(urlencode(query))
            ui.print_("Choose your tracks and click 'tagger' button to add:")
            webbrowser.open(url)
