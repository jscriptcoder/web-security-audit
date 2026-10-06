import { api } from './client';

export type Order = {
  id: string;
  status: 'PLACED' | 'SHIPPED' | 'CANCELLED';
  total: number;
  items: { sku: string; name: string; qty: number }[];
};

export const getOrder = (orderId: string) => api<Order>(`/orders/${orderId}`);

export const cancelOrder = (orderId: string) =>
  api<Order>(`/orders/${orderId}/cancel`, { method: 'POST' });
