# Copyright (c) 2016-2017 The OrarioTreniBot Authors (see AUTHORS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ALL CREDITS FOR THIS FILE TO https://github.com/bluviolin

import json
import os
import re
from urllib.parse import quote

from . import dateutils

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


class Utils:
    __path = os.getcwd() + '/'.join(['', 'data', 'viaggiatreno', 'stationIDs.json'])
    with open(__path, 'r') as fp:
        __stationsIDs = json.load(fp)

    @staticmethod
    def station_from_ID(station_ID):
        return Utils.__stationsIDs.get(station_ID, 'UNKNOWN')

    @staticmethod
    def exists_station_ID(station_ID):
        return station_ID in Utils.__stationsIDs

    @staticmethod
    def train_runs_on_date(train_info, date):
        # trainInfo['runs_on'] flag:
        # G    Runs every day
        # FER5 Runs only Monday to Friday (holidays excluded)
        # FER6 Runs only Monday to Saturday (holidays excluded)
        # FEST Runs only on Sunday and holidays
        runs_on = train_info.get('runs_on', 'G')
        suspended = train_info.get('suspended', [])

        for from_, to in suspended:
            ymd = date.strftime('%Y-%m-%d')
            if from_ <= ymd <= to:
                return False

        if runs_on == 'G':
            return True

        wd = date.weekday()

        if runs_on == 'FEST':
            return dateutils.is_holiday(date) or wd == 6

        if dateutils.is_holiday(date):
            return False

        if runs_on == 'FER6' and wd < 6:
            return True
        if runs_on == 'FER5' and wd < 5:
            return True

        return False


def _decode_json(s):
    if s == '':
        return None
    return json.loads(s)


def _decode_lines(s, linefunc):
    if s == '':
        return []

    lines = s.strip().split('\n')
    result = []
    for line in lines:
        result.append(linefunc(line))

    return result


def _decode_cercaNumeroTrenoTrenoAutocomplete(s):
    def linefunc(line):
        r = re.search('^(\d+)\s-\s(.+)\|(\d+)-(\w+)-(\d+)', line)
        if r is not None:
            return r.group(2, 4, 5)

    return _decode_lines(s, linefunc)


def _decode_autocompletaStazione(s):
    return _decode_lines(s, lambda line: tuple(line.strip().split('|')))


class API:
    def __init__(self, **options):
        self.__verbose = options.get('verbose', False)
        self.__urlopen = options.get('urlopen', urlopen)
        self.__plainoutput = options.get('plainoutput', False)
        self.__decoders = {
            'andamentoTreno': _decode_json,
            'cercaStazione': _decode_json,
            'tratteCanvas': _decode_json,
            'dettaglioStazione': _decode_json,
            'regione': _decode_json,
            'cercaNumeroTrenoTrenoAutocomplete': _decode_cercaNumeroTrenoTrenoAutocomplete,
            'autocompletaStazione': _decode_autocompletaStazione,
            'soluzioniViaggioNew': _decode_json,
            'partenze': _decode_json,
            'arrivi': _decode_json,
            'news': _decode_json,
            'cercaNumeroTreno': _decode_json,
        }
        self.__default_decoder = lambda x: x

    def __checkAndDecode(self, function, data):
        decoder = self.__decoders.get(function, self.__default_decoder)
        return decoder(data)

    def call(self, function, *params, **options):
        plain = options.get('plainoutput', self.__plainoutput)
        verbose = options.get('verbose', self.__verbose)

        base = 'http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno/'
        path = '/'.join(quote(str(p)) for p in params)
        url = base + function + '/' + path

        if verbose:
            print(url)

        try:
            req = self.__urlopen(url)
        except UnicodeError:
            return []

        data = req.read().decode('utf-8')
        if plain:
            return data
        else:
            return self.__checkAndDecode(function, data)

    def cercaNumeroTreno(self, numeroTreno):
        return self.call('cercaNumeroTreno', numeroTreno)

    def andamentoTreno(self, codOrigine, numeroTreno, dataPartenza=None):
        infoTreni = self.call('cercaNumeroTrenoTrenoAutocomplete', numeroTreno)

        for infoTreno in infoTreni:
            if codOrigine == infoTreno[1]:
                dataPartenza = infoTreno[2]
                break

        return self.call('andamentoTreno', codOrigine, numeroTreno, dataPartenza)
