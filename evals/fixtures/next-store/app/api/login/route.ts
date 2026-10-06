import bcrypt from 'bcryptjs';
import { NextResponse, type NextRequest } from 'next/server';
import { db } from '../../../lib/db';
import { createSession } from '../../../lib/session';

function safeNext(value: FormDataEntryValue | null): string {
  const next = typeof value === 'string' ? value : '';
  return next.startsWith('/') ? next : '/account';
}

export async function POST(request: NextRequest) {
  const form = await request.formData();
  const email = String(form.get('email') ?? '').toLowerCase();
  const password = String(form.get('password') ?? '');
  const next = safeNext(form.get('next'));

  const user = await db.user.findUnique({ where: { email } });
  const ok = user ? await bcrypt.compare(password, user.passwordHash) : await bcrypt.compare(password, '$2a$12$invalidinvalidinvalidinvalidinvalidinvalidinvalidinva');
  if (!user || !ok) {
    return NextResponse.redirect(new URL(`/login?error=1&next=${encodeURIComponent(next)}`, request.url), 303);
  }

  await createSession(user.id);
  return NextResponse.redirect(new URL(next, request.url), 303);
}
