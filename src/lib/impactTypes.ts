export interface ImpactHistoryPoint {
  ts: string;
  co2_saved: number;
  revenue: number;
}

export interface ImpactSummary {
  total_co2_kg: number;
  revenue_usd: number;
  contamination_prevented: number;
  by_material_co2: Record<string, number>;
  history: ImpactHistoryPoint[];
  last_updated: string;
}

export interface ThresholdPerformance {
  contamination_rate: number;
  conflict_rate: number;
  avg_confidence: number;
  sample_size: number;
}

export interface ThresholdSnapshot {
  thresholds: Record<string, number>;
  performance: Record<string, ThresholdPerformance>;
  adjustments: Array<{
    timestamp: string;
    material_type: string;
    old_threshold: number;
    new_threshold: number;
    reason: string;
  }>;
}
