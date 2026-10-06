import { useSearchParams } from 'react-router-dom';

export function SearchPage() {
  const [params] = useSearchParams();
  const query = params.get('q') ?? '';

  return (
    <section>
      <h1>Results for “{query}”</h1>
      <p>No products matched {query}. Try a different search.</p>
    </section>
  );
}
