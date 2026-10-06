package notes

import (
	"html/template"
	"os/exec"
	"context"
	"bytes"
	"time"

	"github.com/microcosm-cc/bluemonday"
)

var policy = func() *bluemonday.Policy {
	p := bluemonday.UGCPolicy()
	p.RequireNoFollowOnLinks(true)
	p.AddTargetBlankToFullyQualifiedLinks(true)
	return p
}()

// RenderHTML converts markdown to HTML with pandoc, then sanitizes the result.
// The returned value is template.HTML because sanitization is the last step.
func RenderHTML(ctx context.Context, markdown string) (template.HTML, error) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "pandoc", "--from", "commonmark", "--to", "html", "--sandbox")
	cmd.Stdin = bytes.NewBufferString(markdown)
	var out bytes.Buffer
	cmd.Stdout = &out
	if err := cmd.Run(); err != nil {
		return "", err
	}
	return template.HTML(policy.SanitizeBytes(out.Bytes())), nil
}

var sharedPage = template.Must(template.New("shared").Parse(`<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<title>{{.Title}}</title>
</head>
<body>
<h1>{{.Title}}</h1>
<article>{{.Body}}</article>
<footer>Shared read-only from notes.example.com</footer>
</body>
</html>`))

type SharedView struct {
	Title string
	Body  template.HTML
}

func SharedPage() *template.Template { return sharedPage }
