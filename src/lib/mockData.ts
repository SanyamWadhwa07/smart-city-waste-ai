// Waste item types
export const wasteItems = [
  { name: "Plastic Bottle", category: "Plastic", bin: "recyclable" as const },
  { name: "Paper Cup", category: "Paper", bin: "recyclable" as const },
  { name: "Food Container", category: "Plastic", bin: "recyclable" as const },
  { name: "Aluminum Can", category: "Metal", bin: "recyclable" as const },
  { name: "Glass Bottle", category: "Glass", bin: "recyclable" as const },
  { name: "Cardboard Box", category: "Paper", bin: "recyclable" as const },
  { name: "Apple Core", category: "Organic", bin: "organic" as const },
  { name: "Banana Peel", category: "Organic", bin: "organic" as const },
  { name: "Coffee Grounds", category: "Organic", bin: "organic" as const },
  { name: "Food Scraps", category: "Organic", bin: "organic" as const },
  { name: "Styrofoam Cup", category: "Mixed", bin: "landfill" as const },
  { name: "Chip Bag", category: "Mixed", bin: "landfill" as const },
  { name: "Dirty Napkin", category: "Mixed", bin: "landfill" as const },
  { name: "Battery", category: "Hazardous", bin: "hazardous" as const },
  { name: "Paint Can", category: "Hazardous", bin: "hazardous" as const },
  { name: "Unknown Object", category: "Unknown", bin: "manual" as const },
  { name: "Contaminated Item", category: "Mixed", bin: "manual" as const },
];

export type BinType = "recyclable" | "organic" | "landfill" | "hazardous" | "manual";

export const binColors: Record<BinType, { bg: string; text: string; label: string }> = {
  recyclable: { bg: "bg-secondary/20", text: "bin-recyclable", label: "Recyclable" },
  organic: { bg: "bg-primary/20", text: "bin-organic", label: "Organic" },
  landfill: { bg: "bg-muted/40", text: "bin-landfill", label: "Landfill" },
  hazardous: { bg: "bg-accent/20", text: "bin-hazardous", label: "Hazardous" },
  manual: { bg: "bg-destructive/20", text: "bin-manual", label: "Manual Inspection" },
};

// Generate random confidence score
export const generateConfidence = (): number => {
  return Math.round((0.85 + Math.random() * 0.14) * 100) / 100;
};

// Generate random detection
export interface Detection {
  id: string;
  item: typeof wasteItems[number];
  confidence: number;
  timestamp: Date;
  x: number;
  y: number;
  width: number;
  height: number;
}

export const generateDetection = (): Detection => {
  const item = wasteItems[Math.floor(Math.random() * wasteItems.length)];
  return {
    id: Math.random().toString(36).substr(2, 9),
    item,
    confidence: generateConfidence(),
    timestamp: new Date(),
    x: 10 + Math.random() * 60,
    y: 10 + Math.random() * 60,
    width: 15 + Math.random() * 15,
    height: 15 + Math.random() * 15,
  };
};

// Generate decision stream entry
export interface DecisionEntry {
  id: string;
  timestamp: Date;
  itemName: string;
  bin: BinType;
  confidence: number;
}

export const generateDecisionEntry = (): DecisionEntry => {
  const item = wasteItems[Math.floor(Math.random() * wasteItems.length)];
  return {
    id: Math.random().toString(36).substr(2, 9),
    timestamp: new Date(),
    itemName: item.name,
    bin: item.bin,
    confidence: generateConfidence(),
  };
};

// Initial metrics
export interface Metrics {
  itemsProcessed: number;
  contaminationAlerts: number;
  accuracy: number;
  accuracyTrend: number;
  efficiencyScore: number;
  co2Saved: number;
  recoveryValue: number;
}

export const initialMetrics: Metrics = {
  itemsProcessed: 1247,
  contaminationAlerts: 34,
  accuracy: 87.3,
  accuracyTrend: 4.2,
  efficiencyScore: 82,
  co2Saved: 45.7,
  recoveryValue: 178,
};

// Chart data generators
export const generateContaminationTrend = () => {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return days.map((day) => ({
    day,
    rate: Math.round((8 + Math.random() * 12) * 10) / 10,
    baseline: 12,
  }));
};

