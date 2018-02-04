package main

import (
	"encoding/json"
	"os"
	"strconv"

	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
)

func main() {
	e := echo.New()

	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Use(middleware.SecureWithConfig(middleware.SecureConfig{
		XSSProtection:      "1; mode=block",
		ContentTypeNosniff: "nosniff",
	}))

	domain, err := makeNewDomain()
	if err != nil {
		e.Logger.Fatal(err)
	}

	action := NewAction(domain)
	e.POST("/words/request", action.PostWordsRequest)

	e.File("/", "index.html")

	e.Logger.Fatal(e.Start(":" + os.Getenv("PORT")))
}

func makeNewDomain() (*Domain, error) {
	seed, err := strconv.ParseInt(os.Getenv("WORDGEN_SEED"), 10, 64)
	if err != nil {
		return nil, err
	}

	models := map[string]string{}
	if err := json.Unmarshal([]byte(os.Getenv("WORDGEN_MODELS")), &models); err != nil {
		return nil, err
	}

	maxRetry, err := strconv.Atoi(os.Getenv("WORDGEN_MAX_RETRY"))
	if err != nil {
		return nil, err
	}

	return NewDomain(DomainConfig{
		Seed:     seed,
		Models:   models,
		MaxRetry: maxRetry,
	})
}
