import { MainLayout } from "@/components/layout/MainLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { PredictiveAlert } from "@/components/dashboard/PredictiveAlert";
import { AgentFlow } from "@/components/dashboard/AgentFlow";
import { VideoAnalysisViewer } from "@/components/dashboard/VideoAnalysisViewer";
import {
  useMetricsSimulation,
} from "@/hooks/useSimulation";
import { useBackendLive } from "@/hooks/useBackendLive";
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
  const backend = useBackendLive();
  const simMetrics = useMetricsSimulation();
  const { toast } = useToast();

  const isLive = backend.status === "connected";
  const metrics = backend.metrics ?? simMetrics;

  const handleAlertAction = () => {
    toast({
      title: "Action Initiated",
      description: "Secondary inspection has been deployed to Station 3",
    });
  };

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">Live Dashboard</h1>
            <p className="text-muted-foreground text-base mt-1">Real-time waste detection and routing</p>
          </div>
          <div className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-primary/10 border border-primary/30">
            <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse shadow-lg shadow-primary/50" />
            <span className="text-sm font-medium text-primary">System Online</span>
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

        {/* Video Analysis Section */}
        <div>
          <h2 className="text-2xl font-bold mb-4">Video Analysis</h2>
          <VideoAnalysisViewer />
        </div>

        {/* Agent Flow */}
        <AgentFlow />
      </div>
    </MainLayout>
  );
}
