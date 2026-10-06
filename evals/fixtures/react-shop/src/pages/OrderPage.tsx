import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { cancelOrder, getOrder, Order } from '../api/orders';

export function OrderPage() {
  const { orderId = '' } = useParams();
  const [order, setOrder] = useState<Order | null>(null);

  useEffect(() => {
    getOrder(orderId).then(setOrder);
  }, [orderId]);

  if (!order) return <p>Loading…</p>;

  return (
    <section>
      <h1>Order {order.id}</h1>
      <p>Status: {order.status}</p>
      <ul>
        {order.items.map((item) => (
          <li key={item.sku}>
            {item.qty} × {item.name}
          </li>
        ))}
      </ul>
      {order.status === 'PLACED' && (
        <button onClick={() => cancelOrder(orderId).then(setOrder)}>Cancel order</button>
      )}
    </section>
  );
}
