import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangle, X, Zap, TrendingUp, DollarSign, Leaf } from "lucide-react";
import { cn } from "@/lib/utils";

interface PredictiveAlertProps {
  title?: string;
  currentRate?: number;
  historicalRate?: number;
  likelyCause?: string;
  recommendation?: string;
  impactDaily?: number;
  co2Impact?: number;
  onDismiss?: () => void;
  onAction?: () => void;
}

export function PredictiveAlert({
  title = "Plastic Stream Contamination Rising",
  currentRate = 31,
  historicalRate = 12,
  likelyCause = "Food containers during lunch hours (11 AM - 2 PM)",
  recommendation = "Deploy secondary inspection",
  impactDaily = -47,
  co2Impact = -23,
  onDismiss,
  onAction,
}: PredictiveAlertProps) {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <Card className="pro-card border-warning/50 pulse-alert overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-warning/10 via-transparent to-transparent" />
      <CardContent className="relative p-4">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="p-3 rounded-lg bg-warning/20 shrink-0">
            <AlertTriangle className="h-6 w-6 text-warning" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="flex items-center gap-2 text-xs text-warning font-medium mb-1">
                  <Zap className="h-3 w-3" />
                  PREDICTIVE ALERT
                </div>
                <h3 className="font-semibold text-lg">{title}</h3>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="shrink-0 -mt-1 -mr-2"
                onClick={() => {
                  setDismissed(true);
                  onDismiss?.();
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Stats */}
            <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-contamination" />
                <span className="text-muted-foreground">Rate:</span>
                <span className="font-medium">
                  {historicalRate}% → <span className="text-contamination">{currentRate}%</span>
                </span>
              </div>
              <div className="col-span-2 md:col-span-1 flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-contamination" />
                <span className="text-muted-foreground">Impact:</span>
                <span className="font-medium text-contamination">{impactDaily}/day</span>
              </div>
              <div className="flex items-center gap-2">
                <Leaf className="h-4 w-4 text-contamination" />
                <span className="text-muted-foreground">CO₂:</span>
                <span className="font-medium text-contamination">{co2Impact} kg/day</span>
              </div>
            </div>

            {/* Details */}
            <div className="mt-3 space-y-1 text-sm">
              <p>
                <span className="text-muted-foreground">Likely Cause:</span>{" "}
                <span>{likelyCause}</span>
              </p>
              <p>
                <span className="text-muted-foreground">Recommendation:</span>{" "}
                <span className="text-primary font-medium">{recommendation}</span>
              </p>
            </div>

            {/* Actions */}
            <div className="mt-4 flex items-center gap-2">
              <Button
                size="sm"
                onClick={() => {
                  onAction?.();
                }}
                className="bg-warning hover:bg-warning/90 text-foreground"
              >
                Take Action
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setDismissed(true);
                  onDismiss?.();
                }}
              >
                Dismiss
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
