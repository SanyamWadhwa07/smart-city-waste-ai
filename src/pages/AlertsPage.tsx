import { useState } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { generateAlerts, Alert } from "@/lib/mockData";
import {
  AlertTriangle,
  AlertCircle,
  Info,
  Search,
  CheckCircle,
  X,
  Filter,
  TrendingUp,
  DollarSign,
  Leaf,
} from "lucide-react";
import { cn } from "@/lib/utils";

const alertIcons = {
  warning: AlertTriangle,
  critical: AlertCircle,
  info: Info,
};

const alertStyles = {
  warning: {
    badge: "bg-accent/20 text-accent border-accent/50",
    icon: "text-accent",
  },
  critical: {
    badge: "bg-destructive/20 text-destructive border-destructive/50",
    icon: "text-destructive",
  },
  info: {
    badge: "bg-secondary/20 text-secondary border-secondary/50",
    icon: "text-secondary",
  },
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>(generateAlerts());
  const [filter, setFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSearch =
      alert.title.toLowerCase().includes(filter.toLowerCase()) ||
      alert.message.toLowerCase().includes(filter.toLowerCase());
    const matchesType = typeFilter === "all" || alert.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const handleResolve = (id: string) => {
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === id ? { ...alert, resolved: true } : alert
      )
    );
  };

  const handleDismiss = (id: string) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== id));
    if (selectedAlert?.id === id) {
      setSelectedAlert(null);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">Alert History</h1>
            <p className="text-muted-foreground">Monitor and manage contamination alerts</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-destructive/20 text-destructive border-destructive/50">
              {alerts.filter((a) => a.type === "critical" && !a.resolved).length} Critical
            </Badge>
            <Badge variant="outline" className="bg-accent/20 text-accent border-accent/50">
              {alerts.filter((a) => a.type === "warning" && !a.resolved).length} Warnings
            </Badge>
          </div>
        </div>

        {/* Filters */}
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search alerts..."
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="pl-9 bg-muted/30"
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-[150px] bg-muted/30">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Filter type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Alerts Table */}
          <Card className="glass-card lg:col-span-2">
            <CardHeader className="pb-0">
              <CardTitle>Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead className="hidden md:table-cell">Time</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAlerts.map((alert) => {
                    const Icon = alertIcons[alert.type];
                    const styles = alertStyles[alert.type];

                    return (
                      <TableRow
                        key={alert.id}
                        className={cn(
                          "cursor-pointer hover:bg-muted/30",
                          selectedAlert?.id === alert.id && "bg-muted/50"
                        )}
                        onClick={() => setSelectedAlert(alert)}
                      >
                        <TableCell>
                          <Badge variant="outline" className={styles.badge}>
                            <Icon className={cn("h-3 w-3 mr-1", styles.icon)} />
                            {alert.type}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-medium max-w-[200px] truncate">
                          {alert.title}
                        </TableCell>
                        <TableCell className="hidden md:table-cell text-muted-foreground">
                          {formatDate(alert.timestamp)} {formatTime(alert.timestamp)}
                        </TableCell>
                        <TableCell>
                          {alert.resolved ? (
                            <Badge variant="outline" className="bg-primary/20 text-primary border-primary/50">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Resolved
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="bg-muted/50">
                              Active
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-1">
                            {!alert.resolved && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleResolve(alert.id);
                                }}
                              >
                                <CheckCircle className="h-4 w-4 text-primary" />
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDismiss(alert.id);
                              }}
                            >
                              <X className="h-4 w-4 text-muted-foreground" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                  {filteredAlerts.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        No alerts found
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Alert Details */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle>Alert Details</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedAlert ? (
                <div className="space-y-4">
                  <div>
                    <Badge
                      variant="outline"
                      className={alertStyles[selectedAlert.type].badge}
                    >
                      {selectedAlert.type.toUpperCase()}
                    </Badge>
                    <h3 className="mt-2 font-semibold text-lg">{selectedAlert.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {selectedAlert.message}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-lg bg-muted/30">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                        <TrendingUp className="h-4 w-4" />
                        Rate Change
                      </div>
                      <p className="font-semibold">
                        {selectedAlert.historicalRate}% → {selectedAlert.currentRate}%
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/30">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                        <DollarSign className="h-4 w-4" />
                        Daily Impact
                      </div>
                      <p className={cn("font-semibold", selectedAlert.impactDaily < 0 ? "text-destructive" : "text-primary")}>
                        ${selectedAlert.impactDaily}/day
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/30 col-span-2">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                        <Leaf className="h-4 w-4" />
                        CO₂ Impact
                      </div>
                      <p className={cn("font-semibold", selectedAlert.co2Impact < 0 ? "text-destructive" : "text-primary")}>
                        {selectedAlert.co2Impact} kg/day
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-medium">Likely Cause</h4>
                    <p className="text-sm text-muted-foreground">{selectedAlert.likelyCause}</p>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-medium">Recommendation</h4>
                    <p className="text-sm text-primary">{selectedAlert.recommendation}</p>
                  </div>

                  <div className="flex gap-2 pt-4 border-t border-border/50">
                    {!selectedAlert.resolved && (
                      <Button
                        className="flex-1"
                        onClick={() => handleResolve(selectedAlert.id)}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Mark Resolved
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleDismiss(selectedAlert.id)}
                    >
                      <X className="h-4 w-4 mr-2" />
                      Dismiss
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Select an alert to view details</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
