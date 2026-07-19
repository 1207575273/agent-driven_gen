// 通用 KPI 卡片: 标题 + 值 + 趋势指示, 科技风(玻璃拟态+霓虹边框)
interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  alert?: boolean; // 达到告警阈值时用橙色边框
  danger?: boolean; // 严重异常时用红色边框
}

function formatValue(v: string | number): string {
  if (typeof v === "number") {
    return v.toLocaleString("zh-CN", { maximumFractionDigits: 1 });
  }
  return v;
}

export function StatCard({ title, value, subtitle, alert = false, danger = false }: StatCardProps) {
  let borderColor = "border-neutral-800";
  let glowColor = "";
  if (danger) {
    borderColor = "border-red-500/50";
    glowColor = "shadow-[0_0_12px_rgba(239,68,68,0.15)]";
  } else if (alert) {
    borderColor = "border-amber-500/50";
    glowColor = "shadow-[0_0_12px_rgba(245,158,11,0.15)]";
  }

  return (
    <div
      className={`rounded-lg border ${borderColor} bg-neutral-900/60 backdrop-blur p-4 ${glowColor}`}
    >
      <div className="text-xs font-medium text-neutral-500 uppercase tracking-wider">{title}</div>
      <div
        className={`mt-1.5 text-2xl font-semibold ${
          danger ? "text-red-400" : alert ? "text-amber-400" : "text-neutral-100"
        }`}
      >
        {formatValue(value)}
      </div>
      {subtitle ? <div className="mt-1 text-xs text-neutral-600">{subtitle}</div> : null}
    </div>
  );
}
