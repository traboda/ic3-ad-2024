package models

import (
	"fmt"
	u "supersecurevault/utils"

	"gorm.io/gorm"
)

type Storage struct {
	gorm.Model
	Iname  string `json:"name"`
	IDesc  string `json:"description"`
	IID    string `json:"code"`
	UserId uint   `json:"user_id"`
}

func (storage *Storage) Validate() (map[string]interface{}, bool) {

	if storage.Iname == "" {
		return u.Message(false, "Item name should be on the payload"), false
	}

	if storage.IID == "" {
		return u.Message(false, "Item ID should be on the payload"), false
	}

	if storage.IDesc == "" {
		return u.Message(false, "Description should be on the payload"), false
	}

	if storage.UserId <= 0 {
		return u.Message(false, "User is not recognized"), false
	}

	return u.Message(true, "success"), true
}

func (storage *Storage) Create() map[string]interface{} {

	if resp, ok := storage.Validate(); !ok {
		return resp
	}

	GetDB().Create(storage)

	resp := u.Message(true, "success")
	resp["storage"] = storage
	return resp

}

func GetInventory(id uint) []*Storage {
	storage := make([]*Storage, 0)
	err := GetDB().Table("storages").Where("user_id = ?", id).Find(&storage).Error
	if err != nil {
		fmt.Println(err)
		return nil
	}

	return storage
}

func GetFullInventory(id uint) []*Storage {
	storage := make([]*Storage, 0)
	err := GetDB().Find(&storage).Error
	if err != nil {
		fmt.Println(nil)
		return nil
	}

	return storage

}
