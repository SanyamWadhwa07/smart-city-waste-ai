import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Detection } from "@/lib/mockData";
import { getWasteColor, getWasteBg } from "@/lib/wasteColors";
import { Video, Wifi, Signal } from "lucide-react";
import { cn } from "@/lib/utils";

type Props = {
  detections: Detection[];
  status: "connected" | "connecting" | "error" | "mock";
  frame?: string; // Base64 encoded frame
};

export function DetectionFeed({ detections, status, frame }: Props) {
  const statusLabel =
    status === "connected"
      ? "Backend"
      : status === "connecting"
        ? "Connecting..."
        : status === "error"
          ? "Offline (simulated)"
          : "Simulated";

  return (
    <Card className="pro-card h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Video className="h-5 w-5 text-primary" />
            Live Detection Feed
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-primary/20 text-primary border-primary/50">
              <Wifi className="h-3 w-3 mr-1 animate-pulse" />
              30 FPS
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Signal className="h-3 w-3" />
              {statusLabel}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Video feed */}
        <div className="relative aspect-video bg-muted/30 rounded-lg overflow-hidden border border-border/50">
          {/* Show actual camera frame if available, otherwise show simulation */}
          {frame ? (
            <img 
              src={`data:image/jpeg;base64,${frame}`} 
              alt="Live camera feed"
              className="absolute inset-0 w-full h-full object-cover"
            />
          ) : (
            /* Grid overlay to simulate video */
            <>
              <div className="absolute inset-0 bg-gradient-to-br from-muted/20 to-muted/40">
                <div
                  className="absolute inset-0"
                  style={{
                    backgroundImage: `
                      linear-gradient(to right, hsl(var(--border) / 0.1) 1px, transparent 1px),
                      linear-gradient(to bottom, hsl(var(--border) / 0.1) 1px, transparent 1px)
                    `,
                    backgroundSize: "40px 40px",
                  }}
                />
              </div>

              {/* Conveyor belt simulation */}
              <div className="absolute inset-x-0 top-1/2 h-16 -translate-y-1/2 bg-muted/40 border-y border-border/30">
                <div className="absolute inset-0 flex items-center">
                  <div
                    className="w-full h-full"
                    style={{
                      backgroundImage: `repeating-linear-gradient(
                        90deg,
                        transparent,
                        transparent 20px,
                        hsl(var(--border) / 0.2) 20px,
                        hsl(var(--border) / 0.2) 21px
                      )`,
                      animation: "scroll-left 2s linear infinite",
                    }}
                  />
                </div>
              </div>
            </>
          )}

          {/* Detection bounding boxes */}
          {detections.map((detection) => {
            const wasteType = detection.item.category.toLowerCase() as any;
            return (
              <div
                key={detection.id}
                className="absolute detection-glow"
                style={{
                  left: `${detection.x}%`,
                  top: `${detection.y}%`,
                  width: `${detection.width}%`,
                  height: `${detection.height}%`,
                }}
              >
                <div
                  className={cn(
                    "absolute inset-0 border-2 rounded",
                    getWasteColor(wasteType),
                    "border-current"
                  )}
                />
                <div
                  className={cn(
                    "absolute -top-6 left-0 px-2 py-0.5 rounded text-xs font-medium whitespace-nowrap",
                    getWasteBg(wasteType),
                    getWasteColor(wasteType),
                    "border border-current"
                  )}
                >
                  {detection.item.name} ({(detection.confidence * 100).toFixed(0)}%)
                </div>
              </div>
            );
          })}

          {/* Camera watermark */}
          <div className="absolute bottom-2 left-2 text-xs text-muted-foreground font-mono-logs">
            CAM-01 | {new Date().toLocaleTimeString()}
          </div>

          {/* Recording indicator */}
          <div className="absolute top-2 right-2 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
            <span className="text-xs text-muted-foreground font-mono-logs">REC</span>
          </div>
        </div>

        <style>{`
          @keyframes scroll-left {
            from { background-position: 0 0; }
            to { background-position: -21px 0; }
          }
        `}</style>
      </CardContent>
    </Card>
  );
}
