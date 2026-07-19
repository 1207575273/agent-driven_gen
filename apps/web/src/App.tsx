import { Route, Routes } from "react-router-dom";
import { RootLayout } from "./layouts/RootLayout";
import { HomePage } from "./pages/HomePage";
import { ItemsPage } from "./pages/ItemsPage";
import { NotFoundPage } from "./pages/NotFoundPage";

// 声明式路由(react-router library 模式)。深链刷新的兜底在后端 SpaStaticFiles。
export function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route index element={<HomePage />} />
        <Route path="items" element={<ItemsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
