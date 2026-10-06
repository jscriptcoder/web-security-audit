import 'server-only';
import { randomBytes } from 'node:crypto';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { db } from './db';

const SESSION_DAYS = 14;

export async function createSession(userId: string): Promise<void> {
  const id = randomBytes(32).toString('base64url');
  const expiresAt = new Date(Date.now() + SESSION_DAYS * 86_400_000);
  await db.session.create({ data: { id, userId, expiresAt } });
  (await cookies()).set('sid', id, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    expires: expiresAt,
  });
}

export async function getSession(): Promise<{ userId: string } | null> {
  const sid = (await cookies()).get('sid')?.value;
  if (!sid) return null;
  const session = await db.session.findUnique({ where: { id: sid } });
  if (!session || session.expiresAt < new Date()) return null;
  return { userId: session.userId };
}

export async function requireSession(): Promise<{ userId: string }> {
  const session = await getSession();
  if (!session) redirect('/login');
  return session;
}

export async function destroySession(): Promise<void> {
  const store = await cookies();
  const sid = store.get('sid')?.value;
  if (sid) await db.session.deleteMany({ where: { id: sid } });
  store.delete('sid');
}
