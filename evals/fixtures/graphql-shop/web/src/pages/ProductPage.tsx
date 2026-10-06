import { useQuery } from '@apollo/client';
import { useParams } from 'react-router-dom';
import { PRODUCT_PAGE } from '../queries';

export function ProductPage() {
  const { id = '' } = useParams();
  const { data, loading } = useQuery(PRODUCT_PAGE, { variables: { id } });

  if (loading || !data?.product) return null;

  return (
    <section>
      <h1>{data.product.name}</h1>
      <p>{data.product.price.toFixed(2)} €</p>
      <h2>Reviews</h2>
      {data.product.reviews.map((r: { id: string; rating: number; body: string; author: { displayName: string } }) => (
        <article key={r.id}>
          <header>
            {r.author.displayName} — {'★'.repeat(Math.max(0, Math.min(5, r.rating)))}
          </header>
          <p>{r.body}</p>
        </article>
      ))}
    </section>
  );
}
