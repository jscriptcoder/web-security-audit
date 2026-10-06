export type Stock = { sku: string; available: number };

export async function fetchStock(sku: string): Promise<Stock> {
  const res = await fetch(`${process.env.INVENTORY_API_URL}/stock/${encodeURIComponent(sku)}`, {
    headers: { Authorization: `Bearer ${process.env.INVENTORY_API_TOKEN}` },
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`inventory ${res.status}`);
  return res.json();
}
