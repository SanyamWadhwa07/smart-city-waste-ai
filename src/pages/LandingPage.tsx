import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
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
  Recycle,
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
      <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-border/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary/30 to-accent/20 shine">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <span className="font-bold text-xl bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">CogniRecycle</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              Features
            </a>
            <a href="#pricing" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              Pricing
            </a>
            <a href="#calculator" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              Calculator
            </a>
            <Link to="/about" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              About
            </Link>
          </div>
          <Link to="/dashboard">
            <Button className="shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all">
              View Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 overflow-hidden">
        {/* Animated background gradient */}
        <div className="absolute inset-0 premium-gradient opacity-50" />
        
        {/* Animated particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(25)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 rounded-full bg-gradient-to-r from-primary/40 to-secondary/40 floating-particle blur-sm"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${5 + Math.random() * 5}s`,
              }}
            />
          ))}
        </div>

        <div className="container mx-auto px-4 text-center relative z-10">
          <Badge className="mb-6 bg-primary/20 text-primary border-primary/50 hover:bg-primary/30 hover:scale-105 transition-all shadow-lg">
            <Leaf className="h-3 w-3 mr-1" />
            Sustainable AI Technology
          </Badge>

          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in-up leading-tight">
            <span className="gradient-text block mb-2">Autonomous Waste Intelligence</span>
            <span className="text-foreground/90">for Smart Cities</span>
          </h1>

          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto mb-10 animate-fade-in-up leading-relaxed" style={{ animationDelay: "0.1s" }}>
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
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
            <Link to="/dashboard">
              <Button size="lg" className="gap-2 text-base px-8 py-6 shadow-2xl shadow-primary/30 hover:shadow-primary/40 hover:scale-105 transition-all">
                View Live Demo
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <a href="#features">
              <Button size="lg" variant="outline" className="gap-2 text-base px-8 py-6 hover:bg-card/80 hover:scale-105 transition-all">
                Learn More
              </Button>
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-5xl mx-auto stagger-children">
            {[
              { value: "99.2%", label: "Accuracy Rate", icon: Target },
              { value: "45kg", label: "CO₂ Saved/Day", icon: Leaf },
              { value: "$178", label: "Daily Recovery", icon: DollarSign },
              { value: "1.2K+", label: "Items/Hour", icon: Recycle },
            ].map((stat) => (
              <Card key={stat.label} className="pro-card">
                <CardContent className="p-6 text-center">
                  <stat.icon className="h-8 w-8 text-primary mx-auto mb-3" />
                  <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
                  <div className="text-sm text-muted-foreground font-medium">{stat.label}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-secondary/20 text-secondary border-secondary/50">
              Features
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Intelligent Waste Management
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Cutting-edge AI technology meets environmental sustainability
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 stagger-children">
            {features.map((feature) => (
              <Card key={feature.title} className="pro-card group">
                <CardHeader>
                  <div className="p-3 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/10 w-fit mb-4 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                    <feature.icon className="h-7 w-7 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="py-24 border-t border-border/50 bg-gradient-to-b from-transparent via-card/20 to-transparent">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-chart-4/20 text-chart-4 border-chart-4/50">
              Architecture
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              System Overview
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              From camera input to intelligent routing decisions
            </p>
          </div>
          <ArchitectureDiagram />
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-accent/20 text-accent border-accent/50">
              Deployment Options
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Start at Any Scale
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              From DIY prototypes to enterprise deployments
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto stagger-children">
            {pricingTiers.map((tier) => (
              <Card
                key={tier.name}
                className={`pro-card relative overflow-hidden ${
                  tier.highlighted ? "border-primary ring-2 ring-primary/30 shadow-2xl shadow-primary/20" : ""
                }`}
              >
                {tier.highlighted && (
                  <div className="absolute top-0 right-0 bg-gradient-to-r from-primary to-secondary text-primary-foreground text-xs font-bold px-4 py-1.5 rounded-bl-xl shine">
                    Recommended
                  </div>
                )}
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-start justify-between">
                    <span className="text-2xl">{tier.name}</span>
                    <span className="text-3xl font-bold text-primary">{tier.price}</span>
                  </CardTitle>
                  <CardDescription className="text-base">{tier.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <ul className="space-y-3">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3 text-sm">
                        <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="pt-4 border-t border-border/50">
                    <p className="text-sm text-muted-foreground leading-relaxed">{tier.outcomes}</p>
                  </div>
                  <Button 
                    className={`w-full ${
                      tier.highlighted ? "shadow-lg shadow-primary/30" : ""
                    }`} 
                    variant={tier.highlighted ? "default" : "outline"}
                    size="lg"
                  >
                    Get Started
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Impact Calculator Section */}
      <section id="calculator" className="py-24 border-t border-border/50 bg-gradient-to-b from-transparent via-card/20 to-transparent">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-primary/20 text-primary border-primary/50">
              Impact Calculator
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Calculate Your Savings
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              See the potential impact of deploying CogniRecycle at your facility
            </p>
          </div>
          <ImpactCalculator />
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 border-t border-border/50 bg-card/30">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 shine">
                  <Recycle className="h-5 w-5 text-primary" />
                </div>
                <span className="font-bold text-lg">CogniRecycle</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                AI-powered waste intelligence for a sustainable future.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-foreground">Product</h4>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li><Link to="/dashboard" className="hover:text-primary transition-colors">Dashboard</Link></li>
                <li><Link to="/analytics" className="hover:text-primary transition-colors">Analytics</Link></li>
                <li><Link to="/alerts" className="hover:text-primary transition-colors">Alerts</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-foreground">Resources</h4>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-primary transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">API Reference</a></li>
                <li><Link to="/about" className="hover:text-primary transition-colors">About</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-foreground">Connect</h4>
              <div className="flex gap-3">
                <a href="#" className="p-2.5 rounded-lg bg-muted/50 hover:bg-primary/20 hover:text-primary transition-all hover:scale-110">
                  <Github className="h-5 w-5" />
                </a>
                <a href="#" className="p-2.5 rounded-lg bg-muted/50 hover:bg-primary/20 hover:text-primary transition-all hover:scale-110">
                  <Twitter className="h-5 w-5" />
                </a>
                <a href="#" className="p-2.5 rounded-lg bg-muted/50 hover:bg-primary/20 hover:text-primary transition-all hover:scale-110">
                  <Linkedin className="h-5 w-5" />
                </a>
                <a href="#" className="p-2.5 rounded-lg bg-muted/50 hover:bg-primary/20 hover:text-primary transition-all hover:scale-110">
                  <Mail className="h-5 w-5" />
                </a>
              </div>
            </div>
          </div>
          <div className="border-t border-border/50 pt-8 text-center text-sm text-muted-foreground space-y-2">
            <p>Built with ❤️ for Smart Cities</p>
            <p>© 2024 CogniRecycle. Open source under MIT License.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
