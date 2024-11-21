package utils

type Err struct {
	Error string
}

var Er *Err = new(Err)

func GetVar() *Err {
	return Er
}
