import { useEffect, useMemo, useRef, useState } from "react";
import { backendHttpUrl, backendWsUrl } from "@/lib/config";
import {
  BackendEvent,
  BackendMetricsResponse,
  LiveStatus,
  routeToBin,
} from "@/lib/backendTypes";
import { BinType, Detection as UiDetection, DecisionEntry, Metrics, initialMetrics } from "@/lib/mockData";

type HookState = {
  status: LiveStatus;
  detections: UiDetection[];
  decisions: DecisionEntry[];
  metrics: Metrics | null;
  lastError?: string;
};

const MAX_DETECTIONS = 8;
const MAX_DECISIONS = 20;

const mapEventToDetection = (evt: BackendEvent): UiDetection => {
  const bin = routeToBin(evt.decision.route);
  const name = evt.detection.label.replace(/_/g, " ");
  const [x, y, w, h] = evt.detection.bbox;
  return {
    id: evt.id,
    item: { name, category: evt.detection.label, bin },
    confidence: evt.detection.confidence,
    timestamp: new Date(evt.ts * 1000),
    x: Math.round(x * 100 * 10) / 10,
    y: Math.round(y * 100 * 10) / 10,
    width: Math.round(w * 100 * 10) / 10,
    height: Math.round(h * 100 * 10) / 10,
  };
};

const mapEventToDecision = (evt: BackendEvent): DecisionEntry => {
  const bin: BinType = routeToBin(evt.decision.route);
  return {
    id: evt.id,
    timestamp: new Date(evt.ts * 1000),
    itemName: evt.detection.label,
    bin,
    confidence: evt.detection.confidence,
  };
};

const mapMetrics = (
  resp: BackendMetricsResponse,
  previous?: Metrics | null
): Metrics => {
  const accuracyPercent = Math.round(resp.system_accuracy * 1000) / 10;
  const efficiencyPercent = Math.round(resp.efficiency_score * 1000) / 10;
  const trend =
    previous && previous.accuracy
      ? Math.round((accuracyPercent - previous.accuracy) * 10) / 10
      : 0;
  return {
    itemsProcessed: resp.items_processed,
    contaminationAlerts: resp.contamination_alerts,
    accuracy: accuracyPercent,
    accuracyTrend: trend,
    efficiencyScore: efficiencyPercent,
    co2Saved: resp.co2_saved_kg,
    recoveryValue: resp.recovery_value_usd,
  };
};

export function useBackendLive(): HookState {
  const [state, setState] = useState<HookState>({
    status: "connecting",
    detections: [],
    decisions: [],
    metrics: null,
  });

  const retryRef = useRef(0);
  const wsRef = useRef<WebSocket | null>(null);

  const wsUrl = useMemo(() => backendWsUrl, []);
  const metricsUrl = useMemo(() => `${backendHttpUrl}/metrics`, []);

  useEffect(() => {
    let alive = true;

    const connect = () => {
      if (!alive) return;
      setState((s) => ({ ...s, status: "connecting" }));
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        retryRef.current = 0;
        setState((s) => ({ ...s, status: "connected", lastError: undefined }));
      };

      ws.onmessage = (event) => {
        try {
          const parsed: BackendEvent = JSON.parse(event.data);
          const detection = mapEventToDetection(parsed);
          const decision = mapEventToDecision(parsed);

          setState((prev) => {
            const now = Date.now();
            const freshDetections = prev.detections.filter(
              (d) => now - d.timestamp.getTime() < 4000
            );
            const detections = [...freshDetections, detection].slice(-MAX_DETECTIONS);
            const decisions = [decision, ...prev.decisions].slice(0, MAX_DECISIONS);
            return { ...prev, detections, decisions };
          });
        } catch (err: any) {
          setState((s) => ({
            ...s,
            lastError: err?.message || "Failed to parse backend event",
          }));
        }
      };

      ws.onerror = () => {
        ws.close();
      };

      ws.onclose = () => {
        if (!alive) return;
        setState((s) => ({ ...s, status: "error" }));
        retryRef.current += 1;
        const backoff = Math.min(10000, 500 * 2 ** retryRef.current);
        setTimeout(connect, backoff);
      };
    };

    connect();
    return () => {
      alive = false;
      wsRef.current?.close();
    };
  }, [wsUrl]);

  useEffect(() => {
    let timer: number | undefined;
    let cancelled = false;

    const fetchMetrics = async () => {
      try {
        const res = await fetch(metricsUrl);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json: BackendMetricsResponse = await res.json();
        setState((prev) => ({
          ...prev,
          metrics: mapMetrics(json, prev.metrics ?? initialMetrics),
        }));
      } catch (err: any) {
        if (!cancelled) {
          setState((s) => ({
            ...s,
            lastError: err?.message || "Metrics fetch failed",
          }));
        }
      }
    };

    fetchMetrics();
    timer = window.setInterval(fetchMetrics, 4000);

    return () => {
      cancelled = true;
      if (timer) window.clearInterval(timer);
    };
  }, [metricsUrl]);

  return state;
}
