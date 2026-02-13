import { useEffect, useState } from "react";
import { backendHttpUrl } from "@/lib/config";
import { generateAlerts, Alert } from "@/lib/mockData";

type Status = "loading" | "live" | "offline";

export function useAlertsLive(refreshMs = 7000) {
  const [alerts, setAlerts] = useState<Alert[]>(generateAlerts());
  const [status, setStatus] = useState<Status>("loading");

  useEffect(() => {
    let cancelled = false;

    const fetchAlerts = async () => {
      try {
        const res = await fetch(`${backendHttpUrl}/contamination/alerts`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as Array<any>;
        if (cancelled) return;
        // Map backend shape to UI Alert type
        const mapped = json.map((a, idx) => ({
          id: a.id || `alert-${idx}`,
          type: (a.type as Alert["type"]) || "info",
          title: a.title,
          message: a.message,
          currentRate: a.currentRate ?? 0,
          historicalRate: a.historicalRate ?? 0,
          likelyCause: a.likelyCause ?? "Auto-generated",
          recommendation: a.recommendation ?? "Investigate and confirm",
          impactDaily: a.impactDaily ?? 0,
          co2Impact: a.co2Impact ?? 0,
          timestamp: new Date(a.timestamp),
          resolved: a.resolved ?? false,
        }));
        setAlerts(mapped);
        setStatus("live");
      } catch {
        if (cancelled) return;
        setStatus("offline");
        setAlerts(generateAlerts());
      }
    };

    fetchAlerts();
    const id = window.setInterval(fetchAlerts, refreshMs);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [refreshMs]);

  return { alerts, status, setAlerts };
}
