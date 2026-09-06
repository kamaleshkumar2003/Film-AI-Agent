import React, { useState } from 'react';
import { X, Upload, FileText, CheckCircle2, AlertCircle } from 'lucide-react';

interface UploadScreenplayModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File) => Promise<void>;
  projectName: string;
}

export const UploadScreenplayModal: React.FC<UploadScreenplayModalProps> = ({
  isOpen,
  onClose,
  onUpload,
  projectName
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      const validExts = ['.pdf', '.docx', '.txt', '.fountain'];
      const hasValidExt = validExts.some(ext => f.name.toLowerCase().endsWith(ext));
      if (!hasValidExt) {
        setError("Unsupported file type. Please upload a PDF, DOCX, or TXT screenplay.");
        return;
      }
      if (f.size > 50 * 1024 * 1024) {
        setError("File exceeds 50MB limit.");
        return;
      }
      setSelectedFile(f);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setError(null);
    try {
      await onUpload(selectedFile);
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Upload failed. Please check the file and try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl animate-in fade-in zoom-in-95">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Upload Screenplay</h3>
              <p className="text-xs text-slate-400">Project: {projectName}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="border-2 border-dashed border-slate-800 hover:border-cyan-500/60 rounded-2xl p-6 text-center cursor-pointer transition bg-slate-950/40 relative">
            <input
              type="file"
              accept=".pdf,.docx,.txt,.fountain"
              onChange={handleFileSelect}
              className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
            />
            <div className="flex flex-col items-center">
              <FileText className="w-10 h-10 text-cyan-400 mb-3" />
              <p className="text-sm font-semibold text-slate-200">
                {selectedFile ? selectedFile.name : "Drop screenplay here or click to browse"}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Supports industry formats: PDF, DOCX, TXT (Max 50MB)
              </p>
              {selectedFile && (
                <p className="text-xs text-cyan-400 font-mono mt-2 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Ready: {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              )}
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex justify-end gap-2.5 pt-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={isUploading || !selectedFile}
              className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-semibold transition disabled:opacity-50"
            >
              {isUploading ? "Uploading & Extracting..." : "Upload & Detect Scenes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
