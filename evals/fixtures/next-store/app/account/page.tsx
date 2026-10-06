import { db } from '../../lib/db';
import { requireSession } from '../../lib/session';
import { AccountNav } from '../../components/AccountNav';
import { ProfileForm } from './ProfileForm';

export default async function AccountPage() {
  const { userId } = await requireSession();
  const user = await db.user.findUniqueOrThrow({ where: { id: userId } });

  return (
    <main>
      <AccountNav />
      <h1>Your account</h1>
      <ProfileForm user={user} />
      <form method="post" action="/api/logout">
        <button type="submit">Sign out</button>
      </form>
    </main>
  );
}
