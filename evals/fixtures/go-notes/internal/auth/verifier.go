package auth

import (
	"context"
	"crypto/rsa"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/big"
	"net/http"
	"sync"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type Config struct {
	Issuer   string
	Audience string
	JWKSURL  string
}

type Claims struct {
	jwt.RegisteredClaims
	Email string `json:"email"`
}

// Verifier validates bearer tokens from the identity provider. Keys are
// fetched from the configured JWKS URL only; the token cannot name its own key source.
type Verifier struct {
	cfg    Config
	mu     sync.RWMutex
	keys   map[string]*rsa.PublicKey
	fetched time.Time
	client *http.Client
}

func NewVerifier(ctx context.Context, cfg Config) (*Verifier, error) {
	if cfg.Issuer == "" || cfg.Audience == "" || cfg.JWKSURL == "" {
		return nil, errors.New("auth: issuer, audience and JWKS URL are required")
	}
	v := &Verifier{cfg: cfg, keys: map[string]*rsa.PublicKey{}, client: &http.Client{Timeout: 5 * time.Second}}
	if err := v.refresh(ctx); err != nil {
		return nil, err
	}
	return v, nil
}

func (v *Verifier) Verify(ctx context.Context, raw string) (*Claims, error) {
	claims := &Claims{}
	_, err := jwt.ParseWithClaims(raw, claims, v.keyFunc(ctx),
		jwt.WithValidMethods([]string{"RS256"}),
		jwt.WithIssuer(v.cfg.Issuer),
		jwt.WithAudience(v.cfg.Audience),
		jwt.WithExpirationRequired(),
		jwt.WithLeeway(30*time.Second),
	)
	if err != nil {
		return nil, err
	}
	if claims.Subject == "" {
		return nil, errors.New("auth: token has no subject")
	}
	return claims, nil
}

func (v *Verifier) keyFunc(ctx context.Context) jwt.Keyfunc {
	return func(token *jwt.Token) (any, error) {
		kid, _ := token.Header["kid"].(string)
		if kid == "" {
			return nil, errors.New("auth: missing kid")
		}
		if key := v.lookup(kid); key != nil {
			return key, nil
		}
		// Unknown kid: refresh at most once per minute, then retry the lookup.
		if err := v.refresh(ctx); err != nil {
			return nil, err
		}
		if key := v.lookup(kid); key != nil {
			return key, nil
		}
		return nil, fmt.Errorf("auth: unknown signing key %q", kid)
	}
}

func (v *Verifier) lookup(kid string) *rsa.PublicKey {
	v.mu.RLock()
	defer v.mu.RUnlock()
	return v.keys[kid]
}

type jwks struct {
	Keys []struct {
		Kid string `json:"kid"`
		Kty string `json:"kty"`
		Use string `json:"use"`
		N   string `json:"n"`
		E   string `json:"e"`
	} `json:"keys"`
}

func (v *Verifier) refresh(ctx context.Context) error {
	v.mu.Lock()
	defer v.mu.Unlock()
	if time.Since(v.fetched) < time.Minute && len(v.keys) > 0 {
		return nil
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, v.cfg.JWKSURL, nil)
	if err != nil {
		return err
	}
	res, err := v.client.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return fmt.Errorf("auth: jwks status %d", res.StatusCode)
	}
	var set jwks
	if err := json.NewDecoder(io.LimitReader(res.Body, 1<<20)).Decode(&set); err != nil {
		return err
	}
	keys := map[string]*rsa.PublicKey{}
	for _, k := range set.Keys {
		if k.Kty != "RSA" || (k.Use != "" && k.Use != "sig") {
			continue
		}
		n, err := base64.RawURLEncoding.DecodeString(k.N)
		if err != nil {
			continue
		}
		e, err := base64.RawURLEncoding.DecodeString(k.E)
		if err != nil {
			continue
		}
		keys[k.Kid] = &rsa.PublicKey{N: new(big.Int).SetBytes(n), E: int(new(big.Int).SetBytes(e).Int64())}
	}
	if len(keys) == 0 {
		return errors.New("auth: jwks contained no usable keys")
	}
	v.keys, v.fetched = keys, time.Now()
	return nil
}
