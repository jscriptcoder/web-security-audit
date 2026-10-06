import { NextResponse } from 'next/server';
import { db } from '../../../../lib/db';
import { destroySession, getSession } from '../../../../lib/session';

export async function POST() {
  const session = await getSession();
  if (!session) return NextResponse.json({ error: 'unauthorized' }, { status: 401 });

  await db.user.delete({ where: { id: session.userId } });
  await destroySession();
  return NextResponse.json({ ok: true });
}
