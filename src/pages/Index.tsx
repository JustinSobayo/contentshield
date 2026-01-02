import { useState } from "react";
import Hero from "@/features/landing/components/Hero";
import PlatformSelector from "@/features/analysis/components/PlatformSelector";
import VideoUpload from "@/features/analysis/components/VideoUpload";
import AnalysisResults from "@/features/analysis/components/AnalysisResults";
import { DebugView } from "@/features/debug/components/DebugView";
import { analyzeContent } from "@/features/analysis/api/analyzeContent";
import { AnalyzeResponse } from "@/features/analysis/types/analysis.types";
import { useToast } from "@/components/ui/use-toast";
import { Loader2 } from "lucide-react";

export default function Index() {
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalyzeResponse | null>(null);
  const [showDebug, setShowDebug] = useState(false);
  const { toast } = useToast();

  const handleAnalyze = async () => {
    if (!file || !selectedPlatform) return;

    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('platform', selectedPlatform);

    try {
      console.log("Starting analysis via feature API...");
      const data = await analyzeContent(formData);

      console.log("Analysis success:", data);
      setResults(data);

      toast({
        title: "Analysis Complete",
        description: `Successfully analyzed content for ${selectedPlatform}`,
      });
    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "Analysis Failed",
        description: error instanceof Error ? error.message : "Failed to analyze video. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResults(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <Hero />

      <main className="container mx-auto px-4 py-16 space-y-24">
        {showDebug ? (
          <section className="animate-in fade-in slide-in-from-top-8 duration-500">
            <DebugView />
            <div className="mt-8 text-center">
              <button
                onClick={() => setShowDebug(false)}
                className="text-muted-foreground hover:text-foreground underline text-sm"
              >
                Back to Analysis
              </button>
            </div>
          </section>
        ) : (
          <>
            {/* Step 1: Select Platform */}
            <section id="platform-select" className="scroll-mt-24">
              <PlatformSelector
                selectedPlatform={selectedPlatform}
                onPlatformSelect={setSelectedPlatform}
                disabled={isAnalyzing || !!results}
              />
            </section>

            {/* Step 2: Upload Video (Only shown after platform selected) */}
            {selectedPlatform && !results && (
              <section id="upload" className="animate-in fade-in slide-in-from-bottom-8 duration-500">
                <VideoUpload
                  onFileSelect={setFile}
                  selectedFile={file}
                  onClearFile={() => setFile(null)}
                />

                {file && (
                  <div className="mt-8 text-center animate-in fade-in zoom-in duration-300">
                    <button
                      onClick={handleAnalyze}
                      disabled={isAnalyzing}
                      className="bg-primary hover:bg-primary/90 text-primary-foreground text-lg px-8 py-4 rounded-full font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center mx-auto space-x-2"
                    >
                      {isAnalyzing ? (
                        <>
                          <Loader2 className="h-5 w-5 animate-spin" />
                          <span>Analyzing Content...</span>
                        </>
                      ) : (
                        <span>Analyze Video</span>
                      )}
                    </button>
                    <p className="text-sm text-muted-foreground mt-4">
                      This may take up to a minute depending on video length
                    </p>
                  </div>
                )}
              </section>
            )}

            {/* Step 3: Results */}
            {results && (
              <section id="results" className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                <AnalysisResults
                  riskLevel={results.risk_level}
                  platform={results.platform}
                  fileName={file?.name || 'Uploaded Video'}
                  summaryRationale={results.summary_rationale}
                  issues={results.issues}
                />

                <div className="mt-12 text-center">
                  <button
                    onClick={handleReset}
                    className="text-muted-foreground hover:text-foreground underline"
                  >
                    Analyze Another Video
                  </button>
                </div>
              </section>
            )}
          </>
        )}
      </main>

      <footer className="bg-muted/30 py-12 mt-24 border-t border-border">
        <div className="container mx-auto px-4 text-center text-muted-foreground space-y-4">
          <p>© 2025 Content Shield. Secure. Compliant. Ready.</p>
          <button
            onClick={() => setShowDebug(!showDebug)}
            className="text-[10px] uppercase tracking-widest opacity-30 hover:opacity-100 transition-opacity"
          >
            {showDebug ? "Hide System Diagnostics" : "System Diagnostics"}
          </button>
        </div>
      </footer>
    </div>
  );
}