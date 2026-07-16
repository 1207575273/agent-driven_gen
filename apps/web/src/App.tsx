import { ArchFlow } from "./components/ArchFlow";
import { CapabilityGrid } from "./components/CapabilityGrid";
import { ItemsPanel } from "./components/ItemsPanel";
import { ResourceCard } from "./components/ResourceCard";

function TopBar() {
  return (
    <header className="sticky top-0 z-10 border-b border-neutral-900 bg-[#0a0a0a]/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3">
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-sm bg-accent" />
          <span className="font-mono text-sm text-neutral-200">monorepo·母版</span>
        </span>
        <ResourceCard />
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="py-20">
      <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight text-neutral-50 sm:text-5xl">
        能直接跑通, 又写不进烂代码的
        <br />
        全栈母版
      </h1>
      <p className="mt-6 max-w-2xl text-base leading-relaxed text-neutral-400">
        FastAPI + SQLModel 的三层后端, React + TypeScript 的前端, 一条 pnpm 命令起飞。 给 PMO 与测试
        fork 出去, 迭代自己的工具与系统 —— 母版只保证开箱能跑通 + 写不进烂代码。
      </p>
    </section>
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

export function App() {
  return (
    <div className="min-h-full">
      <TopBar />
      <main className="mx-auto max-w-6xl px-6">
        <Hero />
        <ArchFlow />
        <CapabilityGrid />
        <ItemsPanel />
        <Footer />
      </main>
    </div>
  );
}
