import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { binColors, DecisionEntry } from "@/lib/mockData";
import { ScrollArea } from "@/components/ui/scroll-area";
import { GitBranch, Search, ArrowRight, Signal } from "lucide-react";
import { cn } from "@/lib/utils";

type Props = {
  decisions: DecisionEntry[];
  status: "connected" | "connecting" | "error" | "mock";
};

export function DecisionStream({ decisions, status }: Props) {
  const [filter, setFilter] = useState("");

  const filteredDecisions = decisions.filter(
    (d) =>
      d.itemName.toLowerCase().includes(filter.toLowerCase()) ||
      d.bin.toLowerCase().includes(filter.toLowerCase())
  );

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <Card className="glass-card h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-secondary" />
            Decision Stream
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-secondary/20 text-secondary border-secondary/50">
              Live
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Signal className="h-3 w-3" />
              {status === "connected"
                ? "Backend"
                : status === "connecting"
                  ? "Connecting..."
                  : status === "error"
                    ? "Offline"
                    : "Simulated"}
            </Badge>
          </div>
        </div>
        <div className="relative mt-2">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Filter by item or bin type..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="pl-8 bg-muted/30 border-border/50"
          />
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px] custom-scrollbar">
          <div className="space-y-1 pr-4">
            {filteredDecisions.map((decision, index) => (
              <div
                key={decision.id}
                className={cn(
                  "flex items-center gap-2 p-2 rounded-lg font-mono-logs text-sm transition-colors hover:bg-muted/30",
                  index === 0 && "stream-item"
                )}
              >
                <span className="text-muted-foreground shrink-0">
                  [{formatTime(decision.timestamp)}]
                </span>
                <span className="truncate">{decision.itemName}</span>
                <ArrowRight className="h-3 w-3 text-muted-foreground shrink-0" />
                <Badge
                  variant="outline"
                  className={cn(
                    "shrink-0",
                    binColors[decision.bin].bg,
                    binColors[decision.bin].text,
                    "border-current"
                  )}
                >
                  {binColors[decision.bin].label}
                </Badge>
                <span className="text-muted-foreground text-xs ml-auto shrink-0">
                  {(decision.confidence * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
