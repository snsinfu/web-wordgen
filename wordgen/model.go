package wordgen

import (
	"encoding/json"
	"errors"
	"io"
	"io/ioutil"
)

// Metadata stores model hyper parameters.
type Metadata struct {
	Prefix   string `json:"prefix"`
	Suffix   string `json:"suffix"`
	Ngram    int    `json:"ngram"`
	Backward bool   `json:"backward"`
}

// Histogram represents a histogram of one or more strings.
type Histogram struct {
	Candidates []string `json:"c"`
	Counts     []int    `json:"w"`
}

// Data stores model parameters.
type Data struct {
	Start       Histogram            `json:"start"`
	Transitions map[string]Histogram `json:"transitions"`
	TrainWords  []string             `json:"words"`
}

// ModelConfig stores metadata and data.
type ModelConfig struct {
	Metadata Metadata `json:"metadata"`
	Data     Data     `json:"data"`
}

// Distribution is a discrete distribution of one or more strings.
type Distribution struct {
	candidates []string
	weights    []int
	weightSum  int
}

// Model is an n-gram based generative word model.
type Model struct {
	metadata    Metadata
	start       Distribution
	prefix      Distribution
	transitions map[string]Distribution
	knownWords  map[string]bool
}

// Load constructs a word model from JSON.
func Load(src io.Reader) (*Model, error) {
	data, err := ioutil.ReadAll(src)
	if err != nil {
		return nil, err
	}

	var config ModelConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, err
	}

	return New(config)
}

// New creates a word model from ModelConfig.
func New(config ModelConfig) (*Model, error) {
	start, err := makeDistribution(config.Data.Start)
	if err != nil {
		return nil, err
	}

	transitions := map[string]Distribution{}
	for pred, hist := range config.Data.Transitions {
		distr, err := makeDistribution(hist)
		if err != nil {
			return nil, err
		}
		transitions[pred] = distr
	}

	knownWords := map[string]bool{}
	for _, word := range config.Data.TrainWords {
		knownWords[word] = true
	}

	model := Model{
		metadata:    config.Metadata,
		start:       start,
		prefix:      start,
		transitions: transitions,
		knownWords:  knownWords,
	}
	return &model, nil
}

func makeDistribution(hist Histogram) (Distribution, error) {
	distr := Distribution{}

	if len(hist.Candidates) != len(hist.Counts) {
		return distr, errors.New("histogram data lengths mismatch")
	}
	distr.candidates = hist.Candidates
	distr.weights = hist.Counts

	for _, w := range distr.weights {
		distr.weightSum += w
	}

	if distr.weightSum <= 0 {
		return distr, errors.New("invalid weight")
	}

	return distr, nil
}

// KnownWords returns a set of known words as a map.
func (model *Model) KnownWords() map[string]bool {
	return model.knownWords
}

// Copy creates a copy of existing model.
func (model *Model) Copy() *Model {
	copyModel := *model
	return &copyModel
}
