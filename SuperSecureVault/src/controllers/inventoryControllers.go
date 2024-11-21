package controllers

import (
	"log"
	"net/http"
	"supersecurevault/models"
	u "supersecurevault/utils"
)

var AddItem = func(w http.ResponseWriter, r *http.Request) {
	err := r.ParseForm()
	user := r.Context().Value("user").(uint)
	log.Print(user)
	storage := &models.Storage{}
	f := r.Form
	if f["name"] != nil && f["code"] != nil && f["description"] != nil {
		storage.Iname = string(f["name"][0])
		storage.IDesc = string(f["description"][0])
		storage.IID = string(f["code"][0])

		storage.UserId = user
		resp := storage.Create()

		if resp["status"] != false {
			log.Print("Added Item: -> " + storage.Iname)
			http.Redirect(w, r, "/add", http.StatusFound)
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

var GetItems = func(w http.ResponseWriter, r *http.Request) {

	user := r.Context().Value("user").(uint)
	data := models.GetInventory(user)

	resp := u.Message(true, "success")
	resp["data"] = data
	u.Respond(w, r, resp)

}

var ViewFullInventory = func(w http.ResponseWriter, r *http.Request) {
	user := r.Context().Value("user").(uint)

	acc := models.GetUser(user)

	if acc == nil {
		u.Respond(w, r, u.Message(false, "Email Not Found"))
		return
	}

	if acc.Email[len(acc.Email)-16:] != "inventory.secure" {

		u.Respond(w, r, u.Message(false, "Sorry You are not a Secure Inventory admin"))
		return

	}

	data := models.GetFullInventory(user)
	resp := u.Message(true, "success")
	resp["data"] = data
	u.Respond(w, r, resp)

}
