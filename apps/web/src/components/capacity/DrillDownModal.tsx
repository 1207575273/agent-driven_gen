import { type ReactNode, useCallback, useState } from "react";

export interface BreadcrumbItem {
  label: string;
  onClick?: () => void;
}

interface DrillDownModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  breadcrumbs: BreadcrumbItem[];
  children: ReactNode;
  loading?: boolean;
}

export function DrillDownModal({
  open,
  onClose,
  title,
  breadcrumbs,
  children,
  loading = false,
}: DrillDownModalProps) {
  const [visible, setVisible] = useState(open);

  const handleClose = useCallback(() => {
    setVisible(false);
    onClose();
  }, [onClose]);

  // Track open state for animation
  if (!open && !visible) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity ${
        open ? "opacity-100" : "opacity-0 pointer-events-none"
      }`}
      onClick={(e) => {
        if (e.target === e.currentTarget) handleClose();
      }}
      onKeyDown={(e) => {
        if (e.key === "Escape") handleClose();
      }}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative z-10 w-full max-w-5xl max-h-[85vh] mx-4 rounded-xl border border-neutral-700/50 bg-[#0a0f1e] shadow-2xl shadow-black/50 flex flex-col"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-800/50">
          <div className="flex items-center gap-3 min-w-0">
            <h2 className="text-lg font-semibold text-neutral-100 truncate">{title}</h2>
          </div>
          <button
            type="button"
            onClick={handleClose}
            className="rounded-md p-1.5 text-neutral-500 hover:text-neutral-200 hover:bg-neutral-800 transition-colors"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-label="关闭"
            >
              <title>关闭</title>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Breadcrumbs */}
        {breadcrumbs.length > 0 && (
          <div className="flex items-center gap-1 px-6 py-2 border-b border-neutral-800/30 text-xs text-neutral-500">
            {breadcrumbs.map((crumb, idx) => (
              <span key={`${crumb.label}-${idx}`} className="flex items-center gap-1">
                {idx > 0 && <span className="text-neutral-700">/</span>}
                {crumb.onClick ? (
                  <button
                    type="button"
                    onClick={crumb.onClick}
                    className="text-accent hover:underline transition-colors"
                  >
                    {crumb.label}
                  </button>
                ) : (
                  <span className="text-neutral-400">{crumb.label}</span>
                )}
              </span>
            ))}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-auto px-6 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-neutral-700 border-t-accent" />
            </div>
          ) : (
            children
          )}
        </div>
      </div>
    </div>
  );
}
