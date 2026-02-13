import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Camera, Eye, Brain, GitBranch, Target, Cpu, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const flowSteps = [
  { 
    id: "camera", 
    label: "Camera", 
    icon: Camera, 
    color: "text-blue-500",
    description: "Video Input"
  },
  { 
    id: "detector", 
    label: "Detector", 
    icon: Eye, 
    color: "text-green-500",
    description: "YOLOv8 Detection"
  },
  { 
    id: "classifier", 
    label: "Classifier", 
    icon: Brain, 
    color: "text-purple-500",
    description: "SigLIP Material"
  },
  { 
    id: "decision", 
    label: "Decision", 
    icon: Cpu, 
    color: "text-orange-500",
    description: "Conflict Resolution"
  },
  { 
    id: "routing", 
    label: "Routing", 
    icon: GitBranch, 
    color: "text-cyan-500",
    description: "Bin Selection"
  },
  { 
    id: "output", 
    label: "Output", 
    icon: Target, 
    color: "text-pink-500",
    description: "Final Result"
  },
];

export function AgentFlow() {
  return (
    <Card className="pro-card">
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
                    "p-3 rounded-lg bg-muted/50 border-2 transition-all hover:scale-105 hover:bg-muted hover:shadow-lg",
                    step.color
                  )}
                  title={step.description}
                >
                  <step.icon className="h-5 w-5" />
                </div>
                <span className="text-xs font-medium text-center max-w-[80px]">
                  {step.label}
                </span>
                <span className="text-[10px] text-muted-foreground text-center max-w-[80px]">
                  {step.description}
                </span>
              </div>
              {index < flowSteps.length - 1 && (
                <ArrowRight className="h-4 w-4 text-muted-foreground animate-pulse hidden sm:block mt-[-20px]" />
              )}
            </div>
          ))}
        </div>
        
        {/* Pipeline info */}
        <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 text-green-500 text-xs">
            <Eye className="h-3 w-3" />
            Stage 1: Detection
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/10 text-purple-500 text-xs">
            <Brain className="h-3 w-3" />
            Stage 2: Classification
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            Cross-validation active
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
