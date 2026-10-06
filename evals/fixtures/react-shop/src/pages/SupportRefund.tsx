import { FormEvent, useState } from 'react';
import { issueRefund } from '../api/admin';

export function SupportRefundPage() {
  const [orderId, setOrderId] = useState('');
  const [amount, setAmount] = useState(0);
  const [done, setDone] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    await issueRefund(orderId, amount);
    setDone(true);
  }

  return (
    <form onSubmit={onSubmit}>
      <input value={orderId} onChange={(e) => setOrderId(e.target.value)} placeholder="Order ID" />
      <input type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} />
      <button type="submit">Issue refund</button>
      {done && <p>Refund issued.</p>}
    </form>
  );
}
