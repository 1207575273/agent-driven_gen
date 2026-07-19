import { Outlet } from "react-router-dom";
import { ResourceCard } from "../ResourceCard";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  return (
    <div className="min-h-full">
      {/* Top bar */}
      <header className="sticky top-0 z-30 border-b border-neutral-900 bg-[#0a0a0a]/90 backdrop-blur h-12">
        <div className="flex items-center justify-between h-full px-4">
          <span className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-sm bg-accent" />
            <span className="font-mono text-sm text-neutral-200">monorepo . 母版</span>
          </span>
          <ResourceCard />
        </div>
      </header>

      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <main className="ml-48 pt-12">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
