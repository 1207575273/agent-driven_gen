import { Link } from "react-router-dom";
import { ArchFlow } from "../components/ArchFlow";
import { CapabilityGrid } from "../components/CapabilityGrid";

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
      <Link
        to="/items"
        className="mt-8 inline-block rounded-md border border-neutral-700 px-4 py-2 text-sm text-neutral-200 transition-colors hover:border-neutral-500"
      >
        看实时 CRUD 示例 →
      </Link>
    </section>
  );
}

export function HomePage() {
  return (
    <>
      <Hero />
      <ArchFlow />
      <CapabilityGrid />
    </>
  );
}
