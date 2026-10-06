'use client';

import { useEffect, useState } from 'react';
import { fetchStock } from '../lib/inventory';

export function StockBadge({ sku }: { sku: string }) {
  const [available, setAvailable] = useState<number | null>(null);

  useEffect(() => {
    let active = true;
    const refresh = () => fetchStock(sku).then((s) => active && setAvailable(s.available)).catch(() => {});
    refresh();
    const timer = setInterval(refresh, 30_000);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [sku]);

  if (available === null) return null;
  return <span className="stock">{available > 0 ? `${available} in stock` : 'Out of stock'}</span>;
}
