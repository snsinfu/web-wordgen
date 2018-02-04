package main

import (
	"errors"
	"math/rand"
	"os"
	"time"

	"github.com/snsinfu/web-wordgen/wordgen"
)

type DomainConfig struct {
	Models   map[string]string
	MaxRetry int
}

type Domain struct {
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

	seed := time.Now().UnixNano()
	random := rand.New(rand.NewSource(seed))
	words := []Word{}

	for len(words) < count && retry >= 0 {
		word, likelihood := model.Generate(random)

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
