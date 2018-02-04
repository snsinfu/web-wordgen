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

// POST /requests {model, count}
func (a *Action) PostRequest(c echo.Context) error {
	model := c.FormValue("model")
	prefix := strings.ToLower(c.FormValue("prefix"))

	count, err := strconv.Atoi(c.FormValue("count"))
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
