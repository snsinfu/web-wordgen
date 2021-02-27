import json
import numpy as np


PREFIX = "("
SUFFIX = ")"


def compute_initial_prior(tokens, transition_weights):
    states = []
    weights = []
    for i, token in enumerate(tokens):
        if token.startswith(PREFIX):
            states.append(i)
            weights.append(sum(transition_weights[i].values()))
    return states, weights


class LoadedModel:
    def __init__(self, tokens, transition_weights):
        self._tokens = tokens
        self._token_size = len(tokens[0])

        initial_states, initial_weights = compute_initial_prior(
            tokens, transition_weights
        )
        self._initial_states = initial_states
        self._initial_weights = initial_weights

        self._transition_destinations = [
            list(transition.keys()) for transition in transition_weights
        ]
        self._transition_weights = [
            list(transition.values()) for transition in transition_weights
        ]

    @property
    def token_size(self):
        return self._token_size

    @property
    def tokens(self):
        return self._tokens

    @property
    def initial_prior(self):
        return self._initial_states, self._initial_weights

    def posterior(self, i):
        return self._transition_destinations[i], self._transition_weights[i]

    def save(self, store):
        self._save_metadata(store)
        self._save_initial_prior(store)
        self._save_posterior(store)

    def _save_metadata(self, store):
        metadata = {
            "prefix": PREFIX,
            "suffix": SUFFIX,
            "token_size": self._token_size,
        }
        store.create_dataset(
            "metadata",
            data=json.dumps(metadata),
        )

    def _save_initial_prior(self, store):
        # Save as a sparse vector.
        data = list(zip(self._initial_states, self._initial_weights))

        store.create_dataset(
            "initial_prior_data",
            data=np.array(data, dtype=np.int32),
            scaleoffset=0,
            compression=1,
        )

    def _save_posterior(self, store):
        # Save as a sparse matrix in a flattened LIL format.
        rows = []
        data = []
        for i in range(len(self._tokens)):
            destinations, weights = self.posterior(i)
            start = len(data)
            end = start + len(destinations)
            for j, weight in zip(destinations, weights):
                data.append((j, weight))
            rows.append((start, end))

        store.create_dataset(
            "tokens",
            data=np.array(self._tokens, dtype=f"S{self._token_size}"),
            compression=True,
        )
        store.create_dataset(
            "transition_rows",
            data=np.array(rows, dtype=np.int32),
            chunks=(4096, 2),
            scaleoffset=0,
            compression=1,
        )
        store.create_dataset(
            "transition_data",
            data=np.array(data, dtype=np.int32),
            chunks=(4096, 2),
            scaleoffset=0,
            compression=1,
        )


class StoredModel:
    def __init__(self, store):
        self._store = store
        self._metadata = json.loads(store["metadata"][()])
        self._token_size = self._metadata["token_size"]

        self._tokens = [token.decode("ascii") for token in self._store["tokens"]]
        self._transition_rows = self._store["transition_rows"][:]
        self._transition_data = self._store["transition_data"]

        initial_prior_data = self._store["initial_prior_data"]
        self._initial_states = initial_prior_data[:, 0]
        self._initial_weights = initial_prior_data[:, 1]

    @property
    def token_size(self):
        return self._token_size

    @property
    def tokens(self):
        return self._tokens

    @property
    def prior(self):
        return self._initial_states, self._initial_weights

    def posterior(self, i):
        start, end = self._transition_rows[i]
        data = self._transition_data[start:end]
        destinations = data[:, 0]
        weights = data[:, 1]
        return destinations, weights
