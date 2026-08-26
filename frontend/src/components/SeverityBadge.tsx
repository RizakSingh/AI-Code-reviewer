import type { Severity } from "../api/types"

const STYLES: Record<Severity, string> = {
  info: "bg-sky-100/70 text-sky-700 ring-sky-300 backdrop-blur",
  warning: "bg-amber-100/70 text-amber-700 ring-amber-300 backdrop-blur",
  critical: "bg-rose-100/70 text-rose-700 ring-rose-300 backdrop-blur",
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={`inline-flex shrink-0 items-center rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ring-1 ring-inset ${STYLES[severity]}`}
    >
      {severity}
    </span>
  )
}
