package main

import (
	"errors"
	"math/rand"
	"os"

	"github.com/snsinfu/web-wordgen/wordgen"
)

type DomainConfig struct {
	Seed     int64
	Models   map[string]string
	MaxRetry int
}

type Domain struct {
	random   *rand.Rand
	models   map[string]*wordgen.Model
	maxRetry int
}

type Word struct {
	Word       string  `json:"w"`
	Likelihood float32 `json:"p"`
}

var (
	ErrNoModel            = errors.New("no such model")
	ErrUnrecognizedPrefix = errors.New("unrecognized prefix")
)

func NewDomain(config DomainConfig) (*Domain, error) {
	random := rand.New(rand.NewSource(config.Seed))

	models := map[string]*wordgen.Model{}
	for name, path := range config.Models {
		src, err := os.Open(path)
		if err != nil {
			return nil, err
		}
		defer src.Close()

		model, err := wordgen.Load(src)
		if err != nil {
			return nil, err
		}
		models[name] = model
	}

	domain := Domain{
		random:   random,
		models:   models,
		maxRetry: config.MaxRetry,
	}
	return &domain, nil
}

func (d *Domain) RequestWords(name, prefix string, count int) ([]Word, error) {
	model, ok := d.models[name]
	if !ok {
		return nil, ErrNoModel
	}

	if len(prefix) > 0 {
		model = model.Copy()
		if err := model.SetPrefix(prefix); err != nil {
			return nil, ErrUnrecognizedPrefix
		}
	}

	knownWords := map[string]bool{}
	for word := range model.KnownWords() {
		knownWords[word] = true
	}
	retry := d.maxRetry

	words := []Word{}

	for len(words) < count && retry >= 0 {
		word, likelihood := model.Generate(d.random)

		if _, known := knownWords[word]; known {
			retry--
			continue
		}
		knownWords[word] = true

		words = append(words, Word{
			Word:       word,
			Likelihood: float32(likelihood),
		})
	}

	return words, nil
}
