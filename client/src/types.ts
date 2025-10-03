export type ElevBand = "below_treeline" | "treeline" | "above_treeline";
export type DangerLevel = 0|1|2|3|4|5;

export interface Prediction {
  above_treeline: DangerLevel;
  below_treeline: DangerLevel;
  treeline: DangerLevel;
  model_id?: string;
  scores?: {
    above_treeline: number[];
    below_treeline: number[];
    treeline: number[];
  }
}

export interface Forecast {
  id?: string;
  date?: string;
  datetime?: number;
  summary?: string;
  levels: Record<ElevBand, DangerLevel>;
  mode: "baseline" | "trained" | "fallback" | "rule_based";
}
