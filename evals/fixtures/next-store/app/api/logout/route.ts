import { NextResponse, type NextRequest } from 'next/server';
import { destroySession } from '../../../lib/session';

export async function POST(request: NextRequest) {
  await destroySession();
  return NextResponse.redirect(new URL('/', request.url), 303);
}
