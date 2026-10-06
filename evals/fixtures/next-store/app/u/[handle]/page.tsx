import { notFound } from 'next/navigation';
import { db } from '../../../lib/db';

export default async function PublicProfilePage({ params }: { params: Promise<{ handle: string }> }) {
  const { handle } = await params;
  const profile = await db.user.findUnique({
    where: { handle },
    select: { displayName: true, website: true, bio: true },
  });
  if (!profile) notFound();

  return (
    <main>
      <h1>{profile.displayName}</h1>
      {profile.website && (
        <a href={profile.website} rel="nofollow ugc noopener" target="_blank">
          {profile.website}
        </a>
      )}
      {profile.bio && <p>{profile.bio}</p>}
    </main>
  );
}
