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

import os.path as p


def gen_config():
    conf = (
        '# Copyright (c) 2016-2017 Marco Aceti <dev@marcoaceti.it>'
        '\n#'
        '\n# Permission is hereby granted, free of charge, to any person obtaining a copy'
        '\n# of this software and associated documentation files (the "Software"), to deal'
        '\n# in the Software without restriction, including without limitation the rights'
        '\n# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell'
        '\n# copies of the Software, and to permit persons to whom the Software is'
        '\n# furnished to do so, subject to the following conditions:'
        '\n#'
        '\n# The above copyright notice and this permission notice shall be included in all'
        '\n# copies or substantial portions of the Software.'
        '\n#'
        '\n# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR'
        '\n# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,'
        '\n# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE'
        '\n# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER'
        '\n# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,'
        '\n# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE'
        '\n# SOFTWARE.'
        '\n'
        '\n# -- Redis configuration --'
    )
    rhost = input("Enter the address of the redis server [localhost]: ") or "localhost"
    rport = input("Enter the port of the redis server [6379]: ") or 6379
    assert int(rport), "The redis port must be an integer"
    rdb = input("Enter the redis database number [0]: ") or 0
    rpwd = input("Enter the redis server password [None]: ")
    token = input("Enter the bot token (take it from t.me/botfather): ")
    assert token, "You must insert a bot token"
    conf = conf + "\nREDIS_HOST = \"" + rhost + "\""

    conf = conf + "\nREDIS_PORT = " + str(rport)
    conf = conf + "\nREDIS_DB = " + str(rdb)

    if rpwd:
        conf = conf + "\nREDIS_PASSWD = \"" + rpwd + "\""
    else:
        conf += "\nREDIS_PASSWORD = None"

    conf += "\n\n# Telegram Bot API token from t.me/BotFather"
    conf += conf + "\nBOT_TOKEN = \"" + token + "\"\n"
    cfile = open("config.py", "w")
    cfile.write(conf)
    cfile.close()


if __name__ == "__main__":
    if not p.isfile("config.py"):
        gen_config()

    from src import main
    main.bot.run()
