package main

import (
	"context"
	"log"
	"net/http"
	_ "net/http/pprof" // registers /debug/pprof on http.DefaultServeMux; served only on the admin listener below
	"os"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"example.com/notes/internal/auth"
	"example.com/notes/internal/httpapi"
	"example.com/notes/internal/storage"
)

func main() {
	ctx := context.Background()

	webhookSecret := os.Getenv("WEBHOOK_SECRET")
	if len(webhookSecret) < 32 {
		log.Fatal("WEBHOOK_SECRET must be set to at least 32 bytes")
	}

	pool, err := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Fatalf("db: %v", err)
	}
	defer pool.Close()

	verifier, err := auth.NewVerifier(ctx, auth.Config{
		Issuer:   os.Getenv("JWT_ISSUER"),
		Audience: os.Getenv("JWT_AUDIENCE"),
		JWKSURL:  os.Getenv("JWKS_URL"),
	})
	if err != nil {
		log.Fatalf("auth: %v", err)
	}

	files, err := storage.OpenFiles(os.Getenv("DATA_DIR"))
	if err != nil {
		log.Fatalf("storage: %v", err)
	}
	defer files.Close()

	api := httpapi.New(httpapi.Deps{
		DB:            pool,
		Verifier:      verifier,
		Files:         files,
		WebOrigin:     os.Getenv("WEB_ORIGIN"),
		WebhookSecret: []byte(webhookSecret),
	})

	// Admin listener: pprof and health on loopback only. Not exposed by the Service.
	go func() {
		admin := &http.Server{Addr: "127.0.0.1:6060", Handler: http.DefaultServeMux, ReadHeaderTimeout: 5 * time.Second}
		log.Println(admin.ListenAndServe())
	}()

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           api,
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      60 * time.Second,
		MaxHeaderBytes:    1 << 16,
	}
	log.Fatal(srv.ListenAndServe())
}
