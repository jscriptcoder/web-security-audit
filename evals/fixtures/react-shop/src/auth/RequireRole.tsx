import { ReactNode, useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { getMyProfile, Profile } from '../api/profile';

export function RequireRole({ role, children }: { role: Profile['role']; children: ReactNode }) {
  const [profile, setProfile] = useState<Profile | null | undefined>(undefined);

  useEffect(() => {
    getMyProfile().then(setProfile, () => setProfile(null));
  }, []);

  if (profile === undefined) return null;
  if (!profile || (profile.role !== role && profile.role !== 'ADMIN')) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
