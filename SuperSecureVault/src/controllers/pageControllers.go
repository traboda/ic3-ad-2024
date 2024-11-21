package controllers

import (
	"html/template"
	"net/http"
	u "supersecurevault/utils"
)

type TokenData struct {
	Token string
}

var ind = template.Must(template.ParseFiles("templates/index.html"))
var in = template.Must(template.ParseFiles("templates/login.html"))
var getW = template.Must(template.ParseFiles("templates/getInventory.html"))
var getI = template.Must(template.ParseFiles("templates/getfullInventory.html"))
var reg = template.Must(template.ParseFiles("templates/register.html"))
var add = template.Must(template.ParseFiles("templates/addItem.html"))
var er = template.Must(template.ParseFiles("templates/error.html"))
var hom = template.Must(template.ParseFiles("templates/home.html"))
var addSec = template.Must(template.ParseFiles("templates/addSecureItem.html"))
var tok = template.Must(template.ParseFiles("templates/token.html"))
var vsp = template.Must(template.ParseFiles("templates/viewSecureItem.html"))

func LoginPageHandler(w http.ResponseWriter, r *http.Request) {

	if err := in.ExecuteTemplate(w, "login.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func RegisterPageHandler(w http.ResponseWriter, r *http.Request) {

	if err := reg.ExecuteTemplate(w, "register.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

}

func IndexPageHandler(w http.ResponseWriter, r *http.Request) {

	if err := ind.ExecuteTemplate(w, "index.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func HomePageHandler(w http.ResponseWriter, r *http.Request) {

	if err := hom.ExecuteTemplate(w, "home.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func AddItemPageHandler(w http.ResponseWriter, r *http.Request) {

	if err := add.ExecuteTemplate(w, "addItem.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func GetInventoryPageHandler(w http.ResponseWriter, r *http.Request) {

	if err := getW.ExecuteTemplate(w, "getInventory.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func GetfullInventoryPageHandler(w http.ResponseWriter, r *http.Request) {

	if err := getI.ExecuteTemplate(w, "getfullInventory.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func AddSecureItemPageHandler(w http.ResponseWriter, r *http.Request) {

	if err := addSec.ExecuteTemplate(w, "addSecureItem.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}
func ViewSecureItemPageHandler(w http.ResponseWriter, r *http.Request) {

	if err := vsp.ExecuteTemplate(w, "viewSecureItem.html", nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func ErrorPageHandler(w http.ResponseWriter, r *http.Request) {

	erre := u.GetVar()

	if err := er.ExecuteTemplate(w, "error.html", erre); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func TokenPageHandler(w http.ResponseWriter, r *http.Request) {

	err := r.ParseForm()
	if err != nil {
		http.Error(w, "Error parsing form", http.StatusBadRequest)
		return
	}

	token := r.FormValue("token")

	data := TokenData{Token: token}

	if err := tok.ExecuteTemplate(w, "token.html", data); err != nil {
		http.Error(w, "Error executing template", http.StatusInternalServerError)
	}
}
