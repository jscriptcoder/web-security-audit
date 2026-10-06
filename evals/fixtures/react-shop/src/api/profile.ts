import { api } from './client';

export type Profile = {
  accountId: string;
  displayName: string;
  bio: string;
  website: string;
  role: 'CUSTOMER' | 'SUPPORT' | 'ADMIN';
};

export const getMyProfile = () => api<Profile>('/users/me');

export const getPublicProfile = (accountId: string) =>
  api<Profile>(`/users/${encodeURIComponent(accountId)}/profile`);

export const updateMyProfile = (profile: Profile) =>
  api<Profile>('/users/me', { method: 'PUT', body: JSON.stringify(profile) });
