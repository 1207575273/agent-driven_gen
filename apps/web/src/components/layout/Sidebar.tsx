import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "仪表盘" },
  { to: "/projects", label: "项目看板" },
  { to: "/departments", label: "部门看板" },
  { to: "/roles", label: "角色分析" },
] as const;

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-20 flex h-full w-52 flex-col border-r border-neutral-900 bg-[#0a0a0a]">
      {/* Logo */}
      <div className="flex items-center gap-2 border-b border-neutral-900 px-5 py-4">
        <span className="h-2.5 w-2.5 rounded-sm bg-accent" />
        <span className="font-mono text-sm text-neutral-200">产能分析</span>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 py-4">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `mb-1 flex items-center rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-neutral-800 text-neutral-100"
                  : "text-neutral-500 hover:bg-neutral-900 hover:text-neutral-300"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-neutral-900 px-5 py-3">
        <span className="font-mono text-[11px] text-neutral-600">monorepo · 母版</span>
      </div>
    </aside>
  );
}
