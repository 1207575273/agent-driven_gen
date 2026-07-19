import { useSystemStats } from "../hooks/useItems";

// 占用越高越警示: 正常 emerald, >=70% 琥珀, >=90% 红。
function barColor(pct: number): string {
  if (pct >= 90) return "bg-red-500";
  if (pct >= 70) return "bg-amber-400";
  return "bg-accent";
}

// 进程内存占比通常很小(如 0.4%), 小于 1 时多给几位小数, 别一律取整成 0。
function fmtPct(pct: number): string {
  if (pct === 0) return "0%";
  if (pct >= 10) return `${Math.round(pct)}%`;
  if (pct >= 1) return `${pct.toFixed(1)}%`;
  return `${pct.toFixed(2)}%`;
}

// 进程内存固定用 MB 展示; digits 控制小数位(卡片取整, 悬浮给 1 位更精确)。
function fmtMB(bytes: number, digits = 0): string {
  return `${(bytes / 1024 ** 2).toFixed(digits)} MB`;
}

// 系统总内存较大, 用 GB 作分母参考。
function fmtGB(bytes: number): string {
  return `${(bytes / 1024 ** 3).toFixed(1)} GB`;
}

// 右上角资源卡片: 展示**当前后端进程**的实时占用(GET /api/v1/system/stats)。
// CPU = 本进程占整机 CPU 的百分比; MEM = 本进程常驻内存 RSS 及其占系统内存的百分比。
export function ResourceCard() {
  const { data, isError } = useSystemStats();
  const ok = Boolean(data) && !isError;

  return (
    <div
      className="flex items-center gap-3 rounded-md border border-neutral-800 bg-neutral-900/60 px-3 py-1.5"
      title="当前后端进程占用"
    >
      <div className="flex items-center gap-2" title="本进程占整机 CPU">
        <span className="font-mono text-[10px] tracking-wide text-neutral-500">CPU</span>
        <div className="h-1.5 w-12 overflow-hidden rounded-full bg-neutral-800">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              ok && data ? barColor(data.cpu_percent) : "bg-neutral-700"
            }`}
            style={{
              width: `${ok && data ? Math.min(100, data.cpu_percent) : 0}%`,
            }}
          />
        </div>
        <span className="w-9 text-right font-mono text-[11px] text-neutral-200">
          {ok && data ? fmtPct(data.cpu_percent) : "—"}
        </span>
      </div>

      <span className="h-4 w-px bg-neutral-800" />

      <div
        className="flex items-center gap-2"
        title={
          ok && data
            ? `本进程常驻内存 ${fmtMB(data.mem_rss, 1)} · 占系统内存 ${fmtPct(data.mem_percent)} · 系统共 ${fmtGB(data.mem_total)}`
            : "本进程内存占用"
        }
      >
        <span className="font-mono text-[10px] tracking-wide text-neutral-500">MEM</span>
        <span className="font-mono text-[11px] text-neutral-200">
          {ok && data ? fmtMB(data.mem_rss) : "—"}
        </span>
        <span className="font-mono text-[11px] text-accent">
          {ok && data ? fmtPct(data.mem_percent) : ""}
        </span>
      </div>
    </div>
  );
}
