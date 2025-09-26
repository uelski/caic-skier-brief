export type ElevBand = "below_treeline" | "treeline" | "above_treeline";
export type DangerLevel = 1|2|3|4|5;

export interface Forecast {
  id?: string;
  date?: string;
  datetime?: number;
  summary?: string;
  levels: Record<ElevBand, DangerLevel>;
  mode: "baseline" | "trained" | "fallback" | "rule_based";
}
