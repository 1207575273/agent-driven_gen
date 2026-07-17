---
name: frontend-patterns
description: React + TypeScript 前端 UI 模式与约定汇总
metadata:
  type: project
---

# 前端模式与约定

## 项目设置
- React 18 + Vite + TypeScript strict + Tailwind CSS v4
- 暗色主题(`#0a0a0a` 底色, accent `#34d399` emerald)
- 字体: UI 用 sans-serif, 数字用 `font-mono tabular-nums`, 标注用 `font-mono`

## 状态管理约定
- **服务端数据** -> React Query(`useQuery`/`useMutation`), queryKey 包含筛选参数
- **UI 状态** -> Zustand 或组件内 `useState`
- **筛选参数** -> 先走组件内 state, P1 再做 Zustand 全局联动

## 组件模式
- `StatCard.tsx` 可复用 KPI 卡片: `title/value/unit/loading` props
- `LoadingSpinner.tsx` 居中 loading 态
- `EmptyState.tsx` 居中空态提示
- 图表组件统一用 `echarts-for-react`, SVG 渲染, `notMerge`, 暗色配色
- 三态处理: loading / empty / 数据展示

## ECharts 暗色配置模板
```ts
grid: { left: 16, right: 24, top: 24, bottom: 32, containLabel: true }
xAxis: { axisLabel: { color: "#a3a3a3", fontSize: 12 }, axisLine: { lineStyle: { color: "#404040" } }, axisTick: { show: false } }
yAxis: { axisLabel: { color: "#a3a3a3", fontSize: 12 }, splitLine: { lineStyle: { color: "#1f1f1f" } } }
series: { itemStyle: { color: "#34d399" } }
```

## 表格/Tab 可点击行的无障碍
- 用 `onClick` + `onKeyDown`(Enter/Space) 双事件
- 不加 `role="button"` 和 `tabIndex`(biome 告警 `useSemanticElements`)

## API 约定
- 只用 GET/POST, 前端 `apps/web/src/api/capacity.ts` 封装全部端点
- query params 走 `URLSearchParams`, 项目名 URL 编码用 `encodeURIComponent`
- 所有 hooks 放 `apps/web/src/hooks/`, 按页面拆文件

## Tailwind 常用 class
- 卡片容器: `rounded-lg border border-neutral-800 bg-neutral-900/40 p-5`
- 页面标题: `text-xl font-semibold text-neutral-100`
- 副标题: `text-sm text-neutral-500`
- 数字: `font-mono text-sm tabular-nums text-neutral-100`
