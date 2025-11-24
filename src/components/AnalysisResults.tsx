import { useState } from "react";
import { AlertTriangle, CheckCircle2, Clock, FileText, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

interface AnalysisResultsProps {
  riskLevel: string;
  platform: string;
  fileName: string;
}

export default function AnalysisResults({
  riskLevel,
  platform,
  fileName
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

  const flaggedContent = [
    {
      timestamp: "00:45",
      text: "This is absolutely amazing and revolutionary",
      concern: "Potential copyright claim triggering language",
      severity: "medium"
    },
    {
      timestamp: "02:15",
      text: "Check out this brand new product everyone's talking about",
      concern: "Advertising disclosure requirements may apply",
      severity: "low"
    },
    {
      timestamp: "03:30",
      text: "This will change your life forever",
      concern: "Medical/health claims without evidence",
      severity: "high"
    }
  ];

  const recommendations = [
    {
      priority: "high",
      title: "Add Advertising Disclosure",
      description: "Include proper FTC compliance disclosure for sponsored content",
      action: "Add '#ad' or 'Sponsored by [Brand]' in description"
    },
    {
      priority: "medium",
      title: "Modify Health Claims",
      description: "Replace absolute statements with qualified language",
      action: "Change 'will change your life' to 'may help improve your experience'"
    },
    {
      priority: "low",
      title: "Review Copyright References",
      description: "Ensure all referenced content has proper attribution",
      action: "Add source citations in video description"
    }
  ];

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
            <Tabs defaultValue="flagged" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="flagged">Flagged Content</TabsTrigger>
                <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
                <TabsTrigger value="policies">Policy References</TabsTrigger>
              </TabsList>

              <TabsContent value="flagged" className="space-y-4 mt-6">
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
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-4 mt-6">
                {recommendations.map((rec, index) => (
                  <div key={index} className="border border-border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-foreground">{rec.title}</h3>
                      <Badge
                        variant={rec.priority === 'high' ? 'destructive' :
                          rec.priority === 'medium' ? 'secondary' : 'outline'}
                      >
                        {rec.priority.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground">{rec.description}</p>
                    <div className="bg-success-light p-3 rounded border-l-4 border-l-success">
                      <p className="text-sm text-success-foreground">
                        <strong>Recommended Action:</strong> {rec.action}
                      </p>
                    </div>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="policies" className="space-y-4 mt-6">
                <div className="space-y-4">
                  <div className="border border-border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-foreground">YouTube Community Guidelines</h3>
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        View Policy
                      </Button>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      Section 4.2.1 - Advertising and Sponsored Content Disclosure
                    </p>
                    <p className="text-sm text-muted-foreground">
                      "Creators must clearly disclose when content includes paid promotions, sponsorships, or affiliate marketing."
                    </p>
                  </div>

                  <div className="border border-border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-foreground">FTC Advertising Guidelines</h3>
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        View Policy
                      </Button>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      16 CFR Part 255 - Endorsement Guidelines
                    </p>
                    <p className="text-sm text-muted-foreground">
                      "Material connections between advertisers and endorsers must be clearly disclosed."
                    </p>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}