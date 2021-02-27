import collections
import json
import re

import h5py
import numpy as np

from wordgen import Model


RE_WORD = re.compile(r"\b[a-z]+\b")
PREFIX = "("
SUFFIX = ")"


class Main:
    def __init__(self, source, output, output_group=None, ngram=None):
        self._source = source
        self._ngram = ngram or 3
        self._output_file = h5py.File(output, "w")
        self._output_root = self._output_file.require_group(output_group or "/")


    def __del__(self):
        del self._output_file
        del self._output_root


    def run(self):
        words = load_words(self._source)
        tokens, transition_weights = compute_transition_matrix(words, self._ngram)
        start_indices, start_weights = compute_start_distribution(tokens, transition_weights)

        self._save_metadata()
        self._save_start_weights(start_indices, start_weights)
        self._save_transition_weights(tokens, transition_weights)


    def _save_metadata(self):
        metadata = {
            "prefix": PREFIX,
            "suffix": SUFFIX,
            "ngram": self._ngram,
        }
        self._output_root.create_dataset(
            "metadata",
            data=json.dumps(metadata),
        )


    def _save_start_weights(self, indices, weights):
        self._output_root.create_dataset(
            "start_indices",
            data=np.array(indices, dtype=np.int32),
            scaleoffset=0,
            compression=1,
        )
        self._output_root.create_dataset(
            "start_weights",
            data=np.array(weights, dtype=np.int32),
            scaleoffset=0,
            compression=1,
        )


    def _save_transition_weights(self, tokens, weights_list):
        # Save as a sparse matrix in a flattened LIL format.
        rows = []
        data = []
        for i, weights in enumerate(weights_list):
            start = len(data)
            end = start + len(weights)
            for j, weight in weights.items():
                data.append((i, j, weight))
            rows.append((start, end))

        self._output_root.create_dataset(
            "tokens",
            data=np.array(tokens, dtype=f"S{self._ngram}"),
            compression=True,
        )
        self._output_root.create_dataset(
            "transition_rows",
            data=np.array(rows, dtype=np.int32),
            chunks=(4096, 2),
            scaleoffset=0,
            compression=1,
        )
        self._output_root.create_dataset(
            "transition_data",
            data=np.array(data, dtype=np.int32),
            chunks=(4096, 3),
            scaleoffset=0,
            compression=1,
        )


def load_words(source):
    doc = source.read()
    doc = doc.lower()
    return set(RE_WORD.findall(doc))


def compute_transition_matrix(words, n):
    token_registry = {}
    transition_weights = []

    for src, dst in extract_ngram_transitions(words, n):
        i = token_registry.get(src)
        j = token_registry.get(dst)

        # Allocate index to a token as it appears. A nice side-effect of
        # this strategy is that common tokens tend to get lower index values,
        # so the transition matrix will be automatically clustered by frequency.
        if i is None:
            i = token_registry[src] = len(token_registry)
            transition_weights.append(collections.Counter())

        if j is None:
            j = token_registry[dst] = len(token_registry)
            transition_weights.append(collections.Counter())

        transition_weights[i][j] += 1

    # dict is ordered by insertion order, so this gives a list of tokens
    # ordered by indices.
    tokens = list(token_registry)

    return tokens, transition_weights


def compute_start_distribution(tokens, transition_weights):
    start_indices = []
    start_weights = []

    for i, token in enumerate(tokens):
        if token.startswith(PREFIX):
            start_indices.append(i)
            start_weights.append(sum(transition_weights[i].values()))

    return start_indices, start_weights


def extract_ngram_transitions(words, n):
    for word in words:
        word = PREFIX + word + SUFFIX
        tokens = extract_ngram_tokens(word, n)
        yield from adjacent_pairs(tokens)


def extract_ngram_tokens(word, n):
    for i in range(len(word) - n + 1):
        yield word[i:(i + n)]


def adjacent_pairs(seq):
    it = iter(seq)

    for prev in it:
        break

    for curr in it:
        yield prev, curr
        prev = curr
