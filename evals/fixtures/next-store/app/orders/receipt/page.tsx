import { Suspense } from 'react';
import { ResendReceipt } from '../../../components/ResendReceipt';

export default function ReceiptPage() {
  return (
    <main>
      <h1>Your receipt</h1>
      <p>Didn&apos;t get the email? We can send it again.</p>
      <Suspense>
        <ResendReceipt />
      </Suspense>
    </main>
  );
}
