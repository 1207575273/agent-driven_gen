import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { path: "/capacity/audit", label: "产能填报审计", exact: true },
  { path: "/capacity/analysis", label: "产能交叉维度分析" },
  { path: "/capacity/admin", label: "数据管理" },
];

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-12 bottom-0 w-48 border-r border-neutral-800/50 bg-[#060b14]/95 backdrop-blur flex flex-col z-20">
      <nav className="flex-1 py-4">
        <ul className="space-y-0.5 px-2">
          {NAV_ITEMS.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                end={item.exact}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors ${
                    isActive
                      ? "bg-accent/10 text-accent border-l-2 border-accent"
                      : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/30 border-l-2 border-transparent"
                  }`
                }
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
