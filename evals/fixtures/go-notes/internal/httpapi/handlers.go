package httpapi

import (
	"bytes"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"mime"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/go-chi/chi/v5"
	"golang.org/x/time/rate"

	"example.com/notes/internal/auth"
	"example.com/notes/internal/notes"
	"example.com/notes/internal/storage"
)

const (
	maxJSONBody    = 1 << 20  // 1 MiB
	maxAttachment  = 20 << 20 // 20 MiB
	webhookMaxSkew = 5 * time.Minute
)

type handlers struct {
	repo          *notes.Repo
	files         *storage.Files
	webhookSecret []byte
	webOrigin     string

	seenMu      sync.Mutex
	seenIDs     map[string]time.Time
	feedRate    *rate.Limiter
	shareRate   *rate.Limiter
	renderSlots chan struct{}
}

type noteInput struct {
	Title        string `json:"title"`
	BodyMarkdown string `json:"bodyMarkdown"`
}

func (in noteInput) validate() error {
	if l := len(in.Title); l == 0 || l > 200 {
		return errors.New("title must be 1-200 characters")
	}
	if len(in.BodyMarkdown) > 200_000 {
		return errors.New("body too large")
	}
	return nil
}

func decodeJSON(w http.ResponseWriter, r *http.Request, dst any) bool {
	r.Body = http.MaxBytesReader(w, r.Body, maxJSONBody)
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	if err := dec.Decode(dst); err != nil {
		http.Error(w, "invalid JSON body", http.StatusBadRequest)
		return false
	}
	return true
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func notFoundOr500(w http.ResponseWriter, err error) {
	if errors.Is(err, notes.ErrNotFound) {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	http.Error(w, "internal error", http.StatusInternalServerError)
}

func (h *handlers) me(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	writeJSON(w, http.StatusOK, map[string]string{"id": p.UserID, "email": p.Email})
}

func (h *handlers) listNotes(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	list, err := h.repo.List(r.Context(), p.UserID, r.URL.Query().Get("sort"), limit)
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	writeJSON(w, http.StatusOK, list)
}

func (h *handlers) createNote(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	var in noteInput
	if !decodeJSON(w, r, &in) {
		return
	}
	if err := in.validate(); err != nil {
		http.Error(w, err.Error(), http.StatusUnprocessableEntity)
		return
	}
	n, err := h.repo.Create(r.Context(), p.UserID, in.Title, in.BodyMarkdown)
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, n)
}

func (h *handlers) getNote(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	n, err := h.repo.Get(r.Context(), p.UserID, chi.URLParam(r, "noteID"))
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	writeJSON(w, http.StatusOK, n)
}

func (h *handlers) updateNote(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	var in noteInput
	if !decodeJSON(w, r, &in) {
		return
	}
	if err := in.validate(); err != nil {
		http.Error(w, err.Error(), http.StatusUnprocessableEntity)
		return
	}
	n, err := h.repo.Update(r.Context(), p.UserID, chi.URLParam(r, "noteID"), in.Title, in.BodyMarkdown)
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	writeJSON(w, http.StatusOK, n)
}

func (h *handlers) deleteNote(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	stored, err := h.repo.Delete(r.Context(), p.UserID, chi.URLParam(r, "noteID"))
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	for _, name := range stored {
		_ = h.files.Remove(name)
	}
	w.WriteHeader(http.StatusNoContent)
}

func (h *handlers) enableShare(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	buf := make([]byte, 16)
	if _, err := rand.Read(buf); err != nil {
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	slug := hex.EncodeToString(buf)
	if err := h.repo.SetShareSlug(r.Context(), p.UserID, chi.URLParam(r, "noteID"), &slug); err != nil {
		notFoundOr500(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"url": h.webOrigin + "/s/" + slug})
}

func (h *handlers) disableShare(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	if err := h.repo.SetShareSlug(r.Context(), p.UserID, chi.URLParam(r, "noteID"), nil); err != nil {
		notFoundOr500(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

var allowedAttachmentTypes = map[string]bool{
	"image/png": true, "image/jpeg": true, "image/gif": true, "application/pdf": true, "text/plain": true,
}

func (h *handlers) uploadAttachment(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	noteID := chi.URLParam(r, "noteID")
	// Ownership first, before any bytes reach disk.
	if _, err := h.repo.Get(r.Context(), p.UserID, noteID); err != nil {
		notFoundOr500(w, err)
		return
	}
	r.Body = http.MaxBytesReader(w, r.Body, maxAttachment+4096)
	if err := r.ParseMultipartForm(1 << 20); err != nil {
		http.Error(w, "invalid upload", http.StatusBadRequest)
		return
	}
	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "file is required", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Sniff the content; the declared Content-Type and the extension are not trusted.
	head := make([]byte, 512)
	n, _ := io.ReadFull(file, head)
	contentType, _, _ := mime.ParseMediaType(http.DetectContentType(head[:n]))
	if !allowedAttachmentTypes[contentType] {
		http.Error(w, "unsupported file type", http.StatusUnsupportedMediaType)
		return
	}
	stored, size, err := h.files.Put(io.MultiReader(bytes.NewReader(head[:n]), file), maxAttachment)
	if errors.Is(err, storage.ErrTooLarge) {
		http.Error(w, "attachment too large", http.StatusRequestEntityTooLarge)
		return
	}
	if err != nil {
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	display := header.Filename
	if len(display) > 120 {
		display = display[:120]
	}
	a, err := h.repo.AddAttachment(r.Context(), p.UserID, notes.Attachment{
		NoteID: noteID, StoredName: stored, DisplayName: display, ContentType: contentType, Size: size,
	})
	if err != nil {
		_ = h.files.Remove(stored)
		notFoundOr500(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, a)
}

func (h *handlers) downloadAttachment(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	a, err := h.repo.GetAttachment(r.Context(), p.UserID, chi.URLParam(r, "noteID"), chi.URLParam(r, "attachmentID"))
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	f, err := h.files.Open(a.StoredName)
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	defer f.Close()
	w.Header().Set("Content-Type", a.ContentType)
	w.Header().Set("Content-Disposition", mime.FormatMediaType("attachment", map[string]string{"filename": a.DisplayName}))
	http.ServeContent(w, r, "", time.Time{}, f)
}

func (h *handlers) deleteAttachment(w http.ResponseWriter, r *http.Request) {
	p, _ := auth.From(r.Context())
	a, err := h.repo.DeleteAttachment(r.Context(), p.UserID, chi.URLParam(r, "noteID"), chi.URLParam(r, "attachmentID"))
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	_ = h.files.Remove(a.StoredName)
	w.WriteHeader(http.StatusNoContent)
}

// sharedPage renders a public note. Markdown is converted and sanitized in
// notes.RenderHTML. Rendering spawns a process, so the public route is
// rate-limited and the number of concurrent renders is capped.
func (h *handlers) sharedPage(w http.ResponseWriter, r *http.Request) {
	slug := chi.URLParam(r, "slug")
	if len(slug) != 32 {
		http.NotFound(w, r)
		return
	}
	if !h.shareRate.Allow() {
		http.Error(w, "slow down", http.StatusTooManyRequests)
		return
	}
	n, err := h.repo.GetShared(r.Context(), slug)
	if err != nil {
		notFoundOr500(w, err)
		return
	}
	select {
	case h.renderSlots <- struct{}{}:
		defer func() { <-h.renderSlots }()
	case <-r.Context().Done():
		return
	}
	body, err := notes.RenderHTML(r.Context(), n.BodyMD)
	if err != nil {
		http.Error(w, "render failed", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	_ = notes.SharedPage().Execute(w, notes.SharedView{Title: n.Title, Body: body})
}

// publicFeed lists the most recently shared notes' titles and links. No user data beyond that.
func (h *handlers) publicFeed(w http.ResponseWriter, r *http.Request) {
	if !h.feedRate.Allow() {
		http.Error(w, "slow down", http.StatusTooManyRequests)
		return
	}
	w.Header().Set("Cache-Control", "public, max-age=60")
	writeJSON(w, http.StatusOK, map[string]any{"items": []any{}, "generatedAt": time.Now().UTC()})
}

// loginReturn is where the identity provider sends the browser after login. The
// `next` value is a path chosen before the redirect; anything that is not a local
// path on this origin falls back to the app root.
func (h *handlers) loginReturn(w http.ResponseWriter, r *http.Request) {
	target := safeLocalPath(r.URL.Query().Get("next"))
	http.Redirect(w, r, h.webOrigin+target, http.StatusSeeOther)
}

func safeLocalPath(next string) string {
	if next == "" {
		return "/"
	}
	u, err := url.Parse(next)
	if err != nil || u.IsAbs() || u.Host != "" || u.User != nil {
		return "/"
	}
	path := u.EscapedPath()
	if !strings.HasPrefix(path, "/") || strings.HasPrefix(path, "//") || strings.ContainsAny(path, "\\\r\n") {
		return "/"
	}
	if u.RawQuery != "" {
		path += "?" + u.RawQuery
	}
	return path
}

type idpEvent struct {
	ID      string `json:"id"`
	Type    string `json:"type"`
	UserID  string `json:"userId"`
	Issued  int64  `json:"issuedAt"`
}

// idpWebhook receives user-deleted events. Signature = hex(HMAC-SHA256(secret, timestamp + "." + body)).
func (h *handlers) idpWebhook(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(http.MaxBytesReader(w, r.Body, maxJSONBody))
	if err != nil {
		http.Error(w, "body too large", http.StatusRequestEntityTooLarge)
		return
	}
	ts := r.Header.Get("X-Idp-Timestamp")
	sent, err := strconv.ParseInt(ts, 10, 64)
	if err != nil || time.Since(time.Unix(sent, 0)).Abs() > webhookMaxSkew {
		http.Error(w, "stale or missing timestamp", http.StatusUnauthorized)
		return
	}
	mac := hmac.New(sha256.New, h.webhookSecret)
	mac.Write([]byte(ts))
	mac.Write([]byte("."))
	mac.Write(body)
	expected := mac.Sum(nil)
	got, err := hex.DecodeString(r.Header.Get("X-Idp-Signature"))
	if err != nil || !hmac.Equal(got, expected) {
		http.Error(w, "bad signature", http.StatusUnauthorized)
		return
	}
	var ev idpEvent
	if err := json.Unmarshal(body, &ev); err != nil || ev.ID == "" {
		http.Error(w, "invalid event", http.StatusBadRequest)
		return
	}
	if !h.markSeen(ev.ID) {
		w.WriteHeader(http.StatusOK) // duplicate delivery; already handled
		return
	}
	if ev.Type == "user.deleted" {
		// Deletion of the user's notes is queued; omitted here.
	}
	w.WriteHeader(http.StatusAccepted)
}

func (h *handlers) markSeen(id string) bool {
	h.seenMu.Lock()
	defer h.seenMu.Unlock()
	now := time.Now()
	for k, t := range h.seenIDs {
		if now.Sub(t) > 2*webhookMaxSkew {
			delete(h.seenIDs, k)
		}
	}
	if _, dup := h.seenIDs[id]; dup {
		return false
	}
	h.seenIDs[id] = now
	return true
}
