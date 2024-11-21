package models

import (
	"context"
	"log"
	"net/http"
	"strings"
	u "supersecurevault/utils"

	jwt "github.com/dgrijalva/jwt-go"
)

var JwtAuthentication = func(next http.Handler) http.Handler {

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		notAuth := []string{"/register", "/login", "/", "/styles/style.css", "/styles/font.woff2", "/images/logo.png", "/error"}
		requestPath := r.URL.Path

		for _, value := range notAuth {

			if value == requestPath {
				next.ServeHTTP(w, r)
				return
			}
		}
		log.Print("REQUEST : ", requestPath)
		var co int = 0
		var tokenPart string

		response := make(map[string]interface{})

		tokenHeader := r.Header.Get("Authorization")

		if cookie, err := r.Cookie("token"); err == nil {
			tokenHeader = string(cookie.Value)
			co = 1
		} else {
			log.Print(err)
		}

		if tokenHeader == "" {
			response = u.Message(false, "Missing auth token")
			w.WriteHeader(http.StatusForbidden)
			w.Header().Add("Content-Type", "application/json")
			u.Respond(w, r, response)
			return
		}

		if co == 1 {
			tokenPart = tokenHeader

		} else {

			splitted := strings.Split(tokenHeader, " ")
			if len(splitted) != 2 {
				response = u.Message(false, "Invalid/Malformed auth token")
				w.WriteHeader(http.StatusForbidden)
				w.Header().Add("Content-Type", "application/json")
				u.Respond(w, r, response)
				return
			}

			tokenPart = splitted[1]
		}
		tk := &Token{}

		token, err := jwt.ParseWithClaims(tokenPart, tk, func(token *jwt.Token) (interface{}, error) {
			cfg := u.GetConfig()
			jwtPass := cfg.JWTPass
			return jwtPass, nil
		})

		if err != nil {
			response = u.Message(false, "Malformed authentication token")
			w.WriteHeader(http.StatusForbidden)
			w.Header().Add("Content-Type", "application/json")
			u.Respond(w, r, response)
			return
		}

		if !token.Valid {
			response = u.Message(false, "Token is not valid.")
			w.WriteHeader(http.StatusForbidden)
			w.Header().Add("Content-Type", "application/json")
			u.Respond(w, r, response)
			return
		}

		ctx := context.WithValue(r.Context(), "user", tk.UserId)
		r = r.WithContext(ctx)
		next.ServeHTTP(w, r)
	})
}
