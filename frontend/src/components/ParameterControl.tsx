import type { ParameterSchema, ParameterValue } from "../types/api";

interface ParameterControlProps {
  name: string;
  schema: ParameterSchema;
  value: ParameterValue;
  onChange: (name: string, value: ParameterValue) => void;
}

export function ParameterControl({
  name,
  schema,
  value,
  onChange,
}: ParameterControlProps) {
  const id = `parameter-${name}`;

  if (schema.type === "boolean") {
    return (
      <label className="toggle-control" htmlFor={id}>
        <span>{schema.label}</span>
        <input
          id={id}
          type="checkbox"
          checked={Boolean(value)}
          onChange={(event) => onChange(name, event.target.checked)}
        />
      </label>
    );
  }

  if (schema.type === "select") {
    return (
      <label className="field" htmlFor={id}>
        <span>{schema.label}</span>
        <select
          id={id}
          value={String(value)}
          onChange={(event) => onChange(name, event.target.value)}
        >
          {schema.options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
    );
  }

  const numeric = schema.type === "integer" || schema.type === "number";
  return (
    <label className="field" htmlFor={id}>
      <span>{schema.label}</span>
      <input
        id={id}
        type={schema.type === "color" ? "color" : "number"}
        value={String(value)}
        min={schema.minimum ?? undefined}
        max={schema.maximum ?? undefined}
        step={schema.type === "integer" ? 1 : numeric ? "any" : undefined}
        onChange={(event) =>
          onChange(name, numeric ? event.target.valueAsNumber : event.target.value)
        }
      />
      {schema.description && <small>{schema.description}</small>}
    </label>
  );
}
