import { MainLayout } from "@/components/layout/MainLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { DetectionFeed } from "@/components/dashboard/DetectionFeed";
import { DecisionStream } from "@/components/dashboard/DecisionStream";
import { PredictiveAlert } from "@/components/dashboard/PredictiveAlert";
import { AgentFlow } from "@/components/dashboard/AgentFlow";
import { useMetricsSimulation } from "@/hooks/useSimulation";
import { useToast } from "@/hooks/use-toast";
import {
  Package,
  AlertTriangle,
  Target,
  Gauge,
  Leaf,
  DollarSign,
} from "lucide-react";

export default function DashboardPage() {
  const metrics = useMetricsSimulation();
  const { toast } = useToast();

  const handleAlertAction = () => {
    toast({
      title: "Action Initiated",
      description: "Secondary inspection has been deployed to Station 3",
    });
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">Live Dashboard</h1>
            <p className="text-muted-foreground">Real-time waste detection and routing</p>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-muted-foreground">System Online</span>
          </div>
        </div>

        {/* Predictive Alert */}
        <PredictiveAlert onAction={handleAlertAction} />

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 stagger-children">
          <MetricCard
            title="Items Processed"
            value={metrics.itemsProcessed}
            icon={<Package className="h-5 w-5" />}
            variant="info"
          />
          <MetricCard
            title="Contamination Alerts"
            value={metrics.contaminationAlerts}
            icon={<AlertTriangle className="h-5 w-5" />}
            variant="warning"
          />
          <MetricCard
            title="System Accuracy"
            value={metrics.accuracy}
            suffix="%"
            trend={metrics.accuracyTrend}
            icon={<Target className="h-5 w-5" />}
            variant="success"
            decimals={1}
          />
          <MetricCard
            title="Efficiency Score"
            value={metrics.efficiencyScore}
            suffix="%"
            progress={metrics.efficiencyScore}
            icon={<Gauge className="h-5 w-5" />}
            variant="default"
          />
          <MetricCard
            title="CO₂ Saved"
            value={metrics.co2Saved}
            suffix=" kg"
            icon={<Leaf className="h-5 w-5" />}
            variant="success"
            decimals={1}
          />
          <MetricCard
            title="Recovery Value"
            value={metrics.recoveryValue}
            prefix="$"
            icon={<DollarSign className="h-5 w-5" />}
            variant="info"
          />
        </div>

        {/* Detection Feed and Decision Stream */}
        <div className="grid lg:grid-cols-2 gap-6">
          <DetectionFeed />
          <DecisionStream />
        </div>

        {/* Agent Flow */}
        <AgentFlow />
      </div>
    </MainLayout>
  );
}
