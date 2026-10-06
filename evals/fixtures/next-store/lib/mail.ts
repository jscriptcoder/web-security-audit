import 'server-only';

export async function sendReceipt(orderId: string): Promise<void> {
  await fetch(`${process.env.MAILER_URL}/receipts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.MAILER_TOKEN}` },
    body: JSON.stringify({ orderId }),
  });
}
