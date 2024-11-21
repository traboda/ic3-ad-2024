package utils

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
)

func Message(status bool, message string) map[string]interface{} {
	return map[string]interface{}{"status": status, "message": message}
}

func Respond(w http.ResponseWriter, r *http.Request, data map[string]interface{}) {
	if data["status"] == false {
		log.Print(data["message"])
		er := GetVar()
		er.Error = (data["message"]).(string)
		http.Redirect(w, r, "/error", http.StatusFound)
	}

	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

type Config struct {
	K0      []byte
	K1      []byte
	JWTPass []byte
}

var (
	config *Config
	once   sync.Once
)

func GetConfig() *Config {
	return config
}

func InitConfig(filename string) error {
	var err error
	once.Do(func() {
		var cfg *Config
		cfg, err = LoadKeys(filename)
		if err == nil {
			config = cfg
		}
	})
	return err
}

func LoadKeys(filename string) (*Config, error) {

	content, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("error reading config file: %v", err)
	}

	lines := strings.Split(string(content), "\n")
	config := &Config{}

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}

		key := strings.TrimSpace(parts[0])
		value := strings.TrimSpace(parts[1])

		switch key {
		case "K0":
			config.K0 = []byte(value)
		case "K1":
			config.K1 = []byte(value)
		case "JWT_PASS":
			config.JWTPass = []byte(value)
		}
	}

	if len(config.K0) == 0 || len(config.K1) == 0 || len(config.JWTPass) == 0 {
		return nil, fmt.Errorf("missing required keys in config file")
	}

	return config, nil
}
