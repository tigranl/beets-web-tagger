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

import socket
import threading
import webbrowser
from urllib.parse import urlencode
from beets.plugins import BeetsPlugin
from beets.ui.commands import PromptChoice
from beets import ui
from beets import config


class Server(threading.Thread):
    def __init__(self, port=8000):
        threading.Thread.__init__(self)
        self.host = '127.0.0.1'
        self.port = port
        try:  # Start TCP socket, catch soket.error
            self.run_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.run_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.run_server.bind((self.host, self.port))
        except socket.error as error_msg:
            print("Error occurred: {0}".format(error_msg))

    def listen(self, size=1024):
        self.run_server.listen(1)
        while True:
            connection, addr = self.run_server.accept()
            # threading.Thread(target=self.receiver, args=(connection, addr)).start()
            data = connection.recv(size)
            if not data:
                break
            yield data


class MBWeb(BeetsPlugin):
    def __init__(self):
        super(MBWeb, self).__init__()
        self.port = config['web_tagger']['port'].as_number() or 8000
        self.register_listener('before_choose_candidate', self.prompt)
        self.register_listener('pluginload', self.run)
        self.running = None

    def run(self):
        server = Server()
        server.start()
        self.running = server

    def prompt(self, session, task):
        return [PromptChoice('T', 'Tag Lookup', self.choice)]

    def choice(self):
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
        return artist, realise
