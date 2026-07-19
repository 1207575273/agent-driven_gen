import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { CapacityAuditPage } from "./pages/CapacityAuditPage";
import { CrossAnalysisPage } from "./pages/CrossAnalysisPage";
import { DataAdminPage } from "./pages/DataAdminPage";

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
      </Routes>
    </BrowserRouter>
  );
}
