package controllers

import (
	"log"
	"net/http"
	"supersecurevault/models"
	u "supersecurevault/utils"
)

var CreateAccount = func(w http.ResponseWriter, r *http.Request) {
	err := r.ParseForm()
	account := &models.Account{}
	f := r.Form

	log.Print(f)
	if f["email"] != nil && f["password"] != nil && f["name"] != nil {
		account.Name = string(f["name"][0])
		account.Email = string(f["email"][0])
		account.Password = string(f["password"][0])
		resp := account.Create()

		if resp["status"] != false {
			log.Print("Account Created: -> " + account.Name)
			http.Redirect(w, r, "/login", http.StatusFound)
			return
		} else {
			log.Print(resp["message"])
		}

		u.Respond(w, r, resp)
		return

	}
	if err != nil {
		u.Respond(w, r, u.Message(false, "Error while decoding request body"))
		return
	}
	u.Respond(w, r, u.Message(false, "Something Went Wrong"))

}

var Authenticate = func(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	account := &models.Account{}
	f := r.Form

	if f["email"] != nil && f["password"] != nil {
		account.Email = string(f["email"][0])
		account.Password = string(f["password"][0])
		resp, token := models.Login(account.Email, account.Password)
		http.SetCookie(w, &http.Cookie{
			Name:  "token",
			Value: token})
		w.Header().Add("Authorization", "Basic "+token)
		if resp["status"] != false {
			log.Print("Logged In: -> " + (resp["account"].(*models.Account)).Name)
			http.Redirect(w, r, "/home", http.StatusFound)
		} else {
			log.Print(resp["message"])

		}
		u.Respond(w, r, resp)
		return

	} else {
		u.Respond(w, r, u.Message(false, "Invalid request"))
		return
	}

}
