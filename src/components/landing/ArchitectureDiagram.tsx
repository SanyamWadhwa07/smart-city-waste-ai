import { Card, CardContent } from "@/components/ui/card";
import { Camera, Eye, GitBranch, Layers, Cpu, Target, AlertTriangle, TrendingUp, ArrowRight, ArrowDown, Recycle } from "lucide-react";

const layers = [
  {
    title: "Edge Devices",
    items: [
      { icon: Camera, label: "Conveyor Belt Camera" },
      { icon: Cpu, label: "Edge Processor" },
    ],
    color: "border-muted-foreground",
    bgColor: "bg-muted/20",
  },
  {
    title: "Dual-Agent Processing",
    items: [
      { icon: Eye, label: "Object Detection (6 classes)" },
      { icon: GitBranch, label: "Agent A: Primary Detector" },
      { icon: Layers, label: "Agent B: Material Classifier" },
      { icon: Target, label: "Cross-Validation Engine" },
    ],
    color: "border-primary",
    bgColor: "bg-primary/10",
  },
  {
    title: "Backend Intelligence",
    items: [
      { icon: Cpu, label: "Decision Engine + WebSocket" },
      { icon: AlertTriangle, label: "Contamination Monitor" },
      { icon: TrendingUp, label: "Impact Tracking" },
    ],
    color: "border-success",
    bgColor: "bg-success/10",
  },
  {
    title: "Live Dashboard",
    items: [
      { icon: Recycle, label: "Detection Feed + Routing" },
      { icon: AlertTriangle, label: "Contamination Alerts" },
    ],
    color: "border-accent",
    bgColor: "bg-accent/10",
  },
];

export function ArchitectureDiagram() {
  return (
    <Card className="pro-card max-w-4xl mx-auto overflow-hidden">
      <CardContent className="p-6">
        <div className="space-y-4">
          {layers.map((layer, layerIndex) => (
            <div key={layer.title}>
              {/* Layer */}
              <div className={`rounded-lg border-2 ${layer.color} ${layer.bgColor} p-4`}>
                <h4 className="text-sm font-semibold text-muted-foreground mb-3">
                  {layer.title}
                </h4>
                <div className="flex flex-wrap items-center justify-center gap-4">
                  {layer.items.map((item, itemIndex) => (
                    <div key={item.label} className="flex items-center gap-2">
                      <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-card border border-border/50">
                        <item.icon className="h-5 w-5 text-foreground" />
                        <span className="text-sm font-medium">{item.label}</span>
                      </div>
                      {itemIndex < layer.items.length - 1 && (
                        <ArrowRight className="h-4 w-4 text-muted-foreground hidden sm:block" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Arrow between layers */}
              {layerIndex < layers.length - 1 && (
                <div className="flex justify-center py-2">
                  <ArrowDown className="h-6 w-6 text-muted-foreground animate-bounce" />
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
