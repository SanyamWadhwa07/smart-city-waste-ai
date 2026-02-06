import { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useAnimatedCounter } from "@/hooks/useSimulation";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: number;
  icon: ReactNode;
  suffix?: string;
  prefix?: string;
  trend?: number;
  progress?: number;
  variant?: "default" | "success" | "warning" | "info";
  decimals?: number;
}

const variantStyles = {
  default: "border-border/50",
  success: "border-primary/50",
  warning: "border-accent/50",
  info: "border-secondary/50",
};

const iconVariants = {
  default: "bg-muted text-foreground",
  success: "bg-primary/20 text-primary",
  warning: "bg-accent/20 text-accent",
  info: "bg-secondary/20 text-secondary",
};

export function MetricCard({
  title,
  value,
  icon,
  suffix = "",
  prefix = "",
  trend,
  progress,
  variant = "default",
  decimals = 0,
}: MetricCardProps) {
  const animatedValue = useAnimatedCounter(Math.floor(value));
  
  const displayValue = decimals > 0 
    ? value.toFixed(decimals)
    : animatedValue.toString();

  return (
    <Card className={cn("glass-card overflow-hidden", variantStyles[variant])}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold counter-animate">
                {prefix}{displayValue}{suffix}
              </span>
              {trend !== undefined && (
                <span
                  className={cn(
                    "flex items-center text-xs font-medium",
                    trend >= 0 ? "text-primary" : "text-destructive"
                  )}
                >
                  {trend >= 0 ? (
                    <TrendingUp className="h-3 w-3 mr-0.5" />
                  ) : (
                    <TrendingDown className="h-3 w-3 mr-0.5" />
                  )}
                  {Math.abs(trend)}%
                </span>
              )}
            </div>
          </div>
          <div className={cn("p-2 rounded-lg", iconVariants[variant])}>
            {icon}
          </div>
        </div>
        {progress !== undefined && (
          <div className="mt-3">
            <Progress value={progress} className="h-2" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
