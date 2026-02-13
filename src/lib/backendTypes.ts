import { BinType, binColors } from "./mockData";

export type LiveStatus = "connecting" | "connected" | "error";

export interface BackendEvent {
  id: string;
  ts: number;
  detection: {
    label: string;
    confidence: number;
    bbox: number[]; // [x,y,w,h] normalized
  };
  decision: {
    route: string;
    contamination_flag: boolean;
    agent_disagreement: boolean;
    reason?: string | null;
  };
  frame?: string; // Base64 encoded JPEG frame
}

export interface BackendMetricsResponse {
  items_processed: number;
  contamination_alerts: number;
  system_accuracy: number;
  efficiency_score: number;
  co2_saved_kg: number;
  recovery_value_usd: number;
}

export const routeToBin = (route: string): BinType => {
  const normalized = route.toLowerCase();
  if (normalized.startsWith("recycl")) return "recyclable";
  if (normalized.startsWith("organ")) return "organic";
  if (normalized.startsWith("hazard")) return "hazardous";
  if (normalized.startsWith("manual")) return "manual";
  return "landfill";
};

export const binLabel = (bin: BinType) => binColors[bin].label;
