package storage

import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"io"
	"os"
	"path/filepath"
)

// Files stores attachments under a single directory. Names are server-generated
// and every open goes through os.Root, which refuses to escape the directory
// even through symlinks.
type Files struct {
	root *os.Root
}

func OpenFiles(dir string) (*Files, error) {
	if dir == "" {
		return nil, errors.New("storage: DATA_DIR is required")
	}
	if err := os.MkdirAll(filepath.Join(dir, "attachments"), 0o750); err != nil {
		return nil, err
	}
	root, err := os.OpenRoot(filepath.Join(dir, "attachments"))
	if err != nil {
		return nil, err
	}
	return &Files{root: root}, nil
}

func (f *Files) Close() error { return f.root.Close() }

var ErrTooLarge = errors.New("storage: file exceeds the size limit")

// Put writes the content under a fresh random name and returns that name and
// the number of bytes written. Content beyond limit is rejected, not truncated.
// The client-supplied filename is kept only as display metadata by the caller.
func (f *Files) Put(r io.Reader, limit int64) (string, int64, error) {
	buf := make([]byte, 16)
	if _, err := rand.Read(buf); err != nil {
		return "", 0, err
	}
	name := hex.EncodeToString(buf)
	file, err := f.root.OpenFile(name, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o640)
	if err != nil {
		return "", 0, err
	}
	defer file.Close()
	n, err := io.Copy(file, io.LimitReader(r, limit+1))
	if err != nil {
		_ = f.root.Remove(name)
		return "", 0, err
	}
	if n > limit {
		_ = f.root.Remove(name)
		return "", 0, ErrTooLarge
	}
	return name, n, nil
}

// Open returns the stored file. A name that is not a plain local name is rejected.
func (f *Files) Open(name string) (*os.File, error) {
	if !filepath.IsLocal(name) || filepath.Base(name) != name {
		return nil, os.ErrNotExist
	}
	return f.root.Open(name)
}

func (f *Files) Remove(name string) error {
	if !filepath.IsLocal(name) || filepath.Base(name) != name {
		return os.ErrNotExist
	}
	return f.root.Remove(name)
}
