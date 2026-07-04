import { useState, useRef } from "react";
import { Upload, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";

interface UploadedFile {
  file: File;
  progress: number;
  status: "pending" | "uploading" | "completed" | "error";
  error?: string;
}

export default function FileUploadArea() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [, setLocation] = useLocation();

  const createAnalysisMutation = trpc.analysis.create.useMutation();
  const uploadFileMutation = trpc.file.upload.useMutation();

  const SUPPORTED_FORMATS = ["txt", "pdf", "docx", "csv", "json", "eml"];

  const validateFile = (file: File): { valid: boolean; error?: string } => {
    const extension = file.name.split(".").pop()?.toLowerCase();
    
    if (!extension || !SUPPORTED_FORMATS.includes(extension)) {
      return {
        valid: false,
        error: `Unsupported format: ${extension}. Supported: ${SUPPORTED_FORMATS.join(", ")}`,
      };
    }

    if (file.size > 50 * 1024 * 1024) {
      return {
        valid: false,
        error: "File size exceeds 50MB limit",
      };
    }

    return { valid: true };
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (newFiles: File[]) => {
    const validatedFiles: UploadedFile[] = [];

    for (const file of newFiles) {
      const validation = validateFile(file);
      if (validation.valid) {
        validatedFiles.push({
          file,
          progress: 0,
          status: "pending",
        });
      } else {
        toast.error(`${file.name}: ${validation.error}`);
      }
    }

    setFiles((prev) => [...prev, ...validatedFiles]);
    
    if (validatedFiles.length > 0) {
      handleUpload(validatedFiles);
    }
  };

  const handleUpload = async (filesToUpload: UploadedFile[]) => {
    try {
      const analysis = await createAnalysisMutation.mutateAsync({
        title: `Analysis - ${new Date().toLocaleString()}`,
        description: `Uploaded ${filesToUpload.length} file(s)`,
      });

      if (!analysis.analysisId) {
        toast.error("Failed to create analysis");
        return;
      }

      let successCount = 0;

      for (let i = 0; i < filesToUpload.length; i++) {
        const uploadedFile = filesToUpload[i];

        try {
          setFiles((prev) => {
            const updated = [...prev];
            const idx = updated.findIndex((f) => f.file === uploadedFile.file);
            if (idx !== -1) updated[idx].status = "uploading";
            return updated;
          });

          const fileContent = await new Promise<string>((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
              const base64 = (e.target?.result as string).split(",")[1];
              resolve(base64);
            };
            reader.onerror = () => reject(new Error("Failed to read file"));
            reader.readAsDataURL(uploadedFile.file);
          });

          const extension = uploadedFile.file.name.split(".").pop()?.toLowerCase() || "txt";

          await uploadFileMutation.mutateAsync({
            analysisId: analysis.analysisId,
            fileName: uploadedFile.file.name,
            fileType: extension as any,
            fileSize: uploadedFile.file.size,
            fileContent: fileContent,
          });

          setFiles((prev) => {
            const updated = [...prev];
            const idx = updated.findIndex((f) => f.file === uploadedFile.file);
            if (idx !== -1) {
              updated[idx].status = "completed";
              updated[idx].progress = 100;
            }
            return updated;
          });

          successCount++;
          toast.success(`${uploadedFile.file.name} uploaded`);
        } catch (error) {
          setFiles((prev) => {
            const updated = [...prev];
            const idx = updated.findIndex((f) => f.file === uploadedFile.file);
            if (idx !== -1) {
              updated[idx].status = "error";
              updated[idx].error = String(error);
            }
            return updated;
          });
          toast.error(`Failed to upload ${uploadedFile.file.name}`);
        }
      }

      if (successCount > 0) {
        setTimeout(() => {
          setLocation(`/analysis/${analysis.analysisId}`);
        }, 1000);
      }
    } catch (error) {
      toast.error(`Failed to create analysis: ${String(error)}`);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearCompleted = () => {
    setFiles((prev) => prev.filter((f) => f.status !== "completed"));
  };

  return (
    <div className="space-y-6">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? "border-blue-500 bg-blue-50"
            : "border-slate-300 bg-slate-50 hover:border-slate-400"
        }`}
      >
        <Upload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
        <h3 className="text-lg font-semibold text-slate-900 mb-2">
          Drag and drop files here
        </h3>
        <p className="text-slate-600 mb-4">
          or click to browse
        </p>
        <p className="text-sm text-slate-500 mb-4">
          Supported formats: {SUPPORTED_FORMATS.join(", ")} (Max 50MB)
        </p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={SUPPORTED_FORMATS.map((f) => `.${f}`).join(",")}
          onChange={handleFileInputChange}
          className="hidden"
        />
        <Button
          onClick={() => fileInputRef.current?.click()}
          variant="default"
        >
          Select Files
        </Button>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">
              Upload Progress ({files.filter((f) => f.status === "completed").length}/{files.length})
            </h3>
            {files.some((f) => f.status === "completed") && (
              <Button
                variant="outline"
                size="sm"
                onClick={clearCompleted}
              >
                Clear Completed
              </Button>
            )}
          </div>

          <div className="space-y-3">
            {files.map((uploadedFile, index) => (
              <Card key={index} className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-slate-900 truncate">
                        {uploadedFile.file.name}
                      </span>
                      <span className="text-xs text-slate-500">
                        ({(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    <Progress value={uploadedFile.progress} className="h-2" />
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-xs text-slate-600">
                        {uploadedFile.status === "pending" && "Pending..."}
                        {uploadedFile.status === "uploading" && "Uploading..."}
                        {uploadedFile.status === "completed" && "✓ Completed"}
                        {uploadedFile.status === "error" && "✗ Error"}
                      </span>
                      {uploadedFile.error && (
                        <span className="text-xs text-red-600">{uploadedFile.error}</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
