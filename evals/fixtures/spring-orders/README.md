# spring-orders

Orders API for the storefront. Stateless resource server: clients send an `Authorization: Bearer` JWT issued by the company identity provider (`auth.example.com`), which also issues tokens for other internal applications. Runs behind the company's load balancer on Kubernetes.
