import { notFound } from 'next/navigation';
import { StockBadge } from '../../../components/StockBadge';

type Product = { sku: string; slug: string; name: string; description: string; price: number };

async function getProduct(slug: string): Promise<Product | null> {
  const res = await fetch(`${process.env.INVENTORY_API_URL}/products/${encodeURIComponent(slug)}`, {
    next: { revalidate: 300 },
  });
  return res.ok ? res.json() : null;
}

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const product = await getProduct(slug);
  if (!product) notFound();

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    sku: product.sku,
    offers: { '@type': 'Offer', price: product.price, priceCurrency: 'EUR' },
  };

  return (
    <main>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <StockBadge sku={product.sku} />
    </main>
  );
}
