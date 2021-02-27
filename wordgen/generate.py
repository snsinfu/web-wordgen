import random


def generate(model, max_length=64):
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
