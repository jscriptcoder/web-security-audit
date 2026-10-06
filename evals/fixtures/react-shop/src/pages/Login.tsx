import { FormEvent, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { api } from '../api/client';
import { setAccessToken } from '../auth/token';

export function LoginPage() {
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      const { accessToken } = await api<{ accessToken: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      setAccessToken(accessToken);
      const returnUrl = new URLSearchParams(location.search).get('returnUrl') || '/';
      window.location.href = returnUrl;
    } catch {
      setError('Invalid email or password');
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" />
      {error && <p role="alert">{error}</p>}
      <button type="submit">Sign in</button>
    </form>
  );
}
