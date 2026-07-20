import { NavLink, Outlet } from "react-router-dom";
import { ResourceCard } from "../components/ResourceCard";

function NavItem({ to, end, children }: { to: string; end?: boolean; children: string }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `text-sm transition-colors ${isActive ? "text-neutral-100" : "text-neutral-500 hover:text-neutral-300"}`
      }
    >
      {children}
    </NavLink>
  );
}

function TopBar() {
  return (
    <header className="sticky top-0 z-10 border-b border-neutral-900 bg-[#0a0a0a]/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3">
        <div className="flex items-center gap-6">
          <span className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-sm bg-accent" />
            <span className="font-mono text-sm text-neutral-200">monorepo·母版</span>
          </span>
          <nav className="flex items-center gap-4">
            <NavItem to="/" end>
              主页
            </NavItem>
            <NavItem to="/items">示例</NavItem>
          </nav>
        </div>
        <ResourceCard />
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="border-t border-neutral-900 py-8">
      <p className="font-mono text-xs text-neutral-600">
        pnpm dev · pnpm build · pnpm start · pnpm check —— KISS &amp; YAGNI
      </p>
    </footer>
  );
}

export function RootLayout() {
  return (
    <div className="min-h-full">
      <TopBar />
      <main className="mx-auto max-w-6xl px-6">
        <Outlet />
        <Footer />
      </main>
    </div>
  );
}
