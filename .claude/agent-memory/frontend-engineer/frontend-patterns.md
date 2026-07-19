---
name: frontend-patterns
description: React + TypeScript 前端 UI 模式与约定汇总
metadata:
  type: project
---

# 前端模式与约定

## 项目设置
- React 18 + Vite + TypeScript strict + Tailwind CSS v4
- **科技风暗色主题**: 深空蓝底 `#060b14` + 青蓝霓虹光 `#38bdf8`(accent) + 玻璃拟态
- 字体: UI 用 sans-serif, 数字用 `font-mono tabular-nums`, 标注用 `font-mono`

## 状态管理约定
- **服务端数据** -> React Query(`useQuery`/`useMutation`), queryKey 包含筛选参数, filter 变更自动 refetch
- **UI 状态** -> Zustand 或组件内 `useState`
- **全局筛选** -> Zustand `useFilterStore`(timeGranularity/deptLevel/deptName/role 等)

## 组件模式
- `StatCard.tsx` 可复用 KPI 卡片: `title/value/subtitle/alert/danger` props, 玻璃拟态+霓虹边框
- `LoadingSpinner.tsx` 居中 loading 态
- `EmptyState.tsx` 居中空态提示
- 图表组件统一用 `echarts-for-react`, SVG 渲染, `notMerge`, 暗色配色
- 三态处理: loading / empty / error / 数据展示
- SortableTable 泛型组件: `<SortableTable<T>>` 支持排序/高亮/行点击
- DrillDownModal: 面包屑导航 + 可递归 UseDrillModal

## ECharts 暗色配置模板
```
backgroundColor: "transparent"
textStyle: { color: "#94a3b8" }
tooltip: backgroundColor "rgba(15,23,42,0.9)", borderColor "#1e293b"
grid: { left: 16, right: 16, top: 30, bottom: 24 }
xAxis: axisLabel { color: "#94a3b8" }, axisLine { color: "#1e293b" }
yAxis: splitLine { lineStyle: { color: "#1e293b" } }
科技风配色: "#38bdf8", "#818cf8", "#6366f1", "#475569", "#1e293b"
```

## SortableTable 通用模式
```
// 泛型约束用 Record<string, any> + biome-ignore(only once in shared utility)
// 列定义: Column<T>[] with render callback
// th scope="col", onClick + onKeyDown(Enter) 双事件, tabIndex 0
// 排序状态: useState<string|null>, useState<"asc"|"desc"|null>
// 高亮: highlightRow callback + highlightClass
// 行点击: onRowClick, tr onClick + onKeyDown(Enter), tabIndex 0
```

## API 约定
- 只用 GET/POST, `request<T>` 函数从 `api/client.ts` export
- query params 走 `buildParams` + `URLSearchParams`
- `Record<string, string | number | boolean | null | undefined>` 类型签名包含 boolean
- 所有 hooks 放 `apps/web/src/hooks/`, 按页面拆文件
- Multipart 上传不设 Content-Type header

## Tailwind 常用 class
- 卡片容器: `rounded-lg border border-neutral-800 bg-neutral-900/40 p-5`
- 页面标题: `text-xl font-semibold text-neutral-100`
- 副标题: `text-sm text-neutral-500`
- 数字: `font-mono text-sm tabular-nums text-neutral-100`
- Tab: `border-b-2 border-(accent/transparent) -mb-px`

## 项目结构
```
apps/web/src/
  api/capacity.ts       - 全部类型定义(interface) + API 函数
  hooks/useCapacity.ts  - 全部 React Query hooks(useQuery)
  stores/useFilterStore.ts - Zustand 全局筛选状态
  components/
    charts/PieChart.tsx, BarChart.tsx, LineChart.tsx, Heatmap.tsx - 共享图表组件
    shared/SortableTable.tsx, StatCard.tsx - 共享组件
    capacity/FilterBar.tsx, DrillDownModal.tsx - 业务组件
    capacity/AbnormalDetailList.tsx, MonthlyTrendChart.tsx, DepartmentFillRateTable.tsx - 审计子组件
    capacity/ZeroFillingList.tsx, DeviationRankingTable.tsx - 审计子组件
    capacity/TimeCategoryPanel.tsx, DeptCategoryPanel.tsx, RoleCategoryPanel.tsx - 交叉分析面板
    capacity/PersonRankingTable.tsx, MatrixPanel.tsx, ThreeFastComparison.tsx - 交叉分析面板
  pages/CapacityAuditPage.tsx, CrossAnalysisPage.tsx, DataAdminPage.tsx
```

## 脚坑记录

1. **SortableTable 泛型**: `T extends Record<string, any>` 是必要的折衷。不用 `Record<string, unknown>` 因为 `dataIndex: keyof T` 配合 `render(value: T[keyof T])` 的类型推断要求 T 的值的类型与 Column 中的 render 一致。用 `unknown` 会导致类型不兼容。

2. **biome lint a11y**: sortable th 需要 `scope="col"` 不要 `role="columnheader"`; clickable tr 不加 role=button, biome 建议用 button 包裹内容而非给 tr 加事件。

3. **API params Record type**: 因为 `buildParams` / queryKey 会传 `boolean`(如 `isAbnormalOnly`), 需要 `Record<string, string | number | boolean | null | undefined>`。

4. **isNaN -> Number.isNaN**: biome lint `noGlobalIsNan` 要求使用 `Number.isNaN` 代替全局 `isNaN`。
