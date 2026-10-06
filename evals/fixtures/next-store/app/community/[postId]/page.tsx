import { notFound } from 'next/navigation';
import { db } from '../../../lib/db';
import { PostBody } from '../../../components/PostBody';

export default async function PostPage({ params }: { params: Promise<{ postId: string }> }) {
  const { postId } = await params;
  const post = await db.post.findUnique({
    where: { id: postId },
    select: { title: true, body: true, author: { select: { displayName: true, handle: true } } },
  });
  if (!post) notFound();

  return (
    <article>
      <h1>{post.title}</h1>
      <p>
        by <a href={`/u/${encodeURIComponent(post.author.handle)}`}>{post.author.displayName}</a>
      </p>
      <PostBody markdown={post.body} />
    </article>
  );
}
