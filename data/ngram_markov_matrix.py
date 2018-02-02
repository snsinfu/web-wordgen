# Copyright (c) 2018 snsinfu
# This code is released under the MIT License.

import argparse
import collections
import json
import re
import signal
import sys

WORD_REGEX = r'\b[a-z]+\b'
PREFIX = '('
SUFFIX = ')'


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    Main(**parse_args()).run()


def parse_args():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument

    arg('-n', dest='n', type=int, default=3)
    arg('-b', dest='backward', action='store_true', default=False)
    arg('src', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
    arg('dest', type=argparse.FileType('w'), nargs='?', default=sys.stdout)

    return vars(parser.parse_args())


class Main:
    def __init__(self, src, dest, n, backward):
        self._src = src
        self._dest = dest
        self._n = n
        self._backward = backward

    def run(self):
        doc = self._load_document()
        words = re.findall(WORD_REGEX, doc)
        pair_counts = self._count_pairs(words)
        self._output(pair_counts)

    def _load_document(self):
        doc = self._src.read()
        return doc.lower()

    def _count_pairs(self, words):
        pair_counts = {}

        for ngram, succ in generate_ngram_pairs(words, self._n, self._backward):
            if ngram not in pair_counts:
                pair_counts[ngram] = collections.Counter()
            pair_counts[ngram].update(succ)

        return pair_counts

    def _output(self, pair_counts):
        start_distr = self._build_start_distribution(pair_counts)
        transition_table = self._build_transition_table(pair_counts)

        output_bundle = {
            'metadata': {
                'prefix': PREFIX,
                'suffix': SUFFIX,
                'ngram': self._n,
                'backward': self._backward
            },
            'data': {
                'start': start_distr,
                'transitions': transition_table
            }
        }
        json.dump(output_bundle, self._dest, separators=(',', ':'))

    def _build_start_distribution(self, pair_counts):
        if self._backward:
            def is_start(ngram):
                return ngram.endswith(SUFFIX)
        else:
            def is_start(ngram):
                return ngram.startswith(PREFIX)

        start_distr = {}

        for ngram, counts in pair_counts.items():
            if is_start(ngram):
                start_distr[ngram] = sum(counts.values())

        return build_distribution(start_distr)

    def _build_transition_table(self, pair_counts):
        transition_table = {}

        for key, succ_counts in pair_counts.items():
            transition_table[key] = build_distribution(succ_counts)

        return transition_table


def generate_ngram_pairs(words, n, backward):
    for word in words:
        word = PREFIX + word + SUFFIX
        ngrams = generate_ngrams(word, n)

        for pred, succ in generate_pairs(ngrams):
            if backward:
                yield succ, pred[0]
            else:
                yield pred, succ[-1]


def generate_ngrams(word, n):
    for i in range(len(word) - n + 1):
        yield word[i:(i + n)]


def generate_pairs(seq):
    it = iter(seq)

    for prev in it:
        break

    for curr in it:
        yield prev, curr
        prev = curr


def build_distribution(count_dict):
    # Sort in the decreasing order
    distr = collections.Counter(count_dict).most_common()
    candidates, weights = transpose(distr)
    return {'c': candidates, 'w': weights}


def transpose(lists):
    return list(zip(*lists))


if __name__ == '__main__':
    main()
