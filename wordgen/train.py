import collections

from .model import PREFIX, SUFFIX, LoadedModel


def train(words, n):
    words = set(words)
    token_registry = {}
    transition_weights = []

    for src, dst in extract_ngram_transitions(words, n):
        i = token_registry.get(src)
        j = token_registry.get(dst)

        # Assign index to a token as it appears. A nice side-effect of this
        # strategy is that common tokens tend to get lower index values, so
        # the transition matrix will be automatically clustered by frequency.
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

    return LoadedModel(tokens, transition_weights)


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
