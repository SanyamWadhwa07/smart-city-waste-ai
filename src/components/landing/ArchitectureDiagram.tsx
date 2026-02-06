import { Card, CardContent } from "@/components/ui/card";
import { Camera, Eye, GitBranch, Layers, Cpu, Target, Database, Monitor, ArrowRight, ArrowDown } from "lucide-react";

const layers = [
  {
    title: "Edge Devices",
    items: [
      { icon: Camera, label: "IP Camera" },
      { icon: Cpu, label: "Raspberry Pi / Jetson" },
    ],
    color: "border-muted-foreground",
    bgColor: "bg-muted/30",
  },
  {
    title: "Processing Layer",
    items: [
      { icon: Eye, label: "YOLOv8 Detection" },
      { icon: GitBranch, label: "Routing Agent" },
      { icon: Layers, label: "Material Agent" },
    ],
    color: "border-primary",
    bgColor: "bg-primary/10",
  },
  {
    title: "Backend",
    items: [
      { icon: Cpu, label: "FastAPI Server" },
      { icon: Database, label: "PostgreSQL" },
    ],
    color: "border-secondary",
    bgColor: "bg-secondary/10",
  },
  {
    title: "Frontend",
    items: [
      { icon: Monitor, label: "React Dashboard" },
      { icon: Target, label: "Real-time Metrics" },
    ],
    color: "border-chart-4",
    bgColor: "bg-chart-4/10",
  },
];

export function ArchitectureDiagram() {
  return (
    <Card className="glass-card max-w-4xl mx-auto overflow-hidden">
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
