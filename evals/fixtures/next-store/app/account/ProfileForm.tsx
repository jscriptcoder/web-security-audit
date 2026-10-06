'use client';

import type { User } from '@prisma/client';
import { useState } from 'react';
import { updateProfile } from './actions';

export function ProfileForm({ user }: { user: User }) {
  const [displayName, setDisplayName] = useState(user.displayName);
  const [website, setWebsite] = useState(user.website ?? '');

  return (
    <form action={() => updateProfile({ displayName, website })}>
      <p>Signed in as {user.email}</p>
      <label>
        Display name <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
      </label>
      <label>
        Website <input value={website} onChange={(e) => setWebsite(e.target.value)} />
      </label>
      <p>Two-factor authentication: {user.totpSecret ? 'on' : 'off'}</p>
      <button type="submit">Save</button>
    </form>
  );
}
