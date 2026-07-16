// 架构一览: 一条请求从前端到库表, 依次穿过三层。做成横向流水线, 一眼看懂分层与流向。

interface FlowNode {
  no: string;
  title: string;
  sub: string;
  mono?: boolean;
}

const NODES: FlowNode[] = [
  { no: "", title: "浏览器 · React", sub: "React Query / Zustand" },
  { no: "1", title: "route", sub: "api/v1 · 薄控制器", mono: true },
  { no: "2", title: "service", sub: "业务逻辑 · 抛业务异常", mono: true },
  { no: "3", title: "repository", sub: "数据访问 · SQLModel", mono: true },
  { no: "", title: "SQLite · WAL", sub: "事务边界 get_session" },
];

function Arrow() {
  // 横屏向右、竖屏向下的连接符; 中性色, 不抢戏。
  return (
    <div className="flex shrink-0 items-center justify-center text-neutral-600">
      <span className="hidden md:inline">&#8594;</span>
      <span className="md:hidden">&#8595;</span>
    </div>
  );
}

export function ArchFlow() {
  return (
    <section className="border-t border-neutral-900 py-16">
      <div className="mb-8 flex flex-col gap-1">
        <h2 className="text-lg font-semibold text-neutral-100">一次请求怎么流动</h2>
        <p className="text-sm text-neutral-500">
          完整三层, 禁跨层。依赖装配{" "}
          <code className="text-neutral-300">session → repository → service → route</code>。
        </p>
      </div>

      <div className="flex flex-col gap-2 md:flex-row md:items-stretch">
        {NODES.map((node, i) => (
          <div
            key={node.title}
            className="flex flex-col gap-2 md:flex-1 md:flex-row md:items-stretch"
          >
            <div className="flex flex-1 flex-col justify-center gap-2 rounded-lg border border-neutral-800 bg-neutral-900/60 px-4 py-4">
              <div className="flex items-center gap-2">
                {node.no ? (
                  <span className="flex h-5 w-5 items-center justify-center rounded border border-neutral-700 font-mono text-[11px] text-neutral-400">
                    {node.no}
                  </span>
                ) : null}
                <span
                  className={`text-sm text-neutral-100 ${node.mono ? "font-mono" : "font-medium"}`}
                >
                  {node.title}
                </span>
              </div>
              <span className="text-xs text-neutral-500">{node.sub}</span>
            </div>
            {i < NODES.length - 1 ? <Arrow /> : null}
          </div>
        ))}
      </div>

      <p className="mt-5 font-mono text-xs text-neutral-600">
        {"// 全程只用 GET / POST —— 更新 POST /items/{id}/update,删除 POST /items/{id}/delete"}
      </p>
    </section>
  );
}
