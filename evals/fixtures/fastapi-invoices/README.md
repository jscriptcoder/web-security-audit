# fastapi-invoices

Invoicing API for freelancers and small agencies. Users register with their company, create invoices for their customers and download PDFs to send on. The payment provider calls our webhook when a customer pays; the `paid` status drives dunning emails and the nightly accounting sync. Clients authenticate with a bearer JWT issued by `/auth/login`. Deployed behind the company API gateway. See `docs/SECURITY_NOTES.md` for the current security posture.
