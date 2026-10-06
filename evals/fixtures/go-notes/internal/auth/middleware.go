package auth

import (
	"context"
	"net/http"
	"strings"
)

type ctxKey struct{}

type Principal struct {
	UserID string
	Email  string
}

// Require rejects requests without a valid bearer token and stores the principal in the context.
func Require(v *Verifier) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			header := r.Header.Get("Authorization")
			scheme, raw, ok := strings.Cut(header, " ")
			if !ok || !strings.EqualFold(scheme, "Bearer") || raw == "" {
				w.Header().Set("WWW-Authenticate", `Bearer realm="notes"`)
				http.Error(w, "unauthorized", http.StatusUnauthorized)
				return
			}
			claims, err := v.Verify(r.Context(), raw)
			if err != nil {
				http.Error(w, "unauthorized", http.StatusUnauthorized)
				return
			}
			ctx := context.WithValue(r.Context(), ctxKey{}, Principal{UserID: claims.Subject, Email: claims.Email})
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// From returns the authenticated principal. Handlers behind Require can rely on ok == true.
func From(ctx context.Context) (Principal, bool) {
	p, ok := ctx.Value(ctxKey{}).(Principal)
	return p, ok
}
