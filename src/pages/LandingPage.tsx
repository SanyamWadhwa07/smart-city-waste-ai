import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Recycle,
  ArrowRight,
  Eye,
  Brain,
  GitBranch,
  BarChart3,
  Zap,
  Leaf,
  DollarSign,
  Camera,
  Cpu,
  Target,
  Check,
  Github,
  Mail,
  Twitter,
  Linkedin,
} from "lucide-react";
import { pricingTiers } from "@/lib/mockData";
import { ImpactCalculator } from "@/components/landing/ImpactCalculator";
import { ArchitectureDiagram } from "@/components/landing/ArchitectureDiagram";

const features = [
  {
    icon: Eye,
    title: "Real-time Detection",
    description: "YOLOv8-powered object detection identifies waste items in milliseconds",
  },
  {
    icon: Brain,
    title: "Dual-Agent AI",
    description: "Routing and Material agents cross-validate for 99% accuracy",
  },
  {
    icon: GitBranch,
    title: "Smart Routing",
    description: "Automatic sorting into recyclable, organic, hazardous, or landfill",
  },
  {
    icon: BarChart3,
    title: "Predictive Analytics",
    description: "Forecast contamination trends before they become problems",
  },
  {
    icon: Zap,
    title: "Edge Processing",
    description: "Run entirely on affordable hardware like Raspberry Pi",
  },
  {
    icon: Leaf,
    title: "Impact Tracking",
    description: "Measure CO₂ savings and revenue recovery in real-time",
  },
];

