import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { RootLayout } from "./layouts/RootLayout";
import { CapacityAuditPage } from "./pages/CapacityAuditPage";
import { CrossAnalysisPage } from "./pages/CrossAnalysisPage";
import { DataAdminPage } from "./pages/DataAdminPage";
import { HomePage } from "./pages/HomePage";
import { ItemsPage } from "./pages/ItemsPage";
import { NotFoundPage } from "./pages/NotFoundPage";

// 路由: 产能分析走 AppLayout(默认首页), 母版主页/示例走 RootLayout。
export function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/capacity/audit" replace />} />
        <Route path="/capacity/audit" element={<CapacityAuditPage />} />
        <Route path="/capacity/analysis" element={<CrossAnalysisPage />} />
        <Route path="/capacity/admin" element={<DataAdminPage />} />
      </Route>
      <Route element={<RootLayout />}>
        <Route path="/home" element={<HomePage />} />
        <Route path="items" element={<ItemsPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
