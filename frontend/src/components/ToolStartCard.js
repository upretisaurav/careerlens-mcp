import { TOOL_LABELS } from "../constants";

export default function ToolStartCard({ tool }) {
  return (
    <div className="tool-start">
      <span className="tool-spinner" />
      <span>{TOOL_LABELS[tool] || `Running ${tool}...`}</span>
    </div>
  );
}
