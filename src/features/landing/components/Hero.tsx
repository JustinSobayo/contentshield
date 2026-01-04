import { Shield, CheckCircle2, TrendingUp } from "lucide-react";
import heroImage from "@/assets/hero-image.jpg";

export default function Hero() {
  return (
    <section className="relative bg-gradient-corporate py-20 lg:py-32 overflow-hidden">
      <div className="absolute inset-0">
        <img
          src={heroImage}
          alt="Professional content protection and compliance analysis"
          className="w-full h-full object-cover opacity-10"
        />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="flex justify-center mb-8">
            <div className="bg-primary/10 p-6 rounded-full">
              <Shield className="h-16 w-16 text-primary" />
            </div>
          </div>

          <h1 className="text-5xl lg:text-7xl font-bold text-foreground mb-8 leading-tight">
            Content Shield
            <span className="block text-primary text-4xl lg:text-5xl mt-2">
              Social Media Compliance
            </span>
          </h1>

          <p className="text-xl lg:text-2xl text-muted-foreground mb-12 max-w-4xl mx-auto leading-relaxed">
            Proactively analyze your video content for platform policy compliance.
            Get instant risk assessments and detailed recommendations before publishing.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-card/80 backdrop-blur-sm border border-border rounded-xl p-6 shadow-corporate">
              <CheckCircle2 className="h-8 w-8 text-success mb-4 mx-auto" />
              <h3 className="text-lg font-semibold text-foreground mb-2">AI-Powered Analysis</h3>
              <p className="text-muted-foreground">Advanced transcript analysis and policy matching</p>
            </div>

            <div className="bg-card/80 backdrop-blur-sm border border-border rounded-xl p-6 shadow-corporate">
              <TrendingUp className="h-8 w-8 text-accent-primary mb-4 mx-auto" />
              <h3 className="text-lg font-semibold text-foreground mb-2">Risk Assessment</h3>
              <p className="text-muted-foreground">Clear Low, Medium, High risk level indicators</p>
            </div>

            <div className="bg-card/80 backdrop-blur-sm border border-border rounded-xl p-6 shadow-corporate">
              <Shield className="h-8 w-8 text-primary mb-4 mx-auto" />
              <h3 className="text-lg font-semibold text-foreground mb-2">Compliance Reports</h3>
              <p className="text-muted-foreground">Detailed recommendations and policy citations</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}