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

from .. import main


class Callback:
    """
    Callback base object
    """
    def __init__(self, update):
        """
        Create a callback object
        :param update: Telegram's update object
        """
        self.update = update.callback_query
        self.id = self.update.id
        self.query = self.update.data
        self.sender = self.update.sender
        self.message = self.update.message
        self._api = main.bot.api

        self.isInline = (True if not self.message else False)
        self.inline_message_id = (self.update.inline_message_id if self.isInline else None)
        self.chat = (self.message.chat if not self.isInline else None)

    def notify(self, text, alert=False, cache_time=0):
        self._api.call("answerCallbackQuery", {
            "callback_query_id": self.id,
            "text": text,
            "show_alert": alert,
            "cache_time": cache_time
        })
