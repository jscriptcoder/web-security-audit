# go-notes

Notes API for the team workspace app. Clients send an `Authorization: Bearer` JWT issued by the company identity provider (`https://auth.example.com`, audience `notes-api`). Attachments are stored on local disk under the data directory. Public share links are read-only and unauthenticated by design. Runs behind the company's load balancer; the admin listener is bound to localhost and reached over the pod's port-forward only.
