import json

import h5py
import wordgen


MAX_COUNT = 100
MAX_PREFIX = 16


class BackendUsageError(Exception):
    pass


class Backend:
    def __init__(self, filename):
        with open(filename) as file:
            config = json.load(file)

        self._store = h5py.File(config["model_store"], "r")
        self._models = {
            name: wordgen.StoredModel(self._store[name])
            for name in config["models"]
        }

    def generate(self, model_name, prefix, count):
        if model_name not in self._models:
            raise BackendUsageError("unrecognized model name")
        if prefix is not None and len(prefix) > MAX_PREFIX:
            raise BackendUsageError("prefix too long")
        if count > MAX_COUNT:
            raise BackendUsageError("count too large")

        model = self._models[model_name]
        for i, word in enumerate(wordgen.generate(model, prefix=prefix)):
            if i >= count:
                break
            yield word
