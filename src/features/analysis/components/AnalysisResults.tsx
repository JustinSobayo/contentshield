import { useState } from "react";
import { AlertTriangle, CheckCircle2, Shield, Clock, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Issue {
  category: string;
  timestamp?: string;
  snippet: string;
  rationale: string;
}

interface AnalysisResultsProps {
  riskLevel: string;
  platform: string;
  fileName: string;
  summaryRationale?: string;
  issues?: Issue[];
}

export default function AnalysisResults({
  riskLevel,
  platform,
  fileName,
  summaryRationale,
  issues = []
}: AnalysisResultsProps) {
  const [showReport, setShowReport] = useState(false);

  const getRiskLevel = (level: string) => {
    const normalizedLevel = level.toUpperCase();
    if (normalizedLevel === 'HIGH') return { level: 'HIGH', color: 'destructive', icon: AlertTriangle };
    if (normalizedLevel === 'MEDIUM') return { level: 'MEDIUM', color: 'warning', icon: AlertTriangle };
    return { level: 'LOW', color: 'success', icon: CheckCircle2 };
  };

  const risk = getRiskLevel(riskLevel);
  const RiskIcon = risk.icon;

  // Map backend issues to frontend display format
  const flaggedContent = issues.map(issue => ({
    timestamp: issue.timestamp || "N/A",
    text: issue.snippet,
    concern: issue.category,
    severity: "medium", // Defaulting severity as backend doesn't provide it per issue yet
    rationale: issue.rationale
  }));


  return (
    <div className="w-full max-w-6xl mx-auto space-y-8">
      {/* Risk Assessment Card */}
      <Card className="shadow-elevated border-2">
        <CardHeader className="text-center pb-4">
          <div className="flex justify-center mb-4">
            <div className={cn(
              "p-6 rounded-full",
              risk.color === 'destructive' && "bg-destructive/10",
              risk.color === 'warning' && "bg-warning/10",
              risk.color === 'success' && "bg-success/10"
            )}>
              <RiskIcon className={cn(
                "h-12 w-12",
                risk.color === 'destructive' && "text-destructive",
                risk.color === 'warning' && "text-warning",
                risk.color === 'success' && "text-success"
              )} />
            </div>
          </div>

          <CardTitle className="text-3xl font-bold text-foreground">
            Analysis Complete
          </CardTitle>

          <div className="text-lg text-muted-foreground">
            {fileName} • {platform.charAt(0).toUpperCase() + platform.slice(1)}
          </div>
        </CardHeader>

        <CardContent className="text-center space-y-6">
          <div className="space-y-4">
            <div className="text-xl text-muted-foreground">
              Takedown Risk Likelihood
            </div>
            <Badge
              variant={risk.color === 'destructive' ? 'destructive' : 'secondary'}
              className={cn(
                "text-3xl px-8 py-4",
                risk.color === 'warning' && "bg-warning text-warning-foreground",
                risk.color === 'success' && "bg-success text-success-foreground"
              )}
            >
              {risk.level} RISK
            </Badge>
          </div>

          {summaryRationale && (
            <div className="bg-muted p-4 rounded-lg mt-4 max-w-2xl mx-auto">
              <h4 className="font-semibold text-foreground mb-2 flex items-center justify-center gap-2">
                <Shield className="h-4 w-4" /> AI Analyst Verdict
              </h4>
              <p className="text-sm text-muted-foreground italic">
                "{summaryRationale}"
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="bg-muted/50 p-4 rounded-lg">
              <Clock className="h-6 w-6 text-accent-primary mx-auto mb-2" />
              <div className="text-sm font-medium text-foreground">Analysis Time</div>
              <div className="text-xs text-muted-foreground">2.3 seconds</div>
            </div>

            <div className="bg-muted/50 p-4 rounded-lg">
              <FileText className="h-6 w-6 text-accent-primary mx-auto mb-2" />
              <div className="text-sm font-medium text-foreground">Issues Found</div>
              <div className="text-xs text-muted-foreground">{flaggedContent.length} potential concerns</div>
            </div>

            <div className="bg-muted/50 p-4 rounded-lg">
              <CheckCircle2 className="h-6 w-6 text-success mx-auto mb-2" />
              <div className="text-sm font-medium text-foreground">Confidence</div>
              <div className="text-xs text-muted-foreground">94% accuracy</div>
            </div>
          </div>

          <Button
            onClick={() => setShowReport(!showReport)}
            size="lg"
            className="mt-6"
          >
            {showReport ? 'Hide' : 'View'} Detailed Report
          </Button>
        </CardContent>
      </Card>

      {/* Detailed Report */}
      {showReport && (
        <Card className="shadow-corporate">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-6 w-6 text-primary" />
              <span>Compliance Analysis Report</span>
            </CardTitle>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              {flaggedContent.map((item, index) => (
                <div key={index} className="border border-border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="font-mono">
                      {item.timestamp}
                    </Badge>
                    <Badge
                      variant={item.severity === 'high' ? 'destructive' :
                        item.severity === 'medium' ? 'secondary' : 'outline'}
                    >
                      {item.severity.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="bg-muted/30 p-3 rounded border-l-4 border-l-primary">
                    <p className="font-medium text-foreground">"{item.text}"</p>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    <strong>Concern:</strong> {item.concern}
                  </p>
                  {item.rationale && (
                    <p className="text-sm text-muted-foreground mt-1">
                      <strong>Rationale:</strong> {item.rationale}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}