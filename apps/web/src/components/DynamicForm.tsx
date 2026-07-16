import { type FormEvent, useState } from "react";

export interface FieldConfig {
  name: string;
  label: string;
  type: "text" | "number";
  required?: boolean;
  placeholder?: string;
}

export type FormValues = Record<string, string | number>;

interface DynamicFormProps {
  fields: FieldConfig[];
  onSubmit: (values: FormValues) => void;
  submitting?: boolean;
  submitLabel?: string;
  // 内联布局: 字段与按钮横向排列(用于示例里的紧凑新增条)。
  inline?: boolean;
}

const INPUT_CLASS =
  "w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-neutral-100 placeholder:text-neutral-600 outline-none transition-colors focus:border-neutral-500";

// 配置化动态表单: 传入字段配置即渲染, 团队加表单不用重复写模板。
export function DynamicForm({
  fields,
  onSubmit,
  submitting = false,
  submitLabel = "提交",
  inline = false,
}: DynamicFormProps) {
  const [values, setValues] = useState<FormValues>({});

  const handleChange = (field: FieldConfig, raw: string) => {
    setValues((prev) => ({
      ...prev,
      [field.name]: field.type === "number" ? Number(raw) : raw,
    }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit(values);
  };

  return (
    <form
      data-testid="dynamic-form"
      onSubmit={handleSubmit}
      className={inline ? "flex flex-wrap items-end gap-3" : "flex flex-col gap-3"}
    >
      {fields.map((field) => (
        <label
          key={field.name}
          className={inline ? "flex min-w-[9rem] flex-1 flex-col gap-1.5" : "flex flex-col gap-1.5"}
        >
          <span
            className={`text-xs font-medium text-neutral-400${
              field.required ? " after:ml-1 after:text-accent after:content-['*']" : ""
            }`}
          >
            {field.label}
          </span>
          <input
            name={field.name}
            type={field.type}
            required={field.required}
            placeholder={field.placeholder}
            value={values[field.name] ?? ""}
            onChange={(event) => handleChange(field, event.target.value)}
            className={INPUT_CLASS}
          />
        </label>
      ))}
      <button
        type="submit"
        disabled={submitting}
        className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-neutral-950 transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {submitting ? "提交中…" : submitLabel}
      </button>
    </form>
  );
}
