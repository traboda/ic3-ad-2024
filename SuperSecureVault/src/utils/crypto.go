package utils

import (
	"bytes"
	"crypto/aes"
	"crypto/md5"
	"encoding/hex"
	"math/big"
)

const N = aes.BlockSize

func ToInt(b []byte) *big.Int {
	hexStr := hex.EncodeToString(b)
	n := new(big.Int)
	n.SetString(hexStr, 16)
	return n
}

func ToBlock(b *big.Int) []byte {
	hexStr := b.Text(16)

	if len(hexStr)%2 != 0 {
		hexStr = "0" + hexStr
	}

	for len(hexStr) < N*2 {
		hexStr = "0" + hexStr
	}
	result, _ := hex.DecodeString(hexStr)
	return result
}

func Xor(x, y []byte) []byte {
	result := make([]byte, len(x))
	for i := range x {
		result[i] = x[i] ^ y[i]
	}
	return result
}

func ToBlocks(m []byte) [][]byte {
	lenBytes := ToBlock(big.NewInt(int64(len(m))))
	m = append(m, lenBytes...)

	padb := N - len(m)%N
	padding := bytes.Repeat([]byte{byte(padb)}, padb)
	m = append(m, padding...)

	blocks := make([][]byte, len(m)/N)
	for i := range blocks {
		blocks[i] = m[i*N : (i+1)*N]
	}
	return blocks
}

func Rot(n *big.Int, c int) *big.Int {
	bits := 8 * N
	c = c % bits
	mask := new(big.Int).Lsh(big.NewInt(1), uint(c))
	mask.Sub(mask, big.NewInt(1))

	low := new(big.Int).And(n, mask)
	high := new(big.Int).Rsh(n, uint(c))

	low.Lsh(low, uint(bits-c))
	result := new(big.Int).Or(high, low)

	mask = new(big.Int).Lsh(big.NewInt(1), uint(bits))
	mask.Sub(mask, big.NewInt(1))
	return result.And(result, mask)
}

func F(k0 []byte, i int) []byte {
	n := ToInt(k0)
	rotated := Rot(n, i)
	return ToBlock(rotated)
}

func MAC(sid string, m []byte) []byte {
	cfg := GetConfig()
	var k0, k1 = cfg.K0, cfg.K1
	hash := md5.Sum([]byte(sid))
	tKey := Xor(k1, hash[:])
	cipher, _ := aes.NewCipher(tKey)
	blocks := ToBlocks(m)
	result := make([]byte, N)

	for i, block := range blocks {
		tmp := make([]byte, N)
		fk := F(k0, i)
		xored := Xor(block, fk)
		cipher.Encrypt(tmp, xored)
		result = Xor(result, tmp)
	}

	return result
}
