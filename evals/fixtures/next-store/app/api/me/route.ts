import { NextResponse } from 'next/server';
import { db } from '../../../lib/db';
import { getSession } from '../../../lib/session';

export async function GET() {
  const session = await getSession();
  if (!session) return NextResponse.json({ error: 'unauthorized' }, { status: 401 });

  const user = await db.user.findUniqueOrThrow({
    where: { id: session.userId },
    select: { email: true, displayName: true, addresses: { select: { line1: true, city: true, zip: true } } },
  });
  return NextResponse.json(user);
}
