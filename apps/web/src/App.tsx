import { Suspense, lazy } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { LoadingSpinner } from "./components/shared/LoadingSpinner";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const ProjectsPage = lazy(() => import("./pages/ProjectsPage"));
const DepartmentsPage = lazy(() => import("./pages/DepartmentsPage"));
const RolesPage = lazy(() => import("./pages/RolesPage"));

export function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="departments" element={<DepartmentsPage />} />
            <Route path="roles" element={<RolesPage />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
