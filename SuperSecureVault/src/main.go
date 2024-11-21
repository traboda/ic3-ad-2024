package main

import (
	"fmt"
	"log"
	"net/http"
	"supersecurevault/controllers"
	m "supersecurevault/models"
	"supersecurevault/utils"

	"github.com/gorilla/mux"
)

func main() {

	err := utils.InitConfig("keys.conf")
	if err != nil {
		log.Fatalf("Failed to initialize config: %v", err)
	}
	router := mux.NewRouter()
	router.HandleFunc("/", controllers.IndexPageHandler).Methods("GET")
	router.HandleFunc("/register", controllers.RegisterPageHandler).Methods("GET")
	router.HandleFunc("/login", controllers.LoginPageHandler).Methods("GET")
	router.HandleFunc("/error", controllers.ErrorPageHandler).Methods("GET")
	router.PathPrefix("/styles/").Handler(http.StripPrefix("/styles/",
		http.FileServer(http.Dir("templates/styles/"))))

	router.PathPrefix("/images/").Handler(http.StripPrefix("/images/",
		http.FileServer(http.Dir("templates/images/"))))

	router.Use(m.JwtAuthentication)
	router.HandleFunc("/register", controllers.CreateAccount).Methods("POST")
	router.HandleFunc("/login", controllers.Authenticate).Methods("POST")
	router.HandleFunc("/home", controllers.HomePageHandler).Methods("GET")
	router.HandleFunc("/inventory/addItem", controllers.AddItem).Methods("POST")
	router.HandleFunc("/inventory/view", controllers.GetItems).Methods("GET")
	router.HandleFunc("/inventory/fullinventory", controllers.ViewFullInventory).Methods("GET")
	router.HandleFunc("/view", controllers.GetInventoryPageHandler).Methods("GET")
	router.HandleFunc("/add", controllers.AddItemPageHandler).Methods("GET")
	router.HandleFunc("/fullinventory", controllers.GetfullInventoryPageHandler).Methods("GET")
	router.HandleFunc("/addSecure", controllers.AddSecureItemPageHandler).Methods("GET")
	router.HandleFunc("/viewSecure", controllers.ViewSecureItemPageHandler).Methods("GET")
	router.HandleFunc("/token", controllers.TokenPageHandler).Methods("GET")
	router.HandleFunc("/secureinventory/addItem", controllers.AddSecureItem).Methods("POST")
	router.HandleFunc("/secureinventory/viewItem", controllers.ViewSecureItem).Methods("POST")

	http.Handle("/", router)
	log.Println("Server running on http://localhost:8000")
	err = http.ListenAndServe(":8000", nil)
	if err != nil {
		fmt.Print(err)
	}

}
