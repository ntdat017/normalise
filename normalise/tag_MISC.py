# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import sys
import re


def tag_MISC(dic, verbose=True):
    """Return dictionary with added tag within the value tuple."""
    out = {}
    for ind, (nsw, tag) in dic.items():
        if verbose:
            sys.stdout.write("\r{} of {} subtagged".format(len(out), len(dic)))
            sys.stdout.flush()
        if looks_rude(nsw):
            out.update({ind: (nsw, tag, 'PROF')})
        elif is_url(nsw):
            out.update({ind: (nsw, tag, 'URL')})
        elif hashtag_pattern.match(nsw):
            out.update({ind: (nsw, tag, 'HTAG')})
        else:
            out.update({ind: (nsw, tag, 'NONE')})
    if verbose:
        sys.stdout.write("\r{} of {} classified".format(len(out), len(dic)))
        sys.stdout.flush()
        print("\n")
    return out


def looks_rude(w):
    """Return 'True' if w is three + characters of only letters and '*'."""
    return len(w) > 2 and allrude(w)


def allrude(w):
    """Return 'True' if all characters are letters or '*'."""
    for lt in w:
        if not lt == '*' and not lt.isalpha():
            return False
    return True


def is_url(w):
    """Return 'True' if start or end of w looks like a url."""
    if url_pattern.fullmatch(w):
        return True
    return False

urlstart_pattern = re.compile('''
("?)|
(https?://)|            #'http' followed by optional 's', then '://' OR
(www\.)                 #'www.'
''', re.VERBOSE | re.IGNORECASE)

urlend_pattern = re.compile('''
.*                      #any number of characters
\.                      # '.'
((com)|                 # 'com' OR
(org(\.uk)?)|           # 'org' followed optionally by '.uk' OR
(co\.uk))               # 'co.uk'
$                       #end of string
''', re.VERBOSE | re.IGNORECASE)

URL_RE_PATTERN = r'(?i)((?:"?[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]"?))'

MAIL_RE_PATTERN = r'(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)'

URL_MAIL_RE_PATTERN = URL_RE_PATTERN + '|' + MAIL_RE_PATTERN

url_pattern = re.compile(URL_MAIL_RE_PATTERN, re.VERBOSE | re.IGNORECASE)

hashtag_pattern = re.compile('''
\#
[A-Za-z0-9]+
[_-]?
[A-Za-z0-9]*
''', re.VERBOSE)
