import { marked } from 'marked';

export type ReviewData = {
  id: string;
  author: string;
  rating: number;
  body: string;
};

export function Review({ review }: { review: ReviewData }) {
  return (
    <article className="review">
      <header>
        {review.author} — {'★'.repeat(review.rating)}
      </header>
      <div className="review-body" dangerouslySetInnerHTML={{ __html: marked.parse(review.body) as string }} />
    </article>
  );
}
