// 能力清单: 只列母版真实保证的东西, 不吹。发丝级分隔的网格, 克制、可扫读。

interface Capability {
  title: string;
  desc: string;
}

const CAPS: Capability[] = [
  {
    title: "只用 GET / POST",
    desc: "两种方法走天下, 更新/删除走 POST 子路径, 心智极简。",
  },
  {
    title: "SQLModel 全家桶",
    desc: "Base / Table / Create / Update / Public, 表结构与 API 契约解耦。",
  },
  {
    title: "mypy strict · 编译期替身",
    desc: "Python 没编译期, 靠严格类型 + Ruff 在提交前拦住低级错误。",
  },
  {
    title: "覆盖率 ≥ 80%",
    desc: "Ruff + mypy + pytest 三道防线, 一键 pnpm check 自查。",
  },
  {
    title: "同源单进程",
    desc: "pnpm build + start, 一个 uvicorn 同时托管前端页面与 API。",
  },
  {
    title: "端口自动探测",
    desc: "ports.json 候选端口, 被占用自动跳下一个, 不用手改配置。",
  },
  { title: "定时任务 · 进程内", desc: "APScheduler 随应用起停, 单进程不另起 worker, job 守三层。" },
  { title: "生产日志 · JSONL", desc: "控制台人读 + 文件 JSONL, 8 小时滚动、留 10 天自动清理。" },
  { title: "12-factor 配置", desc: "env + .env 覆盖, 预留配置中心热更 seam(Nacos / ConfigMap)。" },
];

export function CapabilityGrid() {
  return (
    <section className="border-t border-neutral-900 py-16">
      <div className="mb-8 flex flex-col gap-1">
        <h2 className="text-lg font-semibold text-neutral-100">母版保证什么</h2>
        <p className="text-sm text-neutral-500">
          开箱能跑通, 写不进烂代码 —— 只做这两件事, 但做扎实。
        </p>
      </div>

      <div className="grid grid-cols-1 gap-px overflow-hidden rounded-lg border border-neutral-800 bg-neutral-800 sm:grid-cols-2 lg:grid-cols-3">
        {CAPS.map((cap) => (
          <div key={cap.title} className="flex flex-col gap-2 bg-[#0d0d0d] px-5 py-5">
            <span className="font-mono text-sm text-neutral-100">{cap.title}</span>
            <span className="text-sm leading-relaxed text-neutral-500">{cap.desc}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
