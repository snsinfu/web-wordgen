package wordgen

import (
	"errors"
	"math"
	"math/rand"
	"strings"
)

// Draw randomly draws a string from a distribution.
func (distr *Distribution) Draw(random *rand.Rand) (string, float64) {
	part := random.Intn(distr.weightSum)
	for i, weight := range distr.weights {
		part -= weight
		if part <= 0 {
			likelihood := float64(weight) / float64(distr.weightSum)
			return distr.candidates[i], likelihood
		}
	}
	panic("invalid distribution")
}

// SetPrefix fixes the prefix of a generted word.
func (model *Model) SetPrefix(prefix string) error {
	// Basically, we use the ending n-gram of specified prefix as the initial
	// state of a Markov chain. Here, we need to deal with these edge cases:
	//
	// - The prefix is shorter than n characters.
	// - The ending n-gram did not appear in training data (unknown n-gram).
	//
	// We deal with the issues by capping the end of the prefix with known
	// n-grams. The result is a distribution of capped prefixes.

	prefix = model.metadata.Prefix + prefix

	cutpos := len(prefix) - model.metadata.Ngram
	if cutpos < 0 {
		cutpos = 0
	}

	for ; cutpos < len(prefix); cutpos++ {
		prefixStem := prefix[:cutpos]
		prefixEnd := prefix[cutpos:]

		candidates := []string{}
		counts := []int{}

		for ngram, distr := range model.transitions {
			if strings.HasPrefix(ngram, prefixEnd) {
				candidates = append(candidates, prefixStem+ngram)
				counts = append(counts, distr.weightSum)
			}
		}

		if len(candidates) > 0 {
			model.prefix, _ = makeDistribution(Histogram{
				Candidates: candidates,
				Counts:     counts,
			})
			return nil
		}
	}

	return errors.New("prefix not recognizable")
}

// Generate randomly generates a word-like string. Returns a generated word and
// the likelihood of the word.
func (model *Model) Generate(random *rand.Rand) (string, float64) {
	word, lik := model.prefix.Draw(random)
	logLik := math.Log(lik)
	steps := 0

	for !strings.HasSuffix(word, model.metadata.Suffix) {
		tail := len(word) - model.metadata.Ngram
		distr := model.transitions[word[tail:]]
		nextChar, lik := distr.Draw(random)

		word += nextChar
		logLik += math.Log(lik)

		steps++
	}

	word = strings.TrimPrefix(word, model.metadata.Prefix)
	word = strings.TrimSuffix(word, model.metadata.Suffix)

	meanLik := math.Exp(logLik / float64(steps))

	return word, meanLik
}
