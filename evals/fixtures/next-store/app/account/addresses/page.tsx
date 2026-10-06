import { db } from '../../../lib/db';
import { requireSession } from '../../../lib/session';
import { deleteAddress } from './actions';

export default async function AddressesPage() {
  const { userId } = await requireSession();
  const addresses = await db.address.findMany({ where: { userId } });

  return (
    <main>
      <h1>Addresses</h1>
      <ul>
        {addresses.map((a) => (
          <li key={a.id}>
            {a.line1}, {a.zip} {a.city}
            <form action={deleteAddress.bind(null, a.id)}>
              <button type="submit">Remove</button>
            </form>
          </li>
        ))}
      </ul>
    </main>
  );
}
