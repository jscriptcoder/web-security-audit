const KEY = 'shop.accessToken';

export function getAccessToken(): string | null {
  return localStorage.getItem(KEY);
}

export function setAccessToken(token: string): void {
  localStorage.setItem(KEY, token);
}

export function clearAccessToken(): void {
  localStorage.removeItem(KEY);
}
