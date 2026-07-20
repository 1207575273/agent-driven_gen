import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { CapacityAuditPage } from "./pages/CapacityAuditPage";
import { CrossAnalysisPage } from "./pages/CrossAnalysisPage";
import { DataAdminPage } from "./pages/DataAdminPage";
import { RootLayout } from "./layouts/RootLayout";
import { HomePage } from "./pages/HomePage";
import { ItemsPage } from "./pages/ItemsPage";
import { NotFoundPage } from "./pages/NotFoundPage";

// 声明式路由(react-router library 模式)。深链刷新的兜底在后端 SpaStaticFiles。
export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/capacity/audit" replace />} />
          <Route path="/capacity/audit" element={<CapacityAuditPage />} />
          <Route path="/capacity/analysis" element={<CrossAnalysisPage />} />
          <Route path="/capacity/admin" element={<DataAdminPage />} />
        </Route>
        <Route element={<RootLayout />}>
          <Route path="items" element={<ItemsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
