interface DepartmentSelectorProps {
  departments: string[];
  selected: string | null;
  onSelect: (dept: string) => void;
}

export function DepartmentSelector({ departments, selected, onSelect }: DepartmentSelectorProps) {
  if (departments.length === 0) {
    return <div className="text-sm text-neutral-600">暂无部门数据</div>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {departments.map((dept) => {
        const active = dept === selected;
        return (
          <button
            key={dept}
            type="button"
            onClick={() => onSelect(dept)}
            className={`rounded-md px-3 py-1.5 text-sm transition-colors ${
              active
                ? "bg-accent text-neutral-950"
                : "bg-neutral-900 text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200"
            }`}
          >
            {dept}
          </button>
        );
      })}
    </div>
  );
}
