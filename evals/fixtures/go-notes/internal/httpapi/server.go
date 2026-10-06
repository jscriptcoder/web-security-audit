package httpapi

import (
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/rs/cors"
	"golang.org/x/time/rate"

	"example.com/notes/internal/auth"
	"example.com/notes/internal/notes"
	"example.com/notes/internal/storage"
)

type Deps struct {
	DB            *pgxpool.Pool
	Verifier      *auth.Verifier
	Files         *storage.Files
	WebOrigin     string
	WebhookSecret []byte
}

func New(d Deps) http.Handler {
	repo := notes.NewRepo(d.DB)
	h := &handlers{
		repo: repo, files: d.Files, webhookSecret: d.WebhookSecret, webOrigin: d.WebOrigin,
		seenIDs:     map[string]time.Time{},
		feedRate:    rate.NewLimiter(rate.Every(100*time.Millisecond), 20),
		shareRate:   rate.NewLimiter(rate.Every(50*time.Millisecond), 40),
		renderSlots: make(chan struct{}, 4),
	}

	r := chi.NewRouter()
	// The load balancer strips client-supplied True-Client-IP, X-Real-IP and
	// X-Forwarded-For and sets its own before the request reaches the pod; the
	// resolved address is only written to the access log. No limit or
	// authorization decision reads it.
	r.Use(middleware.RealIP)
	r.Use(middleware.RequestID)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(60 * time.Second))
	r.Use(securityHeaders)

	// Authenticated API: credentials are a bearer header set by the SPA, never a cookie.
	r.Group(func(r chi.Router) {
		r.Use(cors.New(cors.Options{
			AllowedOrigins:   []string{d.WebOrigin},
			AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE"},
			AllowedHeaders:   []string{"Authorization", "Content-Type"},
			AllowCredentials: false,
			MaxAge:           600,
		}).Handler)
		r.Use(auth.Require(d.Verifier))

		r.Route("/api/notes", func(r chi.Router) {
			r.Get("/", h.listNotes)
			r.Post("/", h.createNote)
			r.Route("/{noteID}", func(r chi.Router) {
				r.Get("/", h.getNote)
				r.Put("/", h.updateNote)
				r.Delete("/", h.deleteNote)
				r.Post("/share", h.enableShare)
				r.Delete("/share", h.disableShare)
				r.Post("/attachments", h.uploadAttachment)
				r.Get("/attachments/{attachmentID}", h.downloadAttachment)
				r.Delete("/attachments/{attachmentID}", h.deleteAttachment)
			})
		})
		r.Get("/api/me", h.me)
	})

	// Public, read-only surfaces.
	r.Group(func(r chi.Router) {
		r.Use(cors.New(cors.Options{AllowedOrigins: []string{"*"}, AllowedMethods: []string{"GET"}}).Handler)
		r.Get("/public/feed.json", h.publicFeed)
	})
	r.Get("/s/{slug}", h.sharedPage)
	r.Get("/login/return", h.loginReturn)

	// Identity-provider webhook: HMAC over the raw body, constant-time compared, with a replay window.
	r.Post("/webhooks/idp", h.idpWebhook)

	r.Get("/healthz", func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(http.StatusNoContent) })
	return r
}

func securityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		h := w.Header()
		h.Set("X-Content-Type-Options", "nosniff")
		h.Set("Referrer-Policy", "no-referrer")
		h.Set("Content-Security-Policy", "default-src 'none'; img-src 'self' data:; style-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
		h.Set("Cache-Control", "no-store")
		h.Set("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
		next.ServeHTTP(w, r)
	})
}
