package models

import (
	"fmt"
	"log"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var db *gorm.DB

func init() {

	username := "secureusername"
	password := "securepassword"
	dbName := "inventory"
	dbHost := "db"

	dbUri := fmt.Sprintf("host=%s user=%s dbname=%s sslmode=disable password=%s", dbHost, username, dbName, password)
	log.Print(dbUri)

	conn, err := gorm.Open(sqlite.Open("./gorm.db"))
	if err != nil {
		log.Print(err)
	} else {

		log.Print("-----DataBase Connection Complete------")
	}

	db = conn
	db.Debug().AutoMigrate(&Account{}, &Storage{}, &SecureStorage{})
}

func GetDB() *gorm.DB {
	return db
}
