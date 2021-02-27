import json


class Model:
    def __init__(self, store):
        self._store = store
        self._metadata = json.loads(store["metadata"][()])

        self._tokens = [token.decode("ascii") for token in self._store["tokens"]]
        self._transition_rows = self._store["transition_rows"][:]
        self._transition_data = self._store["transition_data"]
        self._start_indices = self._store["start_indices"][:]
        self._start_weights = self._store["start_weights"][:]

    @property
    def tokens(self):
        return self._tokens

    @property
    def prior(self):
        return self._start_indices, self._start_weights

    def posterior(self, i):
        start, end = self._transition_rows[i]
        data = self._transition_data[start:end]
        destinations = data[:, 1]
        weights = data[:, 2]
        return destinations, weights
