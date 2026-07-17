interface DeviationBadgeProps {
  deviationLevel: "normal" | "yellow" | "red";
  deviation: number;
}

const levelMap = {
  normal: "bg-neutral-800 text-neutral-400",
  yellow: "bg-amber-500/20 text-amber-400",
  red: "bg-red-500/20 text-red-400",
} as const;

export function DeviationBadge({ deviationLevel, deviation }: DeviationBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 font-mono text-xs tabular-nums ${
        levelMap[deviationLevel]
      }`}
    >
      {deviation > 0 ? "+" : ""}
      {(deviation * 100).toFixed(0)}%
    </span>
  );
}
