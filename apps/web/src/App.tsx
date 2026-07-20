import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { RootLayout } from "./layouts/RootLayout";
import { CapacityAuditPage } from "./pages/CapacityAuditPage";
import { CrossAnalysisPage } from "./pages/CrossAnalysisPage";
import { DataAdminPage } from "./pages/DataAdminPage";
import { HomePage } from "./pages/HomePage";
import { ItemsPage } from "./pages/ItemsPage";
import { NotFoundPage } from "./pages/NotFoundPage";

// 路由: 产能分析走 /capacity/*(AppLayout), 母版主页/示例走 RootLayout。
// / 由 RootLayout.index(HomePage) 承接, /capacity 重定向到审计页。
export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<RootLayout />}>
          <Route index element={<HomePage />} />
          <Route path="items" element={<ItemsPage />} />
        </Route>
        <Route element={<AppLayout />}>
          <Route path="/capacity" element={<Navigate to="/capacity/audit" replace />} />
          <Route path="/capacity/audit" element={<CapacityAuditPage />} />
          <Route path="/capacity/analysis" element={<CrossAnalysisPage />} />
          <Route path="/capacity/admin" element={<DataAdminPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
