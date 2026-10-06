import { config } from '../config';
import { getAccessToken } from '../auth/token';

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const res = await fetch(`${config.apiBase}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}`);
  }
  return (res.status === 204 ? null : await res.json()) as T;
}
