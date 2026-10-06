import { config } from '../config';
import { api } from './client';

export const issueRefund = (orderId: string, amount: number) =>
  api<void>('/admin/refunds', {
    method: 'POST',
    headers: { 'X-Admin-Secret': config.adminApiSecret },
    body: JSON.stringify({ orderId, amount }),
  });
