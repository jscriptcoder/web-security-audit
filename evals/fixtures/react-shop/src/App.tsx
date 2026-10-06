import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { LoginPage } from './pages/Login';
import { OrderPage } from './pages/OrderPage';
import { SearchPage } from './pages/Search';
import { EditProfilePage } from './pages/EditProfile';
import { ProfilePage } from './pages/ProfilePage';
import { ProductPage } from './pages/ProductPage';
import { SupportRefundPage } from './pages/SupportRefund';
import { RequireRole } from './auth/RequireRole';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/products/:sku" element={<ProductPage />} />
        <Route path="/orders/:orderId" element={<OrderPage />} />
        <Route path="/users/:accountId" element={<ProfilePage />} />
        <Route path="/settings/profile" element={<EditProfilePage />} />
        <Route
          path="/support/refunds"
          element={
            <RequireRole role="SUPPORT">
              <SupportRefundPage />
            </RequireRole>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
