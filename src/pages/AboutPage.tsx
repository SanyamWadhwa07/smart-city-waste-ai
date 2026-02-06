import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Recycle,
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
      <div className="space-y-8 max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center p-4 rounded-2xl bg-primary/20 mb-6">
            <Recycle className="h-12 w-12 text-primary" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            About CogniRecycle
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Building intelligent waste management systems that reduce contamination, 
            maximize recycling rates, and contribute to a sustainable future.
          </p>
        </div>

        {/* Mission */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Our Mission
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Recycling contamination costs municipalities and waste processors billions annually, 
              while sending recoverable materials to landfills. Traditional manual sorting is 
              expensive, error-prone, and cannot scale to meet growing waste volumes.
            </p>
            <p className="text-muted-foreground">
              CogniRecycle uses advanced computer vision and multi-agent AI to automate waste 
              classification at the point of disposal. Our dual-agent architecture cross-validates 
              decisions for near-perfect accuracy, while edge deployment makes it affordable for 
              any scale of operation.
            </p>
            <div className="flex flex-wrap gap-2 pt-4">
              <Badge className="bg-primary/20 text-primary border-primary/50">
                <Leaf className="h-3 w-3 mr-1" />
                Environmental Impact
              </Badge>
              <Badge className="bg-secondary/20 text-secondary border-secondary/50">
                <Cpu className="h-3 w-3 mr-1" />
                Edge AI
              </Badge>
              <Badge className="bg-accent/20 text-accent border-accent/50">
                <Eye className="h-3 w-3 mr-1" />
                Computer Vision
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Technology Stack */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5 text-secondary" />
              Technology Stack
            </CardTitle>
            <CardDescription>
              Built with modern, scalable technologies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
              {techStack.map((tech) => (
                <div
                  key={tech.name}
                  className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 border border-border/50"
                >
                  <div className="p-2 rounded-lg bg-secondary/20">
                    <tech.icon className="h-4 w-4 text-secondary" />
                  </div>
                  <div>
                    <p className="font-medium">{tech.name}</p>
                    <p className="text-xs text-muted-foreground">{tech.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Team */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-chart-4" />
              Team
            </CardTitle>
            <CardDescription>
              The people behind CogniRecycle
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-3 gap-4">
              {team.map((member) => (
                <div
                  key={member.name}
                  className="text-center p-4 rounded-lg bg-muted/30 border border-border/50"
                >
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary mx-auto mb-3 flex items-center justify-center">
                    <Users className="h-8 w-8 text-primary-foreground" />
                  </div>
                  <p className="font-medium">{member.name}</p>
                  <p className="text-sm text-muted-foreground">{member.role}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Links */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Resources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button variant="outline" className="gap-2" asChild>
                <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4" />
                  GitHub Repository
                  <ExternalLink className="h-3 w-3" />
                </a>
              </Button>
              <Button variant="outline" className="gap-2" asChild>
                <a href="#" target="_blank" rel="noopener noreferrer">
                  <Code className="h-4 w-4" />
                  API Documentation
                  <ExternalLink className="h-3 w-3" />
                </a>
              </Button>
              <Button variant="outline" className="gap-2" asChild>
                <a href="mailto:contact@cognirecycle.ai">
                  Contact Us
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground py-8">
          <p>CogniRecycle © 2024 • Open Source under MIT License</p>
          <p className="mt-2">Built with ❤️ for Smart Cities</p>
        </div>
      </div>
    </MainLayout>
  );
}
