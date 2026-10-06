import { NextResponse, type NextRequest } from 'next/server';
import { db } from '../../../../../lib/db';
import { getSession } from '../../../../../lib/session';
import { sendReceipt } from '../../../../../lib/mail';

export async function POST(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await getSession();
  if (!session) return NextResponse.json({ error: 'unauthorized' }, { status: 401 });

  const { id } = await params;
  const order = await db.order.findFirst({ where: { id, userId: session.userId } });
  if (!order) return NextResponse.json({ error: 'not found' }, { status: 404 });

  await sendReceipt(order.id);
  return NextResponse.json({ ok: true });
}
