export const config = {
  apiBase: import.meta.env.VITE_API_BASE ?? '/api',
  stripePublishableKey: import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY as string,
  adminApiSecret: import.meta.env.VITE_ADMIN_API_SECRET as string,
};
