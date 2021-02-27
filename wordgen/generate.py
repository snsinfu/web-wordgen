import random

from .model import PREFIX


def generate(model, prefix=None, max_length=64):
    if prefix is None:
        return generate_normal(model, max_length)
    else:
        return generate_with_prefix(model, prefix, max_length)


def generate_normal(model, max_length):
    tokens = model.tokens
    initial_states, initial_weights = model.prior

    while True:
        state, = random.choices(initial_states, initial_weights)
        word = tokens[state]

        while len(word) < max_length + 2:
            destinations, weights = model.posterior(state)
            if len(destinations) == 0:
                break
            state, = random.choices(destinations, weights)
            word += tokens[state][-1]

        # Trim PREFIX and SUFFIX.
        word = word[1:-1]

        yield word


def generate_with_prefix(model, prefix, max_length):
    tokens = model.tokens
    prefix = PREFIX + prefix

    prefix_state = get_prefix_state(model, prefix)
    if prefix_state is None:
        return

    while True:
        state = prefix_state
        word = prefix

        while len(word) < max_length + 2:
            destinations, weights = model.posterior(state)
            if len(destinations) == 0:
                break
            state, = random.choices(destinations, weights)
            word += tokens[state][-1]

        # Trim PREFIX and SUFFIX.
        word = word[1:-1]

        yield word


def get_prefix_state(model, prefix):
    tokens = model.tokens

    if len(prefix) >= model.token_size:
        prefix_token = prefix[-model.token_size:]
        try:
            return tokens.index(prefix_token)
        except ValueError:
            return None

    initial_states, initial_weights = model.prior
    prefix_states = []
    prefix_weights = []
    for state, weight in zip(initial_states, initial_weights):
        if tokens[state].startswith(prefix):
            prefix_states.append(state)
            prefix_weights.append(weight)

    if len(prefix_states) == 0:
        return None
    prefix_state, = random.choices(prefix_states, prefix_weights)

    return prefix_state
