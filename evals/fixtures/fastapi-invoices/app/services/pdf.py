import subprocess
import tempfile
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from ..config import settings
from ..models import Invoice

_env = Environment(loader=PackageLoader("app", "templates"), autoescape=select_autoescape(["html"]))


def render_invoice(invoice: Invoice) -> Path:
    settings.pdf_dir.mkdir(parents=True, exist_ok=True)
    target = settings.pdf_dir / f"{invoice.id}.pdf"
    html = _env.get_template("invoice.html").render(invoice=invoice)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as source:
        source.write(html)
        source_path = Path(source.name)
    try:
        subprocess.run(
            ["wkhtmltopdf", "--quiet", "--disable-local-file-access", "--disable-javascript", str(source_path), str(target)],
            check=True,
            timeout=30,
            capture_output=True,
        )
    finally:
        source_path.unlink(missing_ok=True)
    return target
