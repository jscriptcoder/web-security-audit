'use client';

import { useSearchParams } from 'next/navigation';
import { useState } from 'react';

export function ResendReceipt() {
  const order = useSearchParams().get('order') ?? '';
  const [status, setStatus] = useState<'idle' | 'sent' | 'error'>('idle');

  async function resend() {
    const res = await fetch(`/api/orders/${encodeURI(order)}/receipt`, { method: 'POST' });
    setStatus(res.ok ? 'sent' : 'error');
  }

  return (
    <div>
      <p>Order {order}</p>
      <button onClick={resend} disabled={!order}>
        Resend receipt
      </button>
      {status === 'sent' && <p>Sent.</p>}
      {status === 'error' && <p role="alert">Could not send the receipt.</p>}
    </div>
  );
}
