package main

import (
	"errors"
	"fmt"
	"math/rand"
	"os"
	"time"

	"github.com/snsinfu/web-wordgen/wordgen"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
	}
}

func run() error {
	if len(os.Args) != 2 && len(os.Args) != 3 {
		return errors.New("specify a model file")
	}

	src, err := os.Open(os.Args[1])
	if err != nil {
		return err
	}
	defer src.Close()

	model, err := wordgen.Load(src)
	if err != nil {
		return err
	}

	random := rand.New(rand.NewSource(time.Now().UnixNano()))
	knownWords := model.KnownWords()

	if len(os.Args) == 3 {
		if err := model.SetPrefix(os.Args[2]); err != nil {
			return err
		}
	}

	for i := 0; i < 100; {
		word, lik := model.Generate(random)

		if _, known := knownWords[word]; known {
			continue
		}

		fmt.Println(word, lik)
		knownWords[word] = true
		i++
	}

	return nil
}