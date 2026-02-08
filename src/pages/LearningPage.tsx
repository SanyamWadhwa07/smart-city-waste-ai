import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAdaptiveLearning } from "@/hooks/useImpact";
import { formatDistanceToNow } from "date-fns";
import { Gauge, SlidersHorizontal } from "lucide-react";

export default function LearningPage() {
  const { data, status, adjustments } = useAdaptiveLearning();

  const performanceEntries = Object.entries(data.performance || {});

  return (
    <MainLayout>
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
              Adaptive Learning
            </h1>
            <p className="text-muted-foreground text-base mt-1">
              Dynamic confidence thresholds and feedback-driven tuning
            </p>
          </div>
          <Badge variant={status === "live" ? "default" : "outline"}>
            {status === "live" ? "Live data" : status === "loading" ? "Connecting…" : "Simulated"}
          </Badge>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <Card className="pro-card">
            <CardHeader className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">Thresholds by Material</CardTitle>
                <CardDescription>Auto-adjusted per contamination & conflict rates</CardDescription>
              </div>
              <SlidersHorizontal className="h-5 w-5 text-primary" />
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Material</TableHead>
                    <TableHead className="text-right">Threshold</TableHead>
                    <TableHead className="text-right">Contamination</TableHead>
                    <TableHead className="text-right">Conflicts</TableHead>
                    <TableHead className="text-right">Avg. Conf.</TableHead>
                    <TableHead className="text-right">Samples</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {performanceEntries.map(([material, perf]) => (
                    <TableRow key={material}>
                      <TableCell className="font-semibold">{material}</TableCell>
                      <TableCell className="text-right">{data.thresholds[material]?.toFixed(2)}</TableCell>
                      <TableCell className="text-right">{perf.contamination_rate.toFixed(1)}%</TableCell>
                      <TableCell className="text-right">{perf.conflict_rate.toFixed(1)}%</TableCell>
                      <TableCell className="text-right">{perf.avg_confidence.toFixed(1)}%</TableCell>
                      <TableCell className="text-right text-muted-foreground">{perf.sample_size}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Card className="pro-card">
            <CardHeader className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">Recent Adjustments</CardTitle>
                <CardDescription>Last 20 threshold changes with reasons</CardDescription>
              </div>
              <Gauge className="h-5 w-5 text-secondary" />
            </CardHeader>
            <CardContent className="space-y-3">
              {adjustments.length === 0 && (
                <p className="text-sm text-muted-foreground">No adjustments yet.</p>
              )}
              {adjustments.map((adj) => (
                <div
                  key={adj.timestamp + adj.material_type}
                  className="p-3 rounded-lg border border-border/60 bg-muted/30 hover:border-primary/40 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{adj.material_type}</div>
                    <Badge variant="outline">
                      {formatDistanceToNow(new Date(adj.timestamp), { addSuffix: true })}
                    </Badge>
                  </div>
                  <p className="text-sm mt-1">
                    {adj.old_threshold.toFixed(2)} → {adj.new_threshold.toFixed(2)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">{adj.reason}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
