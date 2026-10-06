# graphql-shop

Monorepo for the shop's GraphQL API and its web client.

- `api/`: Spring Boot + Spring for GraphQL (Kotlin). Stateless resource server; clients send a bearer JWT from `auth.example.com` with audience `shop-api`. Anonymous visitors can browse products and reviews.
- `web/`: React storefront using Apollo Client. The cache is persisted to `localStorage` so pages load instantly on return visits. The shop is used on shared in-store kiosks as well as personal devices.
