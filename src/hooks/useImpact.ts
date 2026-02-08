import { useEffect, useMemo, useState } from "react";
import { backendHttpUrl } from "@/lib/config";
import { ImpactSummary, ThresholdSnapshot } from "@/lib/impactTypes";
import { generateImpactSummaryMock, generateThresholdSnapshotMock } from "@/lib/mockData";

type LiveState = "loading" | "live" | "offline";

export function useImpactLive(refreshMs = 6000) {
  const [data, setData] = useState<ImpactSummary>(generateImpactSummaryMock());
  const [status, setStatus] = useState<LiveState>("loading");

  useEffect(() => {
    let cancelled = false;

    const fetchImpact = async () => {
      try {
        const res = await fetch(`${backendHttpUrl}/impact/summary`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as ImpactSummary;
        if (cancelled) return;
        setData(json);
        setStatus("live");
      } catch {
        if (!cancelled) {
          setStatus("offline");
          setData(generateImpactSummaryMock());
        }
      }
    };

    fetchImpact();
    const id = window.setInterval(fetchImpact, refreshMs);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [refreshMs]);

  return { data, status };
}

export function useAdaptiveLearning(refreshMs = 8000) {
  const [data, setData] = useState<ThresholdSnapshot>(generateThresholdSnapshotMock());
  const [status, setStatus] = useState<LiveState>("loading");

  useEffect(() => {
    let cancelled = false;

    const fetchSnapshot = async () => {
      try {
        const res = await fetch(`${backendHttpUrl}/learning/thresholds`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as ThresholdSnapshot;
        if (cancelled) return;
        setData(json);
        setStatus("live");
      } catch {
        if (!cancelled) {
          setStatus("offline");
          setData(generateThresholdSnapshotMock());
        }
      }
    };

    fetchSnapshot();
    const id = window.setInterval(fetchSnapshot, refreshMs);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [refreshMs]);

  const sortedAdjustments = useMemo(
    () =>
      [...(data.adjustments || [])].sort(
        (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      ),
    [data.adjustments]
  );

  return { data, status, adjustments: sortedAdjustments };
}
