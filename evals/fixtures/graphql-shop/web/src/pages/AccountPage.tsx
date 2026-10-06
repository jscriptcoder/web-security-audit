import { useMutation, useQuery } from '@apollo/client';
import { FormEvent, useState } from 'react';
import { MY_ACCOUNT, REDEEM_GIFT_CARD } from '../queries';
import { logout } from '../auth/logout';

export function AccountPage() {
  const { data } = useQuery(MY_ACCOUNT);
  const [code, setCode] = useState('');
  const [redeem, { data: result }] = useMutation(REDEEM_GIFT_CARD, { refetchQueries: [MY_ACCOUNT] });

  if (!data?.me) return null;

  async function onRedeem(e: FormEvent) {
    e.preventDefault();
    await redeem({ variables: { code } });
  }

  return (
    <section>
      <h1>Hello {data.me.displayName}</h1>
      <p>
        {data.me.email} · {data.me.phone}
      </p>
      <p>Store credit: {data.me.creditBalance.toFixed(2)} €</p>
      <form onSubmit={onRedeem}>
        <input value={code} onChange={(e) => setCode(e.target.value)} inputMode="numeric" maxLength={6} />
        <button type="submit">Redeem gift card</button>
      </form>
      {result?.redeemGiftCard.message && <p role="alert">{result.redeemGiftCard.message}</p>}
      <h2>Orders</h2>
      <ul>
        {data.me.orders.map((o: { id: string; total: number; status: string; shippingAddress: string }) => (
          <li key={o.id}>
            #{o.id} · {o.status} · {o.total.toFixed(2)} € · {o.shippingAddress}
          </li>
        ))}
      </ul>
      <button onClick={() => logout()}>Sign out</button>
    </section>
  );
}
