package main

import (
	"net/http"
	"strconv"
	"strings"

	"github.com/labstack/echo"
)

type Action struct {
	domain *Domain
}

func NewAction(domain *Domain) *Action {
	return &Action{domain}
}

// GET /words {model, prefix, count}
func (a *Action) GetWords(c echo.Context) error {
	model := c.QueryParam("model")
	prefix := strings.ToLower(c.QueryParam("prefix"))

	count, err := strconv.Atoi(c.QueryParam("count"))
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": err.Error(),
		})
	}

	words, err := a.domain.RequestWords(model, prefix, count)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"error": nil,
		"words": words,
	})
}
