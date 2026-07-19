import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DynamicForm, type FieldConfig } from "../src/components/DynamicForm";

const FIELDS: FieldConfig[] = [{ name: "name", label: "名称", type: "text", required: true }];

describe("DynamicForm", () => {
  it("should render configured fields", () => {
    render(<DynamicForm fields={FIELDS} onSubmit={vi.fn()} />);

    expect(screen.getByLabelText("名称")).toBeInTheDocument();
  });

  it("should call onSubmit with values when submitted", () => {
    const onSubmit = vi.fn();
    render(<DynamicForm fields={FIELDS} onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText("名称"), {
      target: { value: "widget" },
    });
    fireEvent.submit(screen.getByTestId("dynamic-form"));

    expect(onSubmit).toHaveBeenCalledWith({ name: "widget" });
  });
});
