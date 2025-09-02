import { useState } from "react";
import { Button } from "@/components/ui/button";
import Hero from "@/components/Hero";
import VideoUpload from "@/components/VideoUpload";
import PlatformSelector from "@/components/PlatformSelector";
import AnalysisResults from "@/components/AnalysisResults";
import { Loader2, Shield } from "lucide-react";

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [riskPercentage, setRiskPercentage] = useState(0);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setAnalysisComplete(false);
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setSelectedPlatform(null);
    setAnalysisComplete(false);
  };

  const handlePlatformSelect = (platformId: string) => {
    setSelectedPlatform(platformId);
  };

  const handleAnalyze = () => {
    if (!selectedFile || !selectedPlatform) return;
    
    setIsAnalyzing(true);
    
    // Simulate analysis process
    setTimeout(() => {
      // Generate a realistic risk percentage based on platform
      const baseRisk = Math.floor(Math.random() * 60) + 20; // 20-80%
      const platformModifier = selectedPlatform === 'youtube' ? 10 : 
                              selectedPlatform === 'tiktok' ? -5 : 0;
      const finalRisk = Math.max(5, Math.min(95, baseRisk + platformModifier));
      
      setRiskPercentage(finalRisk);
      setIsAnalyzing(false);
      setAnalysisComplete(true);
    }, 3000);
  };

  const canAnalyze = selectedFile && selectedPlatform && !isAnalyzing;

  return (
    <div className="min-h-screen bg-gradient-corporate">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold text-foreground">Content Shield</span>
            </div>
            
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
                Features
              </a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
                Pricing
              </a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
                Enterprise
              </a>
              <Button variant="outline" size="sm">
                Sign In
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <Hero />

      {/* Main Content */}
      <main className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
          
          {/* Analysis Results */}
          {analysisComplete && (
            <AnalysisResults 
              riskPercentage={riskPercentage}
              platform={selectedPlatform!}
              fileName={selectedFile!.name}
            />
          )}
          
          {/* Analysis Loading */}
          {isAnalyzing && (
            <div className="text-center py-16">
              <div className="bg-card border border-border rounded-xl p-12 shadow-corporate max-w-2xl mx-auto">
                <div className="flex flex-col items-center space-y-6">
                  <div className="relative">
                    <div className="w-16 h-16 border-4 border-primary/20 rounded-full"></div>
                    <div className="absolute top-0 left-0 w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-2xl font-bold text-foreground">
                      Analyzing Your Content
                    </h3>
                    <p className="text-muted-foreground">
                      Processing audio transcript and checking platform policies...
                    </p>
                  </div>
                  
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-gradient-primary h-2 rounded-full animate-pulse" style={{width: '65%'}}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Upload and Platform Selection */}
          {!analysisComplete && !isAnalyzing && (
            <>
              <VideoUpload 
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
                onClearFile={handleClearFile}
              />
              
              {selectedFile && (
                <PlatformSelector 
                  selectedPlatform={selectedPlatform}
                  onPlatformSelect={handlePlatformSelect}
                />
              )}
              
              {/* Analyze Button */}
              {canAnalyze && (
                <div className="text-center">
                  <Button 
                    onClick={handleAnalyze}
                    size="lg"
                    className="bg-gradient-primary text-primary-foreground hover:opacity-90 px-12 py-4 text-lg font-semibold shadow-corporate"
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      'Analyze Content'
                    )}
                  </Button>
                </div>
              )}
            </>
          )}
          
          {/* Reset Button */}
          {analysisComplete && (
            <div className="text-center">
              <Button 
                variant="outline"
                onClick={() => {
                  setSelectedFile(null);
                  setSelectedPlatform(null);
                  setAnalysisComplete(false);
                  setRiskPercentage(0);
                }}
                size="lg"
              >
                Analyze Another Video
              </Button>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card/50 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center space-x-6 text-sm text-muted-foreground">
            <span>© 2024 Content Shield Enterprise</span>
            <span>•</span>
            <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
            <span>•</span>
            <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
            <span>•</span>
            <a href="#" className="hover:text-primary transition-colors">Contact Sales</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;