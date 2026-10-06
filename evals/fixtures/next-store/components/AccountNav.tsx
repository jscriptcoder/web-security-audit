'use client';

import { useEffect, useState } from 'react';

export function AccountNav() {
  const [name, setName] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/me')
      .then((res) => (res.ok ? res.json() : null))
      .then((me) => me && setName(me.displayName))
      .catch(() => {});
  }, []);

  if (!name) return null;
  return <nav aria-label="account">Hi, {name}</nav>;
}
