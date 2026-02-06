import { useState, useEffect, useCallback } from "react";
import {
  Detection,
  DecisionEntry,
  Metrics,
  generateDetection,
  generateDecisionEntry,
  initialMetrics,
} from "@/lib/mockData";

export function useDetectionSimulation(interval = 2000) {
  const [detections, setDetections] = useState<Detection[]>([]);

  useEffect(() => {
    const timer = setInterval(() => {
      setDetections((prev) => {
        // Remove old detections (older than 4 seconds)
        const now = Date.now();
        const filtered = prev.filter(
          (d) => now - d.timestamp.getTime() < 4000
        );
        
        // Add 1-3 new detections
        const newCount = Math.floor(Math.random() * 3) + 1;
        const newDetections = Array.from({ length: newCount }, generateDetection);
        
        return [...filtered, ...newDetections].slice(-8);
      });
    }, interval);

    return () => clearInterval(timer);
  }, [interval]);

  return detections;
}

export function useDecisionStream(interval = 1500, maxItems = 20) {
  const [decisions, setDecisions] = useState<DecisionEntry[]>([]);

  useEffect(() => {
    // Generate initial entries
    const initial = Array.from({ length: 5 }, generateDecisionEntry);
    setDecisions(initial);

    const timer = setInterval(() => {
      setDecisions((prev) => {
        const newEntry = generateDecisionEntry();
        return [newEntry, ...prev].slice(0, maxItems);
      });
    }, interval);

    return () => clearInterval(timer);
  }, [interval, maxItems]);

  return decisions;
}

export function useMetricsSimulation(interval = 3000) {
  const [metrics, setMetrics] = useState<Metrics>(initialMetrics);

  useEffect(() => {
    const timer = setInterval(() => {
      setMetrics((prev) => ({
        itemsProcessed: prev.itemsProcessed + Math.floor(Math.random() * 5) + 1,
        contaminationAlerts:
          prev.contaminationAlerts + (Math.random() > 0.85 ? 1 : 0),
        accuracy: Math.round((prev.accuracy + (Math.random() - 0.4) * 0.5) * 10) / 10,
        accuracyTrend: Math.round((prev.accuracyTrend + (Math.random() - 0.5) * 0.3) * 10) / 10,
        efficiencyScore: Math.min(
          100,
          Math.max(70, prev.efficiencyScore + (Math.random() - 0.4) * 2)
        ),
        co2Saved: Math.round((prev.co2Saved + Math.random() * 0.5) * 10) / 10,
        recoveryValue: prev.recoveryValue + Math.floor(Math.random() * 3),
      }));
    }, interval);

    return () => clearInterval(timer);
  }, [interval]);

  return metrics;
}

export function useAnimatedCounter(value: number, duration = 500) {
  const [displayValue, setDisplayValue] = useState(value);

  useEffect(() => {
    const startValue = displayValue;
    const diff = value - startValue;
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function
      const eased = 1 - Math.pow(1 - progress, 3);
      
      setDisplayValue(Math.round(startValue + diff * eased));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return displayValue;
}

export function useTheme() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.remove("light");
    } else {
      root.classList.add("light");
    }
  }, [isDark]);

  const toggle = useCallback(() => setIsDark((prev) => !prev), []);

  return { isDark, toggle };
}
