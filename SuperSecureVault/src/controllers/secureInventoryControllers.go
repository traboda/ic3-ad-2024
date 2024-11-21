package controllers

import (
	"fmt"
	"log"
	"net/http"
	"net/url"
	"supersecurevault/models"
	u "supersecurevault/utils"
)

var AddSecureItem = func(w http.ResponseWriter, r *http.Request) {
	err := r.ParseForm()

	secureStorage := &models.SecureStorage{}
	f := r.Form
	fmt.Print("Over here")
	if f["sid"] != nil && f["message"] != nil && f["name"] != nil && f["code"] != nil && f["description"] != nil {
		secureStorage.SID = string(f["sid"][0])
		secureStorage.Message = string(f["message"][0])

		secureStorage.Iname = string(f["name"][0])
		secureStorage.IDesc = string(f["description"][0])
		secureStorage.IID = string(f["code"][0])
		resp := secureStorage.Create()
		if resp["status"] != false {

			log.Print("Added Item: -> " + secureStorage.Iname)
			http.Redirect(w, r, "/token?token="+url.QueryEscape(secureStorage.Token), http.StatusSeeOther)
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

	u.Respond(w, r, u.Message(false, "Error while decoding request body"))
}

var ViewSecureItem = func(w http.ResponseWriter, r *http.Request) {

	err := r.ParseForm()
	f := r.Form

	if f["sid"] != nil && f["message"] != nil && f["token"] != nil {
		fmt.Println("here")
		sid := string(f["sid"][0])
		message := string(f["message"][0])
		token := string(f["token"][0])

		resp := models.GetSecureInventory(sid, message, token)

		u.Respond(w, r, resp)
		return
	}

	if err != nil {
		u.Respond(w, r, u.Message(false, "Error while decoding request body"))
		return
	}

	u.Respond(w, r, u.Message(false, "Error while decoding request body"))
}
