import re

import h5py
import wordgen


RE_WORD = re.compile(r"\b[a-z]+\b")
DEFAULT_TOKEN_SIZE = 3
DEFAULT_COUNT = 10


def load_words(source):
    doc = source.read()
    doc = doc.lower()
    return set(RE_WORD.findall(doc))


class Train:
    def __init__(self, source, output, group=None, token_size=None):
        self._source = source
        self._token_size = token_size or DEFAULT_TOKEN_SIZE
        self._output = output
        self._group = group or "/"

    def run(self):
        words = load_words(self._source)
        model = wordgen.train(words, self._token_size)

        with h5py.File(self._output, "w") as output:
            store = output.require_group(self._group)
            model.save(store)


class Generate:
    def __init__(self, input, group=None, count=None):
        self._input = input
        self._group = group or "/"
        self._count = count or DEFAULT_COUNT

    def run(self):
        with h5py.File(self._input, "r") as input:
            store = input.require_group(self._group)
            model = wordgen.StoredModel(store)

            generated = 0
            for word in wordgen.generate(model):
                if generated >= self._count:
                    break
                print(word)
                generated += 1
