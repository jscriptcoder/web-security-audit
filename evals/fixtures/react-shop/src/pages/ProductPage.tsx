import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import { Review, ReviewData } from '../components/Review';
import { HelpTip } from '../components/HelpTip';
import { PartnerReceipt } from '../widgets/PartnerReceipt';

type Product = { sku: string; name: string; price: number; reviews: ReviewData[] };

export function ProductPage() {
  const { sku = '' } = useParams();
  const [product, setProduct] = useState<Product | null>(null);

  useEffect(() => {
    api<Product>(`/products/${encodeURIComponent(sku)}`).then(setProduct);
  }, [sku]);

  if (!product) return null;

  return (
    <section>
      <h1>{product.name}</h1>
      <p>
        {product.price.toFixed(2)} € <HelpTip topic="pricing" />
      </p>
      <PartnerReceipt />
      <h2>Reviews</h2>
      {product.reviews.map((r) => (
        <Review key={r.id} review={r} />
      ))}
    </section>
  );
}
