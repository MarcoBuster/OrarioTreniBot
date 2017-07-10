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

import json

from .. import main


class Inline:
    """
    Inline query base object
    """
    def __init__(self, update):
        self.update = update.inline_query
        self.id = self.update.id
        self.location = self.update.location
        self.sender = self.update.sender
        self.query = self.update.query
        self.offset = self.update.offset
        self._api = main.bot.api

    def answer(self,
               results,
               cache_time=300,
               is_personal=True,
               next_offset=None,
               switch_pm_text=None,
               switch_pm_parameter=None):
        self._api.call("answerInlineQuery", {
            "inline_query_id": self.id,
            "results": json.dumps(results),
            "cache_time": cache_time,
            "is_personal": is_personal,
            "next_offset": next_offset,
            "switch_pm_text": switch_pm_text,
            "swtich_pm_parameter": switch_pm_parameter
        })
