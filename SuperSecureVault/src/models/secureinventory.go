package models

import (
	"encoding/hex"
	"fmt"
	"log"
	u "supersecurevault/utils"

	"gorm.io/gorm"
)

type SecureStorage struct {
	gorm.Model
	SID     string `json:"sid"`
	Message string `json:"message"`
	Iname   string `json:"name"`
	IDesc   string `json:"description"`
	IID     string `json:"code"`
	Token   string `json:"token"`
}

func (SecStorage *SecureStorage) Validate() (map[string]interface{}, bool) {

	if SecStorage.SID == "" {
		return u.Message(false, "Secure ID should be on the payload"), false
	}
	if SecStorage.Message == "" {
		return u.Message(false, "Message should be on the payload"), false

	} else if _, ok := hex.DecodeString(SecStorage.Message); ok != nil {
		return u.Message(false, "Message must be hex encoded"), false
	}

	if SecStorage.Iname == "" {
		return u.Message(false, "Item name should be on the payload"), false
	}

	if SecStorage.IID == "" {
		return u.Message(false, "Item ID should be on the payload"), false
	}

	if SecStorage.IDesc == "" {
		return u.Message(false, "Description should be on the payload"), false
	}

	//All the required parameters are present
	return u.Message(true, "success"), true
}

func (SecStorage *SecureStorage) Create() map[string]interface{} {

	if resp, ok := SecStorage.Validate(); !ok {
		return resp
	}
	var count int64

	result := GetDB().Table("secure_storages").Where("s_id = ? AND message = ?", SecStorage.SID, SecStorage.Message).Count(&count)

	if result.Error == nil {
		if count > 0 {
			return u.Message(false, "Record already exists for the given SID and message. Cannot add.")
		} else {
			decMessage, _ := hex.DecodeString(SecStorage.Message)
			token := u.MAC(SecStorage.SID, decMessage)
			hexToken := hex.EncodeToString(token)
			SecStorage.Token = hexToken
			createResult := GetDB().Create(SecStorage)
			if createResult.Error != nil {
				return u.Message(false, "Error adding Item")
			} else {
				log.Println("Record added successfully")
			}
		}

	} else {
		return u.Message(false, "Error adding Item")
	}

	resp := u.Message(true, "success")
	resp["securestorage"] = SecStorage
	return resp

}

func GetSecureInventory(sid, message, token string) map[string]interface{} {

	decMessage, err := hex.DecodeString(message)
	if err != nil {
		return u.Message(false, "Message must be hex encoded")
	}

	genToken := u.MAC(sid, decMessage)
	hexToken := hex.EncodeToString(genToken)

	if hexToken != token {
		return u.Message(false, "MAC verification failed")
	}

	secStorage := &SecureStorage{}
	result := GetDB().Table("secure_storages").Where("s_id = ? AND token = ?", sid, token).Order("created_at ASC").First(secStorage)
	fmt.Println("yay", secStorage.ID)

	if result.Error == nil {

		resp := u.Message(true, "success")
		resp["data"] = secStorage
		return resp

	} else if result.Error == gorm.ErrRecordNotFound {
		return u.Message(false, "Record Not Found")

	} else {
		return u.Message(false, "Error Retriving Item")
	}

}
