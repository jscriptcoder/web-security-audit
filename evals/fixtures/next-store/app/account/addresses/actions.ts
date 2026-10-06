'use server';

import { revalidatePath } from 'next/cache';
import { db } from '../../../lib/db';
import { requireSession } from '../../../lib/session';

type AddressInput = { line1: string; city: string; zip: string };

export async function addAddress(input: AddressInput) {
  const { userId } = await requireSession();
  await db.address.create({ data: { ...pick(input), userId } });
  revalidatePath('/account/addresses');
}

export async function updateAddress(id: string, input: AddressInput) {
  const { userId } = await requireSession();
  const { count } = await db.address.updateMany({ where: { id, userId }, data: pick(input) });
  if (count !== 1) throw new Error('Address not found');
  revalidatePath('/account/addresses');
}

export async function deleteAddress(id: string) {
  await requireSession();
  await db.address.delete({ where: { id } });
  revalidatePath('/account/addresses');
}

function pick({ line1, city, zip }: AddressInput): AddressInput {
  return { line1: line1.slice(0, 120), city: city.slice(0, 60), zip: zip.slice(0, 12) };
}
