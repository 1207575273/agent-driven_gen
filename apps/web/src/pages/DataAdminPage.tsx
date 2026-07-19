import { useState } from "react";
import { type ImportResult, dataImportApi } from "../api/capacity";

const FILE_ITEMS: Array<{ key: string; label: string; accept: string }> = [
  { key: "work_hour_file", label: "工时明细 Excel", accept: ".xlsx,.xls" },
  { key: "roster_file", label: "花名册 Excel", accept: ".xlsx,.xls" },
  { key: "project_category_file", label: "项目分类&项目清单 Excel", accept: ".xlsx,.xls" },
  { key: "holiday_file", label: "企业节假日 Excel", accept: ".xlsx,.xls" },
  { key: "three_fast_plan_file", label: "三快产能计划分配 Excel(可选)", accept: ".xlsx,.xls" },
];

export function DataAdminPage() {
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (key: string, file: File | null) => {
    setFiles((prev) => ({ ...prev, [key]: file }));
    setResult(null);
    setError(null);
  };

  const handleImport = async () => {
    setError(null);
    setResult(null);

    const requiredKeys = FILE_ITEMS.filter((f) => !f.label.includes("可选")).map((f) => f.key);
    const missingRequired = requiredKeys.filter((k) => !files[k]);
    if (missingRequired.length > 0) {
      const missingLabels = FILE_ITEMS.filter((f) => missingRequired.includes(f.key))
        .map((f) => f.label)
        .join("、");
      setError(`请选择必填文件: ${missingLabels}`);
      return;
    }

    setImporting(true);
    try {
      const formData = new FormData();
      for (const [key, file] of Object.entries(files)) {
        if (file) {
          formData.append(key, file);
        }
      }
      const res = await dataImportApi.import(formData);
      setResult(res);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "导入失败";
      setError(message);
    } finally {
      setImporting(false);
    }
  };

  return (
    <div>
      <h1 className="text-xl font-semibold text-neutral-100 mb-4">数据管理</h1>
      <p className="text-sm text-neutral-500 mb-6">
        上传 Excel 文件进行全量数据导入（清空旧数据后重新导入）。三快计划 Excel 为可选。
      </p>

      {/* File upload areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {FILE_ITEMS.map((item) => (
          <FileUploadBox
            key={item.key}
            label={item.label}
            accept={item.accept}
            selectedFile={files[item.key] ?? null}
            onFileSelect={(file) => handleFileSelect(item.key, file)}
          />
        ))}
      </div>

      {/* Import button */}
      <div className="flex items-center gap-4 mb-6">
        <button
          type="button"
          onClick={handleImport}
          disabled={importing}
          className="rounded-md bg-accent px-5 py-2 text-sm font-semibold text-neutral-950 transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {importing ? "导入中..." : "开始导入"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-4 text-sm text-red-400 mb-6">
          {error}
        </div>
      )}

      {/* Import result */}
      {result && <ImportResultSection result={result} />}
    </div>
  );
}

function FileUploadBox({
  label,
  accept,
  selectedFile,
  onFileSelect,
}: {
  label: string;
  accept: string;
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
}) {
  return (
    <div
      className={`rounded-lg border-2 border-dashed p-4 transition-colors ${
        selectedFile
          ? "border-accent/50 bg-accent/5"
          : "border-neutral-700 hover:border-neutral-600 bg-neutral-900/30"
      }`}
    >
      <label className="flex flex-col items-center gap-2 cursor-pointer">
        <span className="text-sm font-medium text-neutral-300">{label}</span>
        {selectedFile ? (
          <div className="flex items-center gap-2">
            <span className="text-xs text-accent">{selectedFile.name}</span>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                onFileSelect(null);
              }}
              className="text-xs text-neutral-500 hover:text-red-400"
            >
              清除
            </button>
          </div>
        ) : (
          <span className="text-xs text-neutral-600">拖拽文件到此处或点击选择</span>
        )}
        <input
          type="file"
          accept={accept}
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0] ?? null;
            onFileSelect(file);
          }}
        />
      </label>
    </div>
  );
}

function ImportResultSection({ result }: { result: ImportResult }) {
  const { stats } = result;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-neutral-100">导入结果</h2>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatBox label="员工导入" value={`${stats.employees_imported} 人`} />
        <StatBox label="工时导入" value={`${stats.work_hours_imported} 条`} />
        <StatBox label="分类导入" value={`${stats.categories_imported} 条`} />
        <StatBox label="节假日导入" value={`${stats.holidays_imported} 条`} />
        <StatBox label="应有产能记录" value={`${stats.capacity_records_created} 条`} />
        <StatBox label="人员匹配率" value={`${stats.employee_match_rate.toFixed(1)}%`} />
        <StatBox label="项目匹配率" value={`${stats.project_match_rate.toFixed(1)}%`} />
        <StatBox label="未匹配项目" value={`${stats.unmatched_projects.length} 个`} />
      </div>

      {/* Unmatched projects */}
      {stats.unmatched_projects.length > 0 && (
        <div className="rounded-lg border border-amber-900/50 bg-amber-900/10 p-4">
          <h3 className="text-sm font-medium text-amber-400 mb-2">
            未匹配项目清单 ({stats.unmatched_projects.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {stats.unmatched_projects.map((proj) => (
              <span
                key={proj}
                className="rounded-full bg-neutral-800 px-2.5 py-1 text-xs text-neutral-400"
              >
                {proj}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Errors */}
      {stats.errors.length > 0 && (
        <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-4">
          <h3 className="text-sm font-medium text-red-400 mb-2">
            错误信息 ({stats.errors.length})
          </h3>
          <ul className="list-disc list-inside space-y-1">
            {stats.errors.map((err) => (
              <li key={err} className="text-xs text-red-300">
                {err}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900/60 p-3">
      <div className="text-[10px] font-medium text-neutral-500 uppercase">{label}</div>
      <div className="mt-1 text-lg font-semibold text-neutral-200">{value}</div>
    </div>
  );
}
