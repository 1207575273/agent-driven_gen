import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section className="flex flex-col items-start gap-4 py-28">
      <span className="font-mono text-5xl text-neutral-700">404</span>
      <p className="text-sm text-neutral-400">这个页面不存在。</p>
      <Link
        to="/"
        className="rounded-md border border-neutral-700 px-4 py-2 text-sm text-neutral-200 transition-colors hover:border-neutral-500"
      >
        回主页
      </Link>
    </section>
  );
}
