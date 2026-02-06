import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Leaf, DollarSign, Users, TrendingDown } from "lucide-react";

export function ImpactCalculator() {
  const [itemsPerDay, setItemsPerDay] = useState(1000);
  const [contaminationRate, setContaminationRate] = useState(15);

  // Calculate impacts
  const co2Savings = Math.round(itemsPerDay * 0.037 * (1 - contaminationRate / 100) * 10) / 10;
  const revenuePotential = Math.round(itemsPerDay * 0.15 * (1 - contaminationRate / 100));
  const laborReduction = Math.round(30 + (itemsPerDay / 100) * 2);
  const contaminationReduction = Math.round(contaminationRate * 0.7);

  return (
    <Card className="glass-card max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Estimate Your Impact</CardTitle>
      </CardHeader>
      <CardContent className="space-y-8">
        {/* Inputs */}
        <div className="space-y-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="items">Items Processed Per Day</Label>
              <span className="text-lg font-semibold text-primary">{itemsPerDay.toLocaleString()}</span>
            </div>
            <Slider
              id="items"
              min={100}
              max={10000}
              step={100}
              value={[itemsPerDay]}
              onValueChange={(v) => setItemsPerDay(v[0])}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>100</span>
              <span>10,000</span>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="contamination">Current Contamination Rate</Label>
              <span className="text-lg font-semibold text-accent">{contaminationRate}%</span>
            </div>
            <Slider
              id="contamination"
              min={5}
              max={40}
              step={1}
              value={[contaminationRate]}
              onValueChange={(v) => setContaminationRate(v[0])}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>5%</span>
              <span>40%</span>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="grid sm:grid-cols-2 gap-4 pt-6 border-t border-border/50">
          <div className="flex items-center gap-4 p-4 rounded-lg bg-primary/10 border border-primary/30">
            <div className="p-3 rounded-lg bg-primary/20">
              <Leaf className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">CO₂ Savings</p>
              <p className="text-2xl font-bold text-primary">{co2Savings} kg/day</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-lg bg-secondary/10 border border-secondary/30">
            <div className="p-3 rounded-lg bg-secondary/20">
              <DollarSign className="h-6 w-6 text-secondary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Revenue Recovery</p>
              <p className="text-2xl font-bold text-secondary">${revenuePotential}/day</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-lg bg-chart-4/10 border border-chart-4/30">
            <div className="p-3 rounded-lg bg-chart-4/20">
              <Users className="h-6 w-6 text-chart-4" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Labor Reduction</p>
              <p className="text-2xl font-bold text-chart-4">{laborReduction}%</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-lg bg-accent/10 border border-accent/30">
            <div className="p-3 rounded-lg bg-accent/20">
              <TrendingDown className="h-6 w-6 text-accent" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Contamination Reduction</p>
              <p className="text-2xl font-bold text-accent">-{contaminationReduction}%</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
