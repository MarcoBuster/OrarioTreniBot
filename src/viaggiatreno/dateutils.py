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

import datetime
import time

__italian_holidays = (
    '01-01', '06-01', '25-04', '01-05', '02-06',
    '15-08', '01-11', '08-12', '25-12', '26-12'
)


def easter(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1
    return datetime.date(year, month, day)


def is_holiday(date):
    ddmm = date.strftime('%d-%m')
    east = easter(date.year)  # Easter
    em = east + datetime.timedelta(1)  # Easter Monday
    return ddmm in __italian_holidays or date in (east, em)


def is_weekend(date):
    return date.weekday() in (5, 6)


def iter_month(year, month):
    d = datetime.date(year, month, 1)
    oneday = datetime.timedelta(1)
    while d.month == month:
        yield d
        d += oneday


def is_DST(_time=time.localtime()):
    return bool(_time.tm_isdst)


def check_timestamp(ts):
    return (ts is not None) and (ts > 0) and (ts < 2147483648000)


def format_timestamp(ts, fmt="%H:%M:%S"):
    return convert_timestamp(ts).strftime(fmt)


def convert_timestamp(ts):
    if check_timestamp(ts):
        return datetime.datetime.fromtimestamp(ts / 1000)
    else:
        return None
