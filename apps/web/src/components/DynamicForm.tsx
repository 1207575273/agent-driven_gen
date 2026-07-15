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
}

// 配置化动态表单: 传入字段配置即渲染, 团队加表单不用重复写模板。
export function DynamicForm({
  fields,
  onSubmit,
  submitting = false,
  submitLabel = "提交",
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
    <form data-testid="dynamic-form" onSubmit={handleSubmit}>
      {fields.map((field) => (
        <label key={field.name} style={{ display: "block", marginBottom: 8 }}>
          <span style={{ marginRight: 8 }}>{field.label}</span>
          <input
            name={field.name}
            type={field.type}
            required={field.required}
            placeholder={field.placeholder}
            value={values[field.name] ?? ""}
            onChange={(event) => handleChange(field, event.target.value)}
          />
        </label>
      ))}
      <button type="submit" disabled={submitting}>
        {submitting ? "提交中..." : submitLabel}
      </button>
    </form>
  );
}
