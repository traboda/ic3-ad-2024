package models

import (
	"strings"
	u "supersecurevault/utils"

	"github.com/dgrijalva/jwt-go"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

/*
JWT claims struct
*/
type Token struct {
	UserId uint
	jwt.StandardClaims
}

// a struct to rep user account
type Account struct {
	gorm.Model
	Name     string `json:"name"`
	Email    string `json:"email"`
	Password string `json:"password"`
	Token    string `json:"token";sql:"-"`
}

func (account *Account) Validate() (map[string]interface{}, bool) {

	if len(account.Name) == 0 {
		return u.Message(false, "User name is required"), false
	}

	if !strings.Contains(account.Email, "@") {
		return u.Message(false, "Email address is required"), false
	}

	if a := strings.Split(account.Email, "@"); a[len(a)-1] == "inventory.secure" && a[0] != "admin" {
		return u.Message(false, "Sorry You are not a Secure Inventory admin"), false
	}

	if len(account.Password) < 6 {
		return u.Message(false, "Password is required"), false
	}

	var count int64

	result := GetDB().Table("accounts").Where("email = ?", account.Email).Count(&count)
	if result.Error != nil {
		return u.Message(false, "Error Occured during registration"), false

	} else {
		if count > 0 {
			return u.Message(false, "Email address already in use by another user."), false
		} else {
			return u.Message(false, "Requirement passed"), true
		}
	}

}

func (account *Account) Create() map[string]interface{} {

	if resp, ok := account.Validate(); !ok {
		return resp
	}

	hashedPassword, _ := bcrypt.GenerateFromPassword([]byte(account.Password), bcrypt.DefaultCost)
	account.Password = string(hashedPassword)

	GetDB().Create(account)

	if account.ID <= 0 {
		return u.Message(false, "Failed to create account, connection error.")
	}

	tk := &Token{UserId: account.ID}
	token := jwt.NewWithClaims(jwt.GetSigningMethod("HS256"), tk)
	cfg := u.GetConfig()
	jwtPass := cfg.JWTPass
	tokenString, _ := token.SignedString(jwtPass)
	account.Token = tokenString

	account.Password = ""

	response := u.Message(true, "Account has been created")
	response["account"] = account
	return response
}

func Login(email, password string) (map[string]interface{}, string) {

	account := &Account{}
	err := GetDB().Table("accounts").Where("email = ?", email).First(account).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return u.Message(false, "Email address not found"), "Error"
		}
		return u.Message(false, "Connection error. Please retry"), "Error"
	}

	err = bcrypt.CompareHashAndPassword([]byte(account.Password), []byte(password))
	if err != nil && err == bcrypt.ErrMismatchedHashAndPassword {
		return u.Message(false, "Invalid login credentials. Please try again"), "Error"
	}

	account.Password = ""

	tk := &Token{UserId: account.ID}
	token := jwt.NewWithClaims(jwt.GetSigningMethod("HS256"), tk)
	cfg := u.GetConfig()
	jwtPass := cfg.JWTPass
	tokenString, _ := token.SignedString(jwtPass)
	account.Token = tokenString

	resp := u.Message(true, "Logged In")
	resp["account"] = account
	return resp, string(tokenString)
}

func GetUser(u uint) *Account {

	acc := &Account{}
	GetDB().Table("accounts").Where("id = ?", u).First(acc)
	if acc.Email == "" {
		return nil
	}

	acc.Password = ""
	return acc
}
