import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Camera, Eye, GitBranch, Layers, Cpu, Target, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const flowSteps = [
  { id: "camera", label: "Camera", icon: Camera, color: "text-muted-foreground" },
  { id: "yolo", label: "YOLOv8", icon: Eye, color: "text-secondary" },
  { id: "routing", label: "Routing Agent", icon: GitBranch, color: "text-primary" },
  { id: "material", label: "Material Agent", icon: Layers, color: "text-accent" },
  { id: "decision", label: "Decision", icon: Cpu, color: "text-chart-4" },
  { id: "output", label: "Output", icon: Target, color: "text-primary" },
];

export function AgentFlow() {
  return (
    <Card className="glass-card">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <Cpu className="h-5 w-5 text-chart-4" />
          Dual-Agent Processing Flow
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap items-center justify-center gap-2 py-4">
          {flowSteps.map((step, index) => (
            <div key={step.id} className="flex items-center gap-2">
              <div className="flex flex-col items-center gap-1">
                <div
                  className={cn(
                    "p-3 rounded-lg bg-muted/50 border border-border/50 transition-all hover:scale-105 hover:bg-muted",
                    step.color
                  )}
                >
                  <step.icon className="h-5 w-5" />
                </div>
                <span className="text-xs text-muted-foreground text-center max-w-[80px]">
                  {step.label}
                </span>
              </div>
              {index < flowSteps.length - 1 && (
                <ArrowRight className="h-4 w-4 text-muted-foreground animate-pulse hidden sm:block" />
              )}
            </div>
          ))}
        </div>
        
        {/* Cross-validation indicator */}
        <div className="mt-2 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            Cross-validation active
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
