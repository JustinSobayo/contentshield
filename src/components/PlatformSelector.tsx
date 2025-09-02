import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const platforms = [
  {
    id: 'youtube',
    name: 'YouTube',
    color: 'text-red-500',
    bgColor: 'bg-red-50 hover:bg-red-100',
    logo: '📺'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    color: 'text-black',
    bgColor: 'bg-gray-50 hover:bg-gray-100',
    logo: '🎵'
  },
  {
    id: 'instagram',
    name: 'Instagram',
    color: 'text-pink-500',
    bgColor: 'bg-pink-50 hover:bg-pink-100',
    logo: '📷'
  },
  {
    id: 'twitter',
    name: 'X (Twitter)',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 hover:bg-blue-100',
    logo: '🐦'
  }
];

interface PlatformSelectorProps {
  selectedPlatform: string | null;
  onPlatformSelect: (platformId: string) => void;
  disabled?: boolean;
}

export default function PlatformSelector({ 
  selectedPlatform, 
  onPlatformSelect, 
  disabled = false 
}: PlatformSelectorProps) {
  return (
    <div className="w-full max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-center text-foreground mb-8">
        Select Target Platform
      </h2>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {platforms.map((platform) => (
          <Button
            key={platform.id}
            variant="outline"
            className={cn(
              "h-32 flex flex-col items-center justify-center space-y-3 transition-all duration-300",
              "border-2 hover:shadow-platform",
              selectedPlatform === platform.id
                ? "border-primary bg-primary/10 shadow-corporate"
                : "border-border hover:border-primary/50",
              disabled && "opacity-50 cursor-not-allowed"
            )}
            onClick={() => !disabled && onPlatformSelect(platform.id)}
            disabled={disabled}
          >
            <div className="text-4xl mb-2">
              {platform.logo}
            </div>
            <div className="text-center">
              <div className={cn("text-lg font-semibold", platform.color)}>
                {platform.name}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Click to analyze
              </div>
            </div>
          </Button>
        ))}
      </div>
      
      {selectedPlatform && (
        <div className="mt-6 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-success-light border border-success/20 rounded-full">
            <div className="w-2 h-2 bg-success rounded-full mr-2"></div>
            <span className="text-success font-medium">
              {platforms.find(p => p.id === selectedPlatform)?.name} selected
            </span>
          </div>
        </div>
      )}
    </div>
  );
}