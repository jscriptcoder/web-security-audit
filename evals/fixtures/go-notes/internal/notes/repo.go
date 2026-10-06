package notes

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

var ErrNotFound = errors.New("notes: not found")

type Note struct {
	ID        string    `json:"id"`
	OwnerID   string    `json:"ownerId"`
	Title     string    `json:"title"`
	BodyMD    string    `json:"bodyMarkdown"`
	ShareSlug *string   `json:"shareSlug,omitempty"`
	UpdatedAt time.Time `json:"updatedAt"`
}

type Attachment struct {
	ID          string `json:"id"`
	NoteID      string `json:"noteId"`
	StoredName  string `json:"-"`
	DisplayName string `json:"name"`
	ContentType string `json:"contentType"`
	Size        int64  `json:"size"`
}

type Repo struct{ db *pgxpool.Pool }

func NewRepo(db *pgxpool.Pool) *Repo { return &Repo{db: db} }

// Sort columns are mapped through this table; the request value never reaches the SQL text.
var sortColumns = map[string]string{
	"updated": "updated_at DESC",
	"title":   "title ASC",
	"created": "created_at DESC",
}

func (r *Repo) List(ctx context.Context, ownerID, sort string, limit int) ([]Note, error) {
	order, ok := sortColumns[sort]
	if !ok {
		order = sortColumns["updated"]
	}
	if limit <= 0 || limit > 200 {
		limit = 50
	}
	query := fmt.Sprintf(`SELECT id, owner_id, title, body_md, share_slug, updated_at
		FROM notes WHERE owner_id = $1 ORDER BY %s LIMIT $2`, order)
	rows, err := r.db.Query(ctx, query, ownerID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	return pgx.CollectRows(rows, pgx.RowToStructByPos[Note])
}

func (r *Repo) Get(ctx context.Context, ownerID, id string) (Note, error) {
	rows, _ := r.db.Query(ctx, `SELECT id, owner_id, title, body_md, share_slug, updated_at
		FROM notes WHERE id = $1 AND owner_id = $2`, id, ownerID)
	n, err := pgx.CollectOneRow(rows, pgx.RowToStructByPos[Note])
	if errors.Is(err, pgx.ErrNoRows) {
		return Note{}, ErrNotFound
	}
	return n, err
}

// GetShared resolves a public share link. Only notes with a slug are reachable, and only by slug.
func (r *Repo) GetShared(ctx context.Context, slug string) (Note, error) {
	rows, _ := r.db.Query(ctx, `SELECT id, owner_id, title, body_md, share_slug, updated_at
		FROM notes WHERE share_slug = $1`, slug)
	n, err := pgx.CollectOneRow(rows, pgx.RowToStructByPos[Note])
	if errors.Is(err, pgx.ErrNoRows) {
		return Note{}, ErrNotFound
	}
	return n, err
}

func (r *Repo) Create(ctx context.Context, ownerID, title, body string) (Note, error) {
	rows, _ := r.db.Query(ctx, `INSERT INTO notes (owner_id, title, body_md)
		VALUES ($1, $2, $3) RETURNING id, owner_id, title, body_md, share_slug, updated_at`, ownerID, title, body)
	return pgx.CollectOneRow(rows, pgx.RowToStructByPos[Note])
}

func (r *Repo) Update(ctx context.Context, ownerID, id, title, body string) (Note, error) {
	rows, _ := r.db.Query(ctx, `UPDATE notes SET title = $3, body_md = $4, updated_at = now()
		WHERE id = $1 AND owner_id = $2 RETURNING id, owner_id, title, body_md, share_slug, updated_at`, id, ownerID, title, body)
	n, err := pgx.CollectOneRow(rows, pgx.RowToStructByPos[Note])
	if errors.Is(err, pgx.ErrNoRows) {
		return Note{}, ErrNotFound
	}
	return n, err
}

// Delete removes the note and its attachment rows in one transaction and returns
// the stored attachment names so the caller can remove the files.
func (r *Repo) Delete(ctx context.Context, ownerID, id string) ([]string, error) {
	tx, err := r.db.Begin(ctx)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback(ctx)
	rows, _ := tx.Query(ctx, `DELETE FROM attachments a USING notes n
		WHERE a.note_id = $1 AND n.id = a.note_id AND n.owner_id = $2 RETURNING a.stored_name`, id, ownerID)
	stored, err := pgx.CollectRows(rows, pgx.RowTo[string])
	if err != nil {
		return nil, err
	}
	tag, err := tx.Exec(ctx, `DELETE FROM notes WHERE id = $1 AND owner_id = $2`, id, ownerID)
	if err != nil {
		return nil, err
	}
	if tag.RowsAffected() == 0 {
		return nil, ErrNotFound
	}
	return stored, tx.Commit(ctx)
}

func (r *Repo) SetShareSlug(ctx context.Context, ownerID, id string, slug *string) error {
	tag, err := r.db.Exec(ctx, `UPDATE notes SET share_slug = $3 WHERE id = $1 AND owner_id = $2`, id, ownerID, slug)
	if err != nil {
		return err
	}
	if tag.RowsAffected() == 0 {
		return ErrNotFound
	}
	return nil
}

func (r *Repo) AddAttachment(ctx context.Context, ownerID string, a Attachment) (Attachment, error) {
	// The note must belong to the caller; the INSERT is conditional on that join.
	rows, _ := r.db.Query(ctx, `INSERT INTO attachments (note_id, stored_name, display_name, content_type, size)
		SELECT n.id, $2, $3, $4, $5 FROM notes n WHERE n.id = $1 AND n.owner_id = $6
		RETURNING id, note_id, stored_name, display_name, content_type, size`,
		a.NoteID, a.StoredName, a.DisplayName, a.ContentType, a.Size, ownerID)
	out, err := pgx.CollectOneRow(rows, pgx.RowToStructByPos[Attachment])
	if errors.Is(err, pgx.ErrNoRows) {
		return Attachment{}, ErrNotFound
	}
	return out, err
}

func (r *Repo) GetAttachment(ctx context.Context, ownerID, noteID, attachmentID string) (Attachment, error) {
	rows, _ := r.db.Query(ctx, `SELECT a.id, a.note_id, a.stored_name, a.display_name, a.content_type, a.size
		FROM attachments a JOIN notes n ON n.id = a.note_id
		WHERE a.id = $1 AND a.note_id = $2 AND n.owner_id = $3`, attachmentID, noteID, ownerID)
	out, err := pgx.CollectOneRow(rows, pgx.RowToStructByPos[Attachment])
	if errors.Is(err, pgx.ErrNoRows) {
		return Attachment{}, ErrNotFound
	}
	return out, err
}

func (r *Repo) DeleteAttachment(ctx context.Context, ownerID, noteID, attachmentID string) (Attachment, error) {
	rows, _ := r.db.Query(ctx, `DELETE FROM attachments a USING notes n
		WHERE a.id = $1 AND a.note_id = $2 AND n.id = a.note_id AND n.owner_id = $3
		RETURNING a.id, a.note_id, a.stored_name, a.display_name, a.content_type, a.size`, attachmentID, noteID, ownerID)
	out, err := pgx.CollectOneRow(rows, pgx.RowToStructByPos[Attachment])
	if errors.Is(err, pgx.ErrNoRows) {
		return Attachment{}, ErrNotFound
	}
	return out, err
}
