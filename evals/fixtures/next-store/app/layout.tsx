import type { ReactNode } from 'react';
import { RegisterServiceWorker } from '../components/RegisterServiceWorker';

export const metadata = { title: 'Next Store' };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <RegisterServiceWorker />
        {children}
      </body>
    </html>
  );
}
