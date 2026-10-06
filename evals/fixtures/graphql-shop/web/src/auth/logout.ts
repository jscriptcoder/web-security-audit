import { setToken } from './token';

export async function logout(): Promise<void> {
  await fetch('https://auth.example.com/logout', { method: 'POST', credentials: 'include' });
  setToken(null);
  window.location.assign('/');
}
