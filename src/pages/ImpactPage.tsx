import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useImpactLive } from "@/hooks/useImpact";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
  Line,
  Legend,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";
import { Leaf, DollarSign, ShieldCheck, Clock } from "lucide-react";
import { format } from "date-fns";

const palette = ["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6", "#14B8A6", "#EC4899"];

export default function ImpactPage() {
  const { data, status } = useImpactLive();

  const history = data.history?.map((h) => ({
    ts: format(new Date(h.ts), "HH:mm"),
    co2: h.co2_saved,
    revenue: h.revenue,
  }));

  const materialBreakdown = Object.entries(data.by_material_co2 || {}).map(([key, value]) => ({
    name: key.replace(/_/g, " "),
    value: Math.round(value * 100) / 100,
  }));

  const revenueByMaterial = materialBreakdown.map((m, idx) => ({
    name: m.name,
    revenue: Math.round((m.value * 0.12) * 100) / 100, // crude proxy
    savings: Math.round(m.value * 10) / 10,
    fill: palette[idx % palette.length],
  }));

  return (
    <MainLayout>
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
              Impact Dashboard
            </h1>
            <p className="text-muted-foreground text-base mt-1">
              Environmental & economic impact from routing decisions
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={status === "live" ? "default" : "outline"}>
              {status === "live" ? "Live data" : status === "loading" ? "Connecting…" : "Simulated"}
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Clock className="h-4 w-4" />
              {format(new Date(data.last_updated), "MMM d, HH:mm")}
            </Badge>
          </div>
        </div>

        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
          <Card className="pro-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">CO₂ Saved</CardTitle>
              <Leaf className="h-5 w-5 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{data.total_co2_kg.toFixed(1)} kg</div>
              <p className="text-xs text-muted-foreground mt-1">
                Includes contamination prevention bonuses
              </p>
            </CardContent>
          </Card>
          <Card className="pro-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Revenue Recovered</CardTitle>
              <DollarSign className="h-5 w-5 text-secondary" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">${data.revenue_usd.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Estimated commodity value from clean material streams
              </p>
            </CardContent>
          </Card>
          <Card className="pro-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Contamination Prevented</CardTitle>
              <ShieldCheck className="h-5 w-5 text-accent" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{data.contamination_prevented}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Batches diverted before rejection
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <Card className="pro-card">
            <CardHeader>
              <CardTitle className="text-xl">CO₂ Savings Over Time</CardTitle>
              <CardDescription>Hourly savings trend with revenue overlay</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={history}>
                  <defs>
                    <linearGradient id="co2" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.05} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="ts" stroke="hsl(var(--muted-foreground))" />
                  <YAxis yAxisId="left" stroke="hsl(var(--muted-foreground))" />
                  <YAxis yAxisId="right" orientation="right" stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "10px",
                    }}
                  />
                  <Legend />
                  <Area
                    yAxisId="left"
                    type="monotone"
                    dataKey="co2"
                    name="CO₂ saved (kg)"
                    stroke="hsl(var(--primary))"
                    fill="url(#co2)"
                    strokeWidth={2}
                    activeDot={{ r: 5 }}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="revenue"
                    name="Revenue ($)"
                    stroke="hsl(var(--secondary))"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="pro-card">
            <CardHeader>
              <CardTitle className="text-xl">Revenue & Savings by Material</CardTitle>
              <CardDescription>Economic vs environmental impact by stream</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={revenueByMaterial}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
                  <YAxis stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "10px",
                    }}
                  />
                  <Legend />
                  <Bar dataKey="revenue" name="Revenue ($)" fill="hsl(var(--secondary))" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="savings" name="CO₂ (kg)" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <Card className="pro-card lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-xl">Material Composition (CO₂ share)</CardTitle>
              <CardDescription>Share of savings by material</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={materialBreakdown}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={110}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {materialBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={palette[index % palette.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "10px",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="pro-card lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-xl">Notes</CardTitle>
              <CardDescription>Live highlights from the impact model</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 mt-2 rounded-full bg-primary" />
                <div>
                  <p className="font-semibold">Adaptive contamination bonus applied</p>
                  <p className="text-sm text-muted-foreground">
                    Prevented batches contribute extra CO₂ savings and cost avoidance automatically.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 mt-2 rounded-full bg-secondary" />
                <div>
                  <p className="font-semibold">Commodity prices modeled from 2025 averages</p>
                  <p className="text-sm text-muted-foreground">
                    PET & aluminum dominate recovery value; adjust if local prices differ.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 mt-2 rounded-full bg-accent" />
                <div>
                  <p className="font-semibold">Routing stream stays synced</p>
                  <p className="text-sm text-muted-foreground">
                    Live WebSocket events keep totals aligned with the detection feed; switches to simulation on failure.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