export const generateWasteDistribution = () => [
  { name: "Recyclable", value: 45, fill: "hsl(var(--secondary))" },
  { name: "Organic", value: 25, fill: "hsl(var(--primary))" },
  { name: "Landfill", value: 20, fill: "hsl(var(--muted))" },
  { name: "Hazardous", value: 5, fill: "hsl(var(--accent))" },
  { name: "Manual", value: 5, fill: "hsl(var(--destructive))" },
];

export const generateCategoryData = () => [
  { category: "Plastic", count: 423 },
  { category: "Paper", count: 312 },
  { category: "Metal", count: 189 },
  { category: "Glass", count: 156 },
  { category: "Organic", count: 287 },
  { category: "Mixed", count: 98 },
];

export const generateAccuracyOverTime = () => {
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);
  let accuracy = 82;
  return hours.map((hour) => {
    accuracy = Math.min(95, Math.max(75, accuracy + (Math.random() - 0.4) * 3));
    return {
      hour,
      accuracy: Math.round(accuracy * 10) / 10,
    };
  });
};

// Alert types
export interface Alert {
  id: string;
  type: "warning" | "critical" | "info";
  title: string;
  message: string;
  currentRate: number;
  historicalRate: number;
  likelyCause: string;
  recommendation: string;
  impactDaily: number;
  co2Impact: number;
  timestamp: Date;
  resolved: boolean;
}

export const generateAlerts = (): Alert[] => [
  {
    id: "1",
    type: "warning",
    title: "Plastic Stream Contamination Rising",
    message: "Contamination rate increasing above threshold",
    currentRate: 31,
    historicalRate: 12,
    likelyCause: "Food containers during lunch hours (11 AM - 2 PM)",
    recommendation: "Deploy secondary inspection",
    impactDaily: -47,
    co2Impact: -23,
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    resolved: false,
  },
  {
    id: "2",
    type: "critical",
    title: "Hazardous Material Detected",
    message: "Battery found in recyclable stream",
    currentRate: 5,
    historicalRate: 1,
    likelyCause: "Improper disposal at Station 3",
    recommendation: "Immediate manual intervention required",
    impactDaily: -120,
    co2Impact: -45,
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    resolved: false,
  },
  {
    id: "3",
    type: "info",
    title: "System Performance Update",
    message: "Model accuracy improved by 2.3%",
    currentRate: 89.3,
    historicalRate: 87,
    likelyCause: "Recent model retraining",
    recommendation: "Continue monitoring",
    impactDaily: 15,
    co2Impact: 8,
    timestamp: new Date(Date.now() - 1000 * 60 * 60),
    resolved: true,
  },
];

// Pricing tiers
export const pricingTiers = [
  {
    name: "Budget",
    price: "$0-15",
    description: "Use existing hardware",
    features: [
      "Existing webcam + laptop",
      "Basic detection model",
      "Local processing",
      "Community support",
    ],
    outcomes: "~500 items/day capacity",
    highlighted: false,
  },
  {
    name: "Standard",
    price: "$93",
    description: "Optimized for small facilities",
    features: [
      "HD Webcam ($43)",
      "Raspberry Pi 4 ($50)",
      "Full detection model",
      "Real-time analytics",
      "Email support",
    ],
    outcomes: "~2,000 items/day capacity",
    highlighted: true,
  },
  {
    name: "Professional",
    price: "$154",
    description: "Enterprise-grade solution",
    features: [
      "IP Camera ($61)",
      "Jetson Nano/Edge ($93)",
      "Multi-stream support",
      "Cloud backup",
      "Priority support",
      "Custom model training",
    ],
    outcomes: "~10,000+ items/day capacity",
    highlighted: false,
  },
];

// Architecture nodes
export const architectureNodes = [
  { id: "camera", label: "Camera Input", icon: "Camera" },
  { id: "yolo", label: "YOLOv8 Detection", icon: "Eye" },
  { id: "routing", label: "Routing Agent", icon: "GitBranch" },
  { id: "material", label: "Material Agent", icon: "Layers" },
  { id: "decision", label: "Decision Engine", icon: "Cpu" },
  { id: "output", label: "Output", icon: "Target" },
];
