import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Play, Pause, Square, Video, Camera, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface Detection {
  id: string;
  detector_label: string;
  classifier_label: string;
  confidence_detector: number;
  confidence_classifier: number;
  final_material: string;
  recommended_bin: string;
  decision: string;
  contamination_flag: boolean;
  reason: string;
}

interface LogMessage {
  timestamp: number;
  text: string;
}

export function VideoAnalysisViewer() {
  const [isConnected, setIsConnected] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [videoSource, setVideoSource] = useState("");
  const [useCamera, setUseCamera] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [totalFrames, setTotalFrames] = useState<number | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    totalObjects: 0,
    avgProcessingTime: 0,
    fps: 0
  });

  const wsRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const connectWebSocket = () => {
    const ws = new WebSocket("ws://localhost:8000/ws/video-analysis");
    
    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
      addLog("Connected to video analysis server");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case "metadata":
          addLog(`Video opened: ${data.width}x${data.height} @ ${data.fps?.toFixed(1)} FPS`);
          if (data.total_frames) {
            setTotalFrames(data.total_frames);
            addLog(`Total frames: ${data.total_frames}`);
          }
          setStats(prev => ({ ...prev, fps: data.fps || 0 }));
          break;
          
        case "detection":
          setCurrentFrame(data.frame_number);
          setDetections(data.detections || []);
          setStats(prev => ({
            totalObjects: prev.totalObjects + data.total_objects,
            avgProcessingTime: data.processing_time_ms,
            fps: prev.fps
          }));
          break;
          
        case "log":
          data.messages.forEach((msg: string) => addLog(msg));
          break;
          
        case "complete":
          addLog(`✓ ${data.message}`);
          setIsPlaying(false);
          break;
          
        case "error":
          setError(data.message);
          addLog(`✗ ERROR: ${data.message}`);
          setIsPlaying(false);
          break;
      }
    };

    ws.onerror = () => {
      setError("WebSocket connection error");
      addLog("✗ Connection error");
    };

    ws.onclose = () => {
      setIsConnected(false);
      setIsPlaying(false);
      addLog("Disconnected from server");
    };

    wsRef.current = ws;
  };

  const addLog = (text: string) => {
    setLogs(prev => [...prev, { timestamp: Date.now(), text }].slice(-100)); // Keep last 100 logs
  };

  const handleStart = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      connectWebSocket();
      // Wait for connection
      setTimeout(() => startAnalysis(), 500);
    } else {
      startAnalysis();
    }
  };

  const startAnalysis = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError("Not connected to server");
      return;
    }

    const source = useCamera ? 0 : videoSource;
    
    if (!useCamera && !videoSource) {
      setError("Please enter a video file path or select camera mode");
      return;
    }

    wsRef.current.send(JSON.stringify({
      action: "start",
      source: source,
      max_fps: 5
    }));

    setIsPlaying(true);
    setError(null);
    setLogs([]);
    setDetections([]);
    setCurrentFrame(0);
    addLog(`Starting analysis from: ${useCamera ? 'Camera 0' : videoSource}`);
  };

  const handleStop = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsPlaying(false);
    setIsConnected(false);
    addLog("Stopped analysis");
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Video Panel */}
      <Card className="lg:col-span-2 p-6">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Video className="h-6 w-6" />
              Video Analysis
            </h2>
            <Badge variant={isConnected ? "default" : "secondary"}>
              {isConnected ? "Connected" : "Disconnected"}
            </Badge>
          </div>

          {/* Controls */}
          <div className="space-y-3">
            <div className="flex gap-2">
              <Button
                variant={useCamera ? "default" : "outline"}
                size="sm"
                onClick={() => setUseCamera(true)}
              >
                <Camera className="h-4 w-4 mr-2" />
                Camera
              </Button>
              <Button
                variant={!useCamera ? "default" : "outline"}
                size="sm"
                onClick={() => setUseCamera(false)}
              >
                <Video className="h-4 w-4 mr-2" />
                Video File
              </Button>
            </div>

            {!useCamera && (
              <Input
                type="text"
                placeholder="Enter video file path (e.g., final.mp4, Recording.mp4)"
                value={videoSource}
                onChange={(e) => setVideoSource(e.target.value)}
                disabled={isPlaying}
              />
            )}

            <div className="flex gap-2">
              <Button
                onClick={handleStart}
                disabled={isPlaying || (!useCamera && !videoSource)}
                className="flex-1"
              >
                <Play className="h-4 w-4 mr-2" />
                Start Analysis
              </Button>
              <Button
                onClick={handleStop}
                disabled={!isPlaying}
                variant="destructive"
                className="flex-1"
              >
                <Square className="h-4 w-4 mr-2" />
                Stop
              </Button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-sm">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <span>{error}</span>
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 p-4 bg-muted/50 rounded-lg">
            <div>
              <div className="text-xs text-muted-foreground">Frame</div>
              <div className="text-lg font-semibold">
                {currentFrame}{totalFrames ? ` / ${totalFrames}` : ''}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Total Objects</div>
              <div className="text-lg font-semibold">{stats.totalObjects}</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Processing</div>
              <div className="text-lg font-semibold">{stats.avgProcessingTime.toFixed(1)}ms</div>
            </div>
          </div>

          {/* Current Detections */}
          <div>
            <h3 className="text-sm font-semibold mb-2">Current Frame Detections</h3>
            {detections.length > 0 ? (
              <div className="space-y-2">
                {detections.map((det, idx) => (
                  <div key={`${det.id}-${idx}`} className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{det.final_material}</span>
                      <Badge variant={det.contamination_flag ? "destructive" : "default"}>
                        {det.recommended_bin}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground space-y-1">
                      <div>Detector: {det.detector_label} ({(det.confidence_detector * 100).toFixed(0)}%)</div>
                      <div>Classifier: {det.classifier_label} ({(det.confidence_classifier * 100).toFixed(0)}%)</div>
                      <div className="text-xs italic">{det.reason}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground text-center py-8">
                {isPlaying ? "Waiting for detections..." : "No detections yet"}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Logs Panel */}
      <Card className="p-6">
        <h2 className="text-xl font-bold mb-4">Detection Logs</h2>
        <ScrollArea className="h-[600px] pr-4">
          <div className="space-y-1 font-mono text-xs">
            {logs.map((log, idx) => (
              <div
                key={idx}
                className={cn(
                  "p-2 rounded",
                  log.text.includes("ERROR") || log.text.includes("✗")
                    ? "bg-destructive/10 text-destructive"
                    : log.text.includes("Detected") || log.text.includes("Object")
                    ? "bg-primary/10"
                    : "bg-muted/50"
                )}
              >
                {log.text}
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </ScrollArea>
      </Card>
    </div>
  );
}
