import { type ReactNode, useCallback, useMemo, useState } from "react";

export interface Column<T> {
  key: string;
  title: string;
  dataIndex: keyof T;
  render?: (value: T[keyof T], record: T) => ReactNode;
  sortable?: boolean;
  width?: string;
  align?: "left" | "right" | "center";
}

interface SortableTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: (record: T) => string | number;
  highlightRow?: (record: T) => boolean;
  highlightClass?: string;
  onRowClick?: (record: T) => void;
  emptyMessage?: string;
  defaultSortKey?: string;
  defaultSortDir?: "asc" | "desc";
}

type SortDirection = "asc" | "desc" | null;

// biome-ignore lint/suspicious/noExplicitAny: generic table needs flexible record type
export function SortableTable<T extends Record<string, any>>({
  columns,
  data,
  rowKey,
  highlightRow,
  highlightClass = "bg-yellow-900/20",
  onRowClick,
  emptyMessage = "暂无数据",
  defaultSortKey,
  defaultSortDir = "desc",
}: SortableTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(defaultSortKey ?? null);
  const [sortDir, setSortDir] = useState<SortDirection>(defaultSortDir);

  const handleSort = useCallback(
    (key: string) => {
      if (sortKey === key) {
        if (sortDir === "asc") {
          setSortDir("desc");
        } else if (sortDir === "desc") {
          setSortKey(null);
          setSortDir(null);
        } else {
          setSortDir("asc");
        }
      } else {
        setSortKey(key);
        setSortDir("asc");
      }
    },
    [sortKey, sortDir],
  );

  const sortedData = useMemo(() => {
    if (!sortKey || !sortDir) return data;
    return [...data].sort((a, b) => {
      const aVal = a[sortKey] as unknown;
      const bVal = b[sortKey] as unknown;
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortDir === "asc" ? aVal - bVal : bVal - aVal;
      }
      const aStr = String(aVal ?? "");
      const bStr = String(bVal ?? "");
      return sortDir === "asc" ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
    });
  }, [data, sortKey, sortDir]);

  const getSortIndicator = (key: string): string => {
    if (sortKey !== key) return " ↕";
    if (sortDir === "asc") return " ↑";
    if (sortDir === "desc") return " ↓";
    return " ↕";
  };

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        {emptyMessage}
      </div>
    );
  }

  const headerCellClass =
    "px-3 py-3 text-left text-xs font-medium text-neutral-400 uppercase tracking-wider";
  const bodyCellClass = "px-3 py-2.5 text-sm text-neutral-200 border-t border-neutral-800/50";

  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-800/50">
      <table className="min-w-full">
        <thead>
          <tr className="bg-neutral-900/50">
            {columns.map((col) => (
              <th
                key={col.key}
                className={`${headerCellClass} ${
                  col.sortable ? "cursor-pointer select-none hover:text-accent" : ""
                }`}
                style={{ width: col.width, textAlign: col.align ?? "left" }}
                onClick={() => col.sortable && handleSort(col.key)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && col.sortable) handleSort(col.key);
                }}
                tabIndex={col.sortable ? 0 : undefined}
                scope="col"
              >
                <span>
                  {col.title}
                  {col.sortable ? (
                    <span className="ml-1 text-neutral-600">{getSortIndicator(col.key)}</span>
                  ) : null}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((record) => {
            const isHighlighted = highlightRow?.(record) ?? false;
            return (
              <tr
                key={rowKey(record)}
                className={`${isHighlighted ? highlightClass : ""} ${
                  onRowClick ? "cursor-pointer transition-colors hover:bg-neutral-800/30" : ""
                }`}
                onClick={() => onRowClick?.(record)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && onRowClick) onRowClick(record);
                }}
                tabIndex={onRowClick ? 0 : undefined}
              >
                {columns.map((col) => {
                  const value = record[col.dataIndex];
                  return (
                    <td
                      key={col.key}
                      className={bodyCellClass}
                      style={{ textAlign: col.align ?? "left" }}
                    >
                      {col.render ? col.render(value, record) : String(value ?? "-")}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
