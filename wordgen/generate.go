package wordgen

import (
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

// Likelihood calculates the likelihood of given sample in a distribution.
// Currently this operation is O(n) where n is the numner of candidates in the
// distribution.
func (distr *Distribution) Likelihood(sample string) float64 {
	for i, cand := range distr.candidates {
		if sample == cand {
			weight := distr.weights[i]
			return float64(weight) / float64(distr.weightSum)
		}
	}
	return 0
}

// SetPrefix fixes the prefix of a generted word.
func (model *Model) SetPrefix(prefix string) error {
	return nil
}

// Generate randomly generates a word-like string.
func (model *Model) Generate(random *rand.Rand) (string, float64) {
	word, startLik := model.prefix.Draw(random)
	logLik := math.Log(startLik)
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

func (model *Model) preparePrefix(random *rand.Rand, prefix string) string {

	maxTail := model.metadata.Ngram
	if maxTail > len(prefix) {
		maxTail = len(prefix)
	}

	for tailSize := maxTail; tailSize > 0; tailSize-- {
		split := len(prefix) - tailSize
		stem := prefix[:split]
		tail := prefix[split:]

		candidates := []string{}

		for valid := range model.transitions {
			valid = strings.TrimPrefix(valid, model.metadata.Prefix)
			if strings.HasPrefix(valid, tail) {
				candidates = append(candidates, stem+valid)
			}
		}

		if len(candidates) != 0 {
			return model.metadata.Prefix + candidates[rand.Intn(len(candidates))]
		}
	}

	panic("FIXME")
}
