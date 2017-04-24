# Copyright (c) 2016-2017 Marco Aceti <dev@marcoaceti.it>
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

from . import dateutils


def formatTrain(raw: dict):
    dh = dateutils.format_timestamp(raw.get('orarioPartenza'), fmt="%H:%M")
    ah = dateutils.format_timestamp(raw.get('orarioArrivo'), fmt="%H:%M")

    delay = raw['ritardo']
    if delay == 1:
        status = '\n🕒 <b>In ritardo di {x} minuto</b>'.format(x=delay)
    elif delay > 1:
        status = '\n🕒 <b>In ritardo di {x} minuti</b>'.format(x=delay)
    elif delay < 0:
        status = '\n🕒 <b>In anticipo di {x} minuti</b>'.format(x=abs(delay))
    else:
        status = '\n🕒 <b>In perfetto orario</b>'

    last_detection = raw['stazioneUltimoRilevamento']
    if last_detection in ['--', None] or last_detection == raw.get('origine'):
        status += ' a {o} (in partenza)'.format(o=raw.get('origine'))
    elif last_detection == raw.get('destinazione'):
        status += ' a {d} (arrivato a destinazione)'.format(d=last_detection)
    else:
        status += ' a {l} ({h})'.format(l=last_detection,
                                        h=dateutils.format_timestamp(raw.get('oraUltimoRilevamento'), fmt="%H:%M"))

    return (
        "🚅 <b>Treno {n}</b>"
        "\n🚉 <b>Stazione di partenza</b>: {d} ({dh})"
        "\n🚉 <b>Stazione di arrivo</b>: {a} ({ah})"
        "{s}"
        .format(n=raw.get('compNumeroTreno'),
                d=raw.get('origine'), dh=dh,
                a=raw.get('destinazione'), ah=ah,
                s=status)
    )