const processSteps = [
  { label: "Detect", icon: Camera, color: "text-secondary" },
  { label: "Reason", icon: Brain, color: "text-primary" },
  { label: "Decide", icon: GitBranch, color: "text-accent" },
  { label: "Quantify", icon: BarChart3, color: "text-chart-4" },
  { label: "Improve", icon: Target, color: "text-primary" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen gradient-bg">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-border/50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-primary/20">
              <Recycle className="h-6 w-6 text-primary" />
            </div>
            <span className="font-bold text-xl">CogniRecycle</span>
          </div>
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
              Features
            </a>
            <a href="#pricing" className="text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </a>
            <a href="#calculator" className="text-muted-foreground hover:text-foreground transition-colors">
              Calculator
            </a>
            <Link to="/about" className="text-muted-foreground hover:text-foreground transition-colors">
              About
            </Link>
          </div>
          <Link to="/dashboard">
            <Button>
              View Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Animated particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 rounded-full bg-primary/30 floating-particle"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${4 + Math.random() * 4}s`,
              }}
            />
          ))}
        </div>

        <div className="container mx-auto px-4 text-center relative z-10">
          <Badge className="mb-6 bg-primary/20 text-primary border-primary/50 hover:bg-primary/30">
            <Leaf className="h-3 w-3 mr-1" />
            Sustainable AI Technology
          </Badge>

          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in-up">
            <span className="gradient-text">Autonomous Waste Intelligence</span>
            <br />
            <span className="text-foreground">for Smart Cities</span>
          </h1>

          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
            AI-powered waste sorting that reduces contamination, maximizes recycling, and saves money. Deploy on edge devices for real-time processing.
          </p>

          {/* Process Flow */}
          <div className="flex flex-wrap items-center justify-center gap-2 md:gap-4 mb-10 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
            {processSteps.map((step, index) => (
              <div key={step.label} className="flex items-center gap-2">
                <div className={`flex items-center gap-2 px-4 py-2 rounded-full bg-muted/50 border border-border/50 ${step.color}`}>
                  <step.icon className="h-4 w-4" />
                  <span className="font-medium">{step.label}</span>
                </div>
                {index < processSteps.length - 1 && (
                  <ArrowRight className="h-4 w-4 text-muted-foreground hidden md:block" />
                )}
              </div>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
            <Link to="/dashboard">
              <Button size="lg" className="gap-2">
                View Live Demo
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <a href="#features">
              <Button size="lg" variant="outline" className="gap-2">
                Learn More
              </Button>
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 max-w-4xl mx-auto stagger-children">
            {[
              { value: "87%", label: "Accuracy Rate", icon: Target },
              { value: "45kg", label: "CO₂ Saved/Day", icon: Leaf },
              { value: "$178", label: "Daily Recovery", icon: DollarSign },
              { value: "1.2K+", label: "Items/Hour", icon: Recycle },
            ].map((stat) => (
              <Card key={stat.label} className="glass-card">
                <CardContent className="p-4 text-center">
                  <stat.icon className="h-6 w-6 text-primary mx-auto mb-2" />
                  <div className="text-2xl font-bold text-primary">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <Badge className="mb-4 bg-secondary/20 text-secondary border-secondary/50">
              Features
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Intelligent Waste Management
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Cutting-edge AI technology meets environmental sustainability
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 stagger-children">
            {features.map((feature) => (
              <Card key={feature.title} className="glass-card group hover:border-primary/50 transition-colors">
                <CardHeader>
                  <div className="p-3 rounded-lg bg-primary/20 w-fit mb-2 group-hover:scale-110 transition-transform">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="py-20 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <Badge className="mb-4 bg-chart-4/20 text-chart-4 border-chart-4/50">
              Architecture
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              System Overview
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              From camera input to intelligent routing decisions
            </p>
          </div>
          <ArchitectureDiagram />
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <Badge className="mb-4 bg-accent/20 text-accent border-accent/50">
              Deployment Options
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Start at Any Scale
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              From DIY prototypes to enterprise deployments
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto stagger-children">
            {pricingTiers.map((tier) => (
              <Card
                key={tier.name}
                className={`glass-card relative overflow-hidden ${
                  tier.highlighted ? "border-primary ring-2 ring-primary/20" : ""
                }`}
              >
                {tier.highlighted && (
                  <div className="absolute top-0 right-0 bg-primary text-primary-foreground text-xs font-medium px-3 py-1 rounded-bl-lg">
                    Recommended
                  </div>
                )}
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    {tier.name}
                    <span className="text-2xl font-bold text-primary">{tier.price}</span>
                  </CardTitle>
                  <CardDescription>{tier.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <ul className="space-y-2">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2 text-sm">
                        <Check className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="pt-4 border-t border-border/50">
                    <p className="text-sm text-muted-foreground">{tier.outcomes}</p>
                  </div>
                  <Button className="w-full" variant={tier.highlighted ? "default" : "outline"}>
                    Get Started
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Impact Calculator Section */}
      <section id="calculator" className="py-20 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <Badge className="mb-4 bg-primary/20 text-primary border-primary/50">
              Impact Calculator
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Calculate Your Savings
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              See the potential impact of deploying CogniRecycle at your facility
            </p>
          </div>
          <ImpactCalculator />
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 rounded-lg bg-primary/20">
                  <Recycle className="h-5 w-5 text-primary" />
                </div>
                <span className="font-bold text-lg">CogniRecycle</span>
              </div>
              <p className="text-sm text-muted-foreground">
                AI-powered waste intelligence for a sustainable future.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="/dashboard" className="hover:text-foreground transition-colors">Dashboard</Link></li>
                <li><Link to="/analytics" className="hover:text-foreground transition-colors">Analytics</Link></li>
                <li><Link to="/alerts" className="hover:text-foreground transition-colors">Alerts</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">API Reference</a></li>
                <li><Link to="/about" className="hover:text-foreground transition-colors">About</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Connect</h4>
              <div className="flex gap-3">
                <a href="#" className="p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                  <Github className="h-5 w-5" />
                </a>
                <a href="#" className="p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                  <Twitter className="h-5 w-5" />
                </a>
                <a href="#" className="p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                  <Linkedin className="h-5 w-5" />
                </a>
                <a href="#" className="p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                  <Mail className="h-5 w-5" />
                </a>
              </div>
            </div>
          </div>
          <div className="border-t border-border/50 pt-8 text-center text-sm text-muted-foreground">
            <p>Built with ❤️ for Smart Cities</p>
            <p className="mt-2">© 2024 CogniRecycle. Open source under MIT License.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
