# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import pickle
from io import open

from nltk.corpus import names

from normalise.detect import create_NSW_dict, mod_path
from normalise.tagger import tagify, is_digbased
from normalise.splitter import split, retagify
from normalise.class_ALPHA import run_clfALPHA
from normalise.class_NUMB import run_clfNUMB, gen_frame
from normalise.tag_MISC import tag_MISC
from normalise.expand_all import expand_all
from normalise.expand_NUMB import bmoney


with open('{}/data/wordlist.pickle'.format(mod_path), mode='rb') as file:
    wordlist = pickle.load(file)

with open('{}/data/names.pickle'.format(mod_path), mode='rb') as file:
    names_lower = pickle.load(file)


def list_NSWs(text, verbose=True, variety='BrE', user_abbrevs={}):
    if verbose:
        print("\nCREATING NSW DICTIONARY")
        print("-----------------------\n")

    NSWs = create_NSW_dict(text, verbose=verbose)
    if verbose:
        print("{} NSWs found\n".format(len(NSWs)))
        print("TAGGING NSWs")
        print("------------\n")
    tagged = tagify(NSWs, verbose=verbose)
    ALPHA_dict = {}
    NUMB_dict = {}
    MISC_dict = {}
    SPLT_dict = {}
    for item in tagged.items():
        tag = item[1][1]
        if tag == 'ALPHA':
            ALPHA_dict.update((item,))
        elif tag == 'NUMB':
            NUMB_dict.update((item,))
        elif tag == 'MISC':
            MISC_dict.update((item,))
        elif tag == 'SPLT':
            SPLT_dict.update((item,))
    if verbose:
        print("SPLITTING NSWs")
        print("--------------\n")
    splitted = split(SPLT_dict, verbose=verbose)
    if verbose:
        print("RETAGGING SPLIT NSWs")
        print("--------------------\n")
    retagged = retagify(splitted, verbose=verbose)
    for item in retagged.items():
        tag = item[1][1]
        if tag == 'SPLT-ALPHA':
            ALPHA_dict.update((item,))
        elif tag == 'SPLT-NUMB':
            NUMB_dict.update((item,))
        elif tag == 'SPLT-MISC':
            MISC_dict.update((item,))
    if verbose:
        print("CLASSIFYING ALPHABETIC NSWs")
        print("---------------------------\n")
    tagged_ALPHA = run_clfALPHA(ALPHA_dict, text, verbose=verbose, user_abbrevs=user_abbrevs)
    if verbose:
        print("CLASSIFYING NUMERIC NSWs")
        print("------------------------\n")
    tagged_NUMB = run_clfNUMB(NUMB_dict, text, verbose=verbose)
    if verbose:
        print("CLASSIFYING MISCELLANEOUS NSWs")
        print("------------------------------\n")
    tagged_MISC = tag_MISC(MISC_dict, verbose=verbose)
    if verbose:
        print("EXPANDING ALPHABETIC NSWs")
        print("-------------------------\n")
    expanded_ALPHA = expand_all(tagged_ALPHA, text, verbose=verbose, variety=variety, user_abbrevs=user_abbrevs)
    if verbose:
        print("EXPANDING NUMERIC NSWs")
        print("----------------------\n")
    expanded_NUMB = expand_all(tagged_NUMB, text, verbose=verbose, variety=variety, user_abbrevs=user_abbrevs)
    if verbose:
        print("EXPANDING MISCELLANEOUS NSWs")
        print("----------------------------\n")
    expanded_MISC = expand_all(tagged_MISC, text, verbose=verbose, variety=variety, user_abbrevs=user_abbrevs)
    return expanded_ALPHA, expanded_NUMB, expanded_MISC

def parsing_token(guess):
    if not guess:
        return []
    elif guess.isalpha():
        return [guess]
    elif guess[0] in ['(', '[', '{']:
        if guess[-1] in [')', ']', '}']:
            return [guess[0], *parsing_token(guess[1:-1]), guess[-1]]
        else:
            return [guess[0], *parsing_token(guess[1:])]
    elif guess[-1] in [')', ']', '}']:
            return [*parsing_token(guess[:-1]), guess[-1]]
    elif guess[-1] in ['!', '?']:
        return [*parsing_token(guess[:-1]), guess[-1]]
    elif guess[0] in ['"', "'"]:
        if guess[-1] in ['"', "'"]:
            return [guess[0], *parsing_token(guess[1:-1]), guess[-1]]
        else:
            return [guess[0], *parsing_token(guess[1:])]
    elif guess[-1] in ['"', "'"]:
            return [*parsing_token(guess[:-1]), guess[-1]]
    elif guess[-1] == '.' and guess[:-1].isalpha():
        if guess[:-1].lower() in wordlist:
            return [*parsing_token(guess[:-1]), '.']
        elif guess[-1] == '.' and is_digbased(guess[:-1]):
            return [*parsing_token(guess[:-1]), '.']
        else:
            return [guess]
    elif guess.endswith((',', ':', ';')):
        return [*parsing_token(guess[:-1]), guess[-1]]
    return [guess]

def tokenize_basic(text):
    guess = [d for w in text.split(' ') for d in w.split('\n')]
    out = []
    for i in range(len(guess)):
        out.extend(parsing_token(guess[i]))
    return out


def normalise(text, tokenizer=tokenize_basic, verbose=True, variety='BrE', user_abbrevs={}):
    if type(text) == str:
        if tokenizer == tokenize_basic and verbose:
            print("NOTE: using basic tokenizer.\n"
                  "For better results, input tokenized text,"
                  " or use a custom tokenizer")
            return insert(tokenizer(text), verbose=verbose, variety=variety, user_abbrevs=user_abbrevs)
        else:
            return insert(tokenizer(text), verbose=verbose, variety=variety, user_abbrevs=user_abbrevs)
    else:
        return insert(text, verbose=verbose, variety=variety, user_abbrevs=user_abbrevs)


def insert(text, verbose=True, variety='BrE', user_abbrevs={}):
    (expanded_ALPHA,
    expanded_NUMB,
    expanded_MISC) = list_NSWs(text, verbose=verbose, variety=variety, user_abbrevs=user_abbrevs)
    out = text[:]
    split_dict = {}
    for item in (expanded_ALPHA, expanded_NUMB, expanded_MISC):
        for nsw in item.items():
            if isinstance(nsw[0], int):
                out[nsw[0]] = nsw[1][3]
                if nsw[1][2] == 'MONEY' and gen_frame(nsw, text)[3] in bmoney:
                    out[nsw[0] + 1] = ''
            else:
                rind = int(nsw[0])
                if rind in split_dict:
                    split_dict[rind][100 * (nsw[0] - rind)] = nsw[1][3]
                else:
                    split_dict[rind] = {(100 * (nsw[0] - rind)): nsw[1][3]}
                if out[rind] == text[rind]:
                    out[rind] = nsw[1][3]
                else:
                    final = ''
                    for it in sorted(split_dict[rind]):
                        final += ' '
                        final += split_dict[rind][it]
                    final = final[1:]
                    out[rind] = final
    return out


def rejoin(tokenized_text):
    out = ''
    for word in tokenized_text:
        if word:
            out += word
            out += ' '
    return out[:-1]
