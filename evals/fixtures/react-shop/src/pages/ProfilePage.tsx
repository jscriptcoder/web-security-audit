import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getPublicProfile, Profile } from '../api/profile';
import { Bio } from '../components/Bio';

export function ProfilePage() {
  const { accountId = '' } = useParams();
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    getPublicProfile(accountId).then(setProfile);
  }, [accountId]);

  if (!profile) return null;

  return (
    <article>
      <h1>{profile.displayName}</h1>
      {profile.website && (
        <a href={profile.website} target="_blank" rel="noopener noreferrer">
          {profile.website}
        </a>
      )}
      <Bio markdown={profile.bio} />
    </article>
  );
}
