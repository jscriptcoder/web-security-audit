import { useEffect, useRef } from 'react';

const PARTNER_HOST = 'partner-pay.com';

export function PartnerReceipt() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      if (!event.origin.includes(PARTNER_HOST)) return;
      if (event.data?.type === 'receipt' && containerRef.current) {
        containerRef.current.innerHTML = event.data.receiptHtml;
      }
    }
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, []);

  return (
    <div>
      <iframe title="Pay with partner" src={`https://checkout.${PARTNER_HOST}/embed`} />
      <div ref={containerRef} className="partner-receipt" />
    </div>
  );
}
