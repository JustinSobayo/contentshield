import { useState, useRef, DragEvent } from "react";
import { Upload, File, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface VideoUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClearFile: () => void;
}

export default function VideoUpload({ onFileSelect, selectedFile, onClearFile }: VideoUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const videoFile = files.find(file => file.type.startsWith('video/'));

    if (videoFile) {
      onFileSelect(videoFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('video/')) {
      onFileSelect(file);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-center text-foreground mb-8">
        Upload Your Video Content
      </h2>

      {!selectedFile ? (
        <div
          className={cn(
            "border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300",
            "hover:border-primary hover:bg-primary/5 cursor-pointer",
            isDragging
              ? "border-primary bg-primary/10 shadow-corporate"
              : "border-border bg-card"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="flex flex-col items-center space-y-6">
            <div className={cn(
              "p-6 rounded-full transition-colors",
              isDragging ? "bg-primary text-primary-foreground" : "bg-primary/10 text-primary"
            )}>
              <Upload className="h-12 w-12" />
            </div>

            <div className="space-y-2">
              <h3 className="text-xl font-semibold text-foreground">
                Drag & drop your video file here
              </h3>
              <p className="text-muted-foreground">
                or click to browse files
              </p>
            </div>

            <div className="text-sm text-muted-foreground">
              Supports MP4, AVI, MOV, WMV files up to 500MB
            </div>

            <Button variant="outline" size="lg" className="pointer-events-none">
              Select Video File
            </Button>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      ) : (
        <div className="bg-card border border-border rounded-xl p-8 shadow-corporate">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-success/10 p-4 rounded-full">
                <File className="h-8 w-8 text-success" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">
                  {selectedFile.name}
                </h3>
                <p className="text-muted-foreground">
                  {formatFileSize(selectedFile.size)} • Video file ready for analysis
                </p>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={onClearFile}
              className="text-muted-foreground hover:text-destructive"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}