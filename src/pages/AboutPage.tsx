import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sparkles,
  Target,
  Leaf,
  Users,
  Github,
  ExternalLink,
  Code,
  Database,
  Cpu,
  Eye,
  GitBranch,
} from "lucide-react";

const techStack = [
  { name: "React", description: "Frontend framework", icon: Code },
  { name: "TypeScript", description: "Type safety", icon: Code },
  { name: "YOLOv8", description: "Object detection", icon: Eye },
  { name: "FastAPI", description: "Backend API", icon: Cpu },
  { name: "PostgreSQL", description: "Database", icon: Database },
  { name: "LangGraph", description: "Agent orchestration", icon: GitBranch },
];

const team = [
  { name: "AI Research Lead", role: "Model Development" },
  { name: "Full Stack Engineer", role: "Dashboard & Integration" },
  { name: "MLOps Engineer", role: "Edge Deployment" },
];

export default function AboutPage() {
  return (
    <MainLayout>
      <div className="space-y-10 max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center p-5 rounded-2xl bg-gradient-to-br from-primary/30 to-accent/20 mb-6 shine">
            <Sparkles className="h-14 w-14 text-primary" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
            About CogniRecycle
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Building intelligent waste management systems that reduce contamination, 
            maximize recycling rates, and contribute to a sustainable future.
          </p>
        </div>

        {/* Mission */}
        <Card className="pro-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Target className="h-6 w-6 text-primary" />
              Our Mission
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground leading-relaxed">
              Recycling contamination costs municipalities and waste processors billions annually, 
              while sending recoverable materials to landfills. Traditional manual sorting is 
              expensive, error-prone, and cannot scale to meet growing waste volumes.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              CogniRecycle uses advanced computer vision and multi-agent AI to automate waste 
              classification at the point of disposal. Our dual-agent architecture cross-validates 
              decisions for near-perfect accuracy, while edge deployment makes it affordable for 
              any scale of operation.
            </p>
            <div className="flex flex-wrap gap-2 pt-4">
              <Badge className="bg-primary/20 text-primary border-primary/50 hover:scale-105 transition-transform">
                <Leaf className="h-3 w-3 mr-1" />
                Environmental Impact
              </Badge>
              <Badge className="bg-secondary/20 text-secondary border-secondary/50 hover:scale-105 transition-transform">
                <Cpu className="h-3 w-3 mr-1" />
                Edge AI
              </Badge>
              <Badge className="bg-accent/20 text-accent border-accent/50 hover:scale-105 transition-transform">
                <Eye className="h-3 w-3 mr-1" />
                Computer Vision
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Technology Stack */}
        <Card className="pro-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Code className="h-6 w-6 text-secondary" />
              Technology Stack
            </CardTitle>
            <CardDescription className="text-base mt-2">
              Built with modern, scalable technologies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
              {techStack.map((tech) => (
                <div
                  key={tech.name}
                  className="flex items-center gap-3 p-4 rounded-xl bg-muted/30 border border-border/50 hover:border-secondary/50 hover:shadow-lg transition-all hover:-translate-y-1"
                >
                  <div className="p-2.5 rounded-lg bg-gradient-to-br from-secondary/20 to-secondary/10">
                    <tech.icon className="h-5 w-5 text-secondary" />
                  </div>
                  <div>
                    <p className="font-semibold">{tech.name}</p>
                    <p className="text-xs text-muted-foreground">{tech.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Team */}
        <Card className="pro-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Users className="h-6 w-6 text-chart-4" />
              Team
            </CardTitle>
            <CardDescription className="text-base mt-2">
              The people behind CogniRecycle
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-3 gap-6">
              {team.map((member) => (
                <div
                  key={member.name}
                  className="text-center p-6 rounded-xl bg-muted/30 border border-border/50 hover:border-primary/30 hover:shadow-lg transition-all hover:-translate-y-1"
                >
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary via-secondary to-accent mx-auto mb-4 flex items-center justify-center ring-4 ring-background">
                    <Users className="h-10 w-10 text-primary-foreground" />
                  </div>
                  <p className="font-semibold text-lg">{member.name}</p>
                  <p className="text-sm text-muted-foreground mt-1">{member.role}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Links */}
        <Card className="pro-card">
          <CardHeader>
            <CardTitle className="text-2xl">Resources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button variant="outline" className="gap-2 hover:scale-105 transition-transform" size="lg" asChild>
                <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4" />
                  GitHub Repository
                  <ExternalLink className="h-3 w-3" />
                </a>
              </Button>
              <Button variant="outline" className="gap-2 hover:scale-105 transition-transform" size="lg" asChild>
                <a href="#" target="_blank" rel="noopener noreferrer">
                  <Code className="h-4 w-4" />
                  API Documentation
                  <ExternalLink className="h-3 w-3" />
                </a>
              </Button>
              <Button variant="outline" className="gap-2 hover:scale-105 transition-transform" size="lg" asChild>
                <a href="mailto:contact@cognirecycle.ai">
                  Contact Us
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground py-8 space-y-2">
          <p className="font-medium">CogniRecycle © 2024 • Open Source under MIT License</p>
          <p>Built with ❤️ for Smart Cities</p>
        </div>
      </div>
    </MainLayout>
  );
}
