'use server';

import { revalidatePath } from 'next/cache';
import { db } from '../../lib/db';
import { requireSession } from '../../lib/session';

export async function updateProfile(input: { displayName: string; website: string }) {
  const { userId } = await requireSession();
  const website = input.website.trim();
  await db.user.update({
    where: { id: userId },
    data: { displayName: input.displayName.slice(0, 60), website: website === '' ? null : website },
  });
  revalidatePath('/account');
}
