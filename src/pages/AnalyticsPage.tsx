import { useState, useMemo, useEffect } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { chartColors } from "@/lib/wasteColors";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import {
  generateContaminationTrend,
  generateWasteDistribution,
  generateCategoryData,
  generateAccuracyOverTime,
} from "@/lib/mockData";
import { TrendingUp, Download, Calendar } from "lucide-react";

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState("7d");
  
  const contaminationData = useMemo(() => generateContaminationTrend(), []);
  const wasteDistribution = useMemo(() => generateWasteDistribution(), []);
  const categoryData = useMemo(() => generateCategoryData(), []);
  const accuracyData = useMemo(() => generateAccuracyOverTime(), []);

  const handleExport = () => {
    // Simulate PDF export
    const data = {
      contaminationData,
      wasteDistribution,
      categoryData,
      accuracyData,
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cognirecycle-report-${dateRange}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">Analytics</h1>
            <p className="text-muted-foreground text-base mt-1">Performance insights and trends</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={dateRange} onValueChange={setDateRange}>
              <SelectTrigger className="w-[160px] bg-card shadow-sm hover:shadow-md transition-shadow">
                <Calendar className="h-4 w-4 mr-2 text-primary" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24h">Last 24 hours</SelectItem>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={handleExport} className="shadow-sm hover:shadow-md transition-all">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Contamination Trends */}
          <Card className="pro-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2 text-xl">
                    <TrendingUp className="h-5 w-5 text-accent" />
                    Contamination Trends
                  </CardTitle>
                  <CardDescription className="mt-1">Daily contamination rate vs baseline</CardDescription>
                </div>
                <Badge variant="outline" className="bg-accent/20 text-accent border-accent/50">
                  {dateRange === "7d" ? "7 Days" : dateRange}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={contaminationData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} unit="%" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="rate"
                    stroke={chartColors.warning}
                    strokeWidth={2}
                    dot={{ fill: chartColors.warning }}
                    name="Contamination Rate"
                  />
                  <Line
                    type="monotone"
                    dataKey="baseline"
                    stroke="hsl(var(--muted-foreground))"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    name="Baseline"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Waste Distribution */}
          <Card className="pro-card">
            <CardHeader>
              <CardTitle className="text-xl">Waste Stream Distribution</CardTitle>
              <CardDescription className="mt-1">Breakdown by destination type</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={wasteDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {wasteDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Items by Category */}
          <Card className="pro-card">
            <CardHeader>
              <CardTitle className="text-xl">Items by Category</CardTitle>
              <CardDescription className="mt-1">Total items processed by material type</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="category" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Bar dataKey="count" fill={chartColors.primary} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Accuracy Over Time */}
          <Card className="pro-card">
            <CardHeader>
              <CardTitle className="text-xl">System Accuracy</CardTitle>
              <CardDescription className="mt-1">Accuracy percentage throughout the day</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={accuracyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis 
                    dataKey="hour" 
                    stroke="hsl(var(--muted-foreground))" 
                    fontSize={12}
                    tickFormatter={(value) => value.split(":")[0]}
                  />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} domain={[70, 100]} unit="%" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <defs>
                    <linearGradient id="accuracyGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={chartColors.success} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={chartColors.success} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="accuracy"
                    stroke={chartColors.success}
                    strokeWidth={2}
                    fill="url(#accuracyGradient)"
                    name="Accuracy"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
