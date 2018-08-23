"""Just a bunch of random convenience functions."""

import calendar
import time
import os
import sys
import re


def get_now():
    """get the time in epoch seconds"""
    return int(calendar.timegm(time.gmtime()))


def v_or_null(val):
    """returns a value or if it is None, then the string '<null>'"""
    return val if val else '<null>'


def get_file_details(fname):
    """do some fstat on a file and return the results"""
    mtime = 0
    ctime = 0
    file_size = 0

    try:
        mtime = int(os.path.getmtime(fname))
        ctime = int(os.path.getctime(fname))
        file_size = os.path.getsize(fname)
    except:
        print("-Warning- ")
        print(sys.exc_info())

    modtime = mtime
    if ctime > modtime:
        modtime = ctime

    return {'create': ctime,
            'modify': mtime,
            'now': get_now(),
            'size': file_size}


def quote_names_google(name):
    """
    GDrive does not like the name to have a backslash
    in it, at least not over the API. There is probably
    a more sensible way to escape this."""
    retval = re.sub(r"\\", '_', name)
    # handle ampersand
    # rv = re.sub(r"&",'%26',rv)
    return retval


def epoch_to_iso3339(epoch_ts):
    """convert an epoch time stamp to an ISO3339 string"""
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(epoch_ts))


def strip_objs(args):
    """for debug convenience, when debug printing certain objects,
    strip out the objects that have no string conversion methods"""
    retval = {}
    if isinstance(args, dict):
        for key in args:
            if not key in ['google', 'database', 'driveinst']:
                retval[key] = args[key]
    else:
        retval = args
    return retval


# helps write database to text file
def quote_for_db(thing, quote_for_csv=None):
    out = str(thing)
    if quote_for_csv:
        out = '"' + out.replace('"','""') + '"'
    return out


def num_to_binary_multiple_str(v, t='B'):
    """Take a number and convert it to mega, giga, etc"""

    if v < 0:
        v = -v

    prefixes = ['', 'k', 'M', 'G', 'T', 'P']
    iter_count = 0
    while iter_count < len(prefixes) and int(v / 1024) > 0:
        v /= 1024.0
        iter_count += 1
    prefix = prefixes[iter_count]
    rv = ''
    if iter_count:
        rv = "{:3.3f} {:s}i{:s}".format(v, prefix, t)
    else:
        rv = "{:d} {:s}".format(int(v), t)

    return rv


def interval_to_timestamp(interval):
    digits_and_letter = re.match(r'^(\d+)([smhdwMy])$',interval)
    all_digits = re.match(r'^(\d+)$',interval)
    now = get_now()
    rv = None
    if digits_and_letter:
        number = digits_and_letter.group(1)
        letter = digits_and_letter.group(2)
        multiplier = 1
        if letter == 's':
            multiplier = 1
        elif letter == 'm':
            multiplier = 60
        elif letter == 'h':
            multiplier = 60*60
        elif letter == 'd':
            multiplier = 24*60*60
        elif letter == 'w':
            multiplier = 7*24*60*60
        elif letter == 'M':
            multiplier = 30*24*60*60
        elif letter == 'y':
            multiplier = 365*24*60*60
        rv = now - multiplier * int(number)
    elif all_digits:
        rv = int(interval)

    return rv


