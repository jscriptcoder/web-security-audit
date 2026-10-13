"""Smoke tests for the `Starting searches` patterns bundled in the references.

The compile check in test_sink_inventory.py proves a pattern is valid; these
tests prove it still matches the idiom it was written for, so an edit that
breaks a pattern cannot silently turn a stack's leads into an empty table.
Run: python3 -m unittest discover tests
"""

import re
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "web-security-audit"
FIXTURES = Path(__file__).resolve().parent.parent / "evals" / "fixtures"
sys.path.insert(0, str(SKILL / "scripts"))

import sink_inventory as si  # noqa: E402

# One representative source line per reference file and category. Each line is
# the idiom the category exists to surface, so a pattern that stops matching it
# has stopped doing its job. Adding a category to a reference requires a sample.
SAMPLES: dict[str, dict[str, str]] = {
    "references/stacks/dotnet.md": {
        "Entry points": '[HttpGet("{id}")]',
        "Bulk operations": "_db.Messages.RemoveRange(_db.Messages);",
        "Enforcement": '[Authorize(Roles = "Admin")]',
        "Interpreters": 'var orders = db.Orders.FromSqlRaw($"SELECT * FROM Orders WHERE Id = {id}");',
        "Config": "app.UseDeveloperExceptionPage();",
    },
    "references/stacks/go.md": {
        "Entry points": 'mux.HandleFunc("/notes", h.list)',
        "Bulk operations": '_, err := db.Exec("DELETE FROM notes")',
        "Interpreters": 'cmd := exec.Command("pandoc", "-f", "markdown")',
        "Outbound/config": "resp, err := http.Get(target)",
    },
    "references/stacks/java-kotlin.md": {
        "Entry points": '@GetMapping("/orders/{id}")',
        "Bulk operations": "mailboxRepository.deleteAll();",
        "Enforcement": '@PreAuthorize("hasRole(\'ADMIN\')")',
        "Interpreters": 'em.createNativeQuery("SELECT * FROM orders WHERE id = " + id)',
        "Parsers/outbound": "val factory = DocumentBuilderFactory.newInstance()",
        "Config": 'management.endpoints.web.exposure.include: "*"',
    },
    "references/stacks/javascript-node.md": {
        "Entry points": "app.get('/orders/:id', async (req, res) => {",
        "Bulk operations": "await FeedbackModel.destroy({ where: {} })",
        "Interpreters": 'const rows = await prisma.$queryRawUnsafe("SELECT * FROM orders WHERE id = " + id)',
        "Data flow": "const { role } = req.body;",
        "Outbound/config": "app.set('trust proxy', true)",
    },
    "references/stacks/php.md": {
        "Entry points": "$id = $_GET['id'];",
        "Bulk operations": "Message::query()->delete();",
        "Interpreters": '$rows = DB::raw("SELECT * FROM users WHERE id = $id");',
        "Config/data": "protected $guarded = [];",
    },
    "references/stacks/python.md": {
        "Entry points": '@router.get("/invoices/{invoice_id}")',
        "Bulk operations": "Message.objects.all().delete()",
        "Enforcement": "user: User = Depends(current_user)",
        "Interpreters": "cursor.execute(f\"SELECT * FROM invoices WHERE owner = '{name}'\")",
        "Config": "DEBUG = True",
    },
    "references/stacks/ruby.md": {
        "Entry points": "user = User.find(params[:id])",
        "Bulk operations": "Message.delete_all",
        "Enforcement": "before_action :authenticate_user!",
        "Interpreters": 'Order.where("name LIKE \'%#{params[:q]}%\'")',
    },
    "references/frontend-frameworks.md": {
        "Browser sinks": "<div dangerouslySetInnerHTML={{ __html: review.body }} />",
        "Rich content": "const html = marked.parse(body)",
        "Navigation": "window.location.href = returnUrl",
        "Client requests": "fetch(`/api/orders/${orderId}`)",
        "Messages and storage": "window.addEventListener('message', onPartnerMessage)",
        "Server code in the frontend repo": "'use server'",
    },
    "references/frontend-runtime.md": {
        "Build config": "const key = import.meta.env.VITE_ADMIN_API_SECRET",
        "Secret-looking names in client code": "const token = process.env.STRIPE_SECRET_KEY",
        "Tokens and storage": "localStorage.setItem('access_token', token)",
        "Service workers and caches": "navigator.serviceWorker.register('/sw.js')",
        "Third parties and embedding": '<script src="https://cdn.example.com/widget.js"></script>',
    },
}


def bundled_references() -> list[str]:
    return sorted({rel for files in si.STACK_REFERENCES.values() for rel in files})


class StartingSearchesMatchTheirIdiom(unittest.TestCase):
    def test_every_bundled_reference_has_samples(self) -> None:
        self.assertEqual(bundled_references(), sorted(SAMPLES))

    def test_every_category_has_a_sample_and_every_sample_names_a_real_category(self) -> None:
        for rel in bundled_references():
            categories = [category for category, _ in si.load_searches(SKILL / rel)]
            self.assertEqual(sorted(categories), sorted(SAMPLES[rel]), rel)

    def test_every_pattern_matches_the_idiom_it_exists_to_surface(self) -> None:
        for rel in bundled_references():
            for category, pattern in si.load_searches(SKILL / rel):
                sample = SAMPLES[rel][category]
                with self.subTest(reference=rel, category=category):
                    self.assertTrue(
                        re.search(pattern, sample),
                        f"/{pattern}/ no longer matches {sample!r}",
                    )


# Generated CRUD resources have no handler code to read, so their registration line
# is the only place an audit can find them. Each line must surface as an entry point.
GENERATED_RESOURCE_REGISTRATIONS: dict[str, str] = {
    "references/stacks/javascript-node.md": "finale.resource({ model: ProductModel, endpoints: ['/api/Products', '/api/Products/:id'] })",
    "references/stacks/java-kotlin.md": '@RepositoryRestResource(path = "orders", collectionResourceRel = "orders")',
    "references/stacks/python.md": 'router.register(r"orders", OrdersAPI, basename="orders")',
    "references/stacks/ruby.md": "resources :orders, only: [:index, :show, :update]",
    "references/stacks/php.md": "Route::resource('orders', OrderController::class);",
}


class GeneratedResourceRegistrationsAreEntryPoints(unittest.TestCase):
    def test_each_registration_idiom_matches_the_entry_points_pattern(self) -> None:
        for rel, sample in GENERATED_RESOURCE_REGISTRATIONS.items():
            pattern = dict(si.load_searches(SKILL / rel))["Entry points"]
            with self.subTest(reference=rel):
                self.assertTrue(re.search(pattern, sample), f"/{pattern}/ does not match {sample!r}")


class StartingSearchesFindLeadsInTheEvalFixtures(unittest.TestCase):
    def test_every_detected_stack_in_every_fixture_yields_at_least_one_lead(self) -> None:
        checked: set[str] = set()
        for fixture in sorted(p for p in FIXTURES.iterdir() if p.is_dir()):
            files, _ = si._walk(fixture)
            stacks = si._stacks_from_manifests(files)
            if not stacks:
                continue
            leads, errors = si.inventory(fixture, stacks, files)
            self.assertEqual(errors, [], fixture.name)
            for stack in stacks:
                self.assertTrue(
                    any(lead.stack == stack for lead in leads),
                    f"{fixture.name}: the {stack} searches found nothing",
                )
                checked.add(stack)
        self.assertGreaterEqual(len(checked), 4, f"only {sorted(checked)} were exercised by a fixture")


if __name__ == "__main__":
    unittest.main()
