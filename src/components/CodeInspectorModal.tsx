import React, { useState, useEffect } from "react";
import {
  Code2,
  FileCode,
  Download,
  Copy,
  Check,
  X,
  RefreshCw,
} from "lucide-react";

interface CodeInspectorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CodeInspectorModal: React.FC<CodeInspectorModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [files, setFiles] = useState<Record<string, string>>({});
  const [selectedFile, setSelectedFile] = useState<string>("finance_tracker.py");
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      fetch("/api/python/source-code")
        .then((res) => res.json())
        .then((data) => {
          if (data.success && data.files) {
            setFiles(data.files);
            if (!data.files[selectedFile]) {
              const firstKey = Object.keys(data.files)[0];
              if (firstKey) setSelectedFile(firstKey);
            }
          }
        })
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [isOpen]);

  const handleCopy = () => {
    const content = files[selectedFile] || "";
    navigator.clipboard.writeText(content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleDownloadZip = async () => {
    try {
      setIsDownloading(true);
      const res = await fetch("/api/python/download-zip");
      if (!res.ok) throw new Error("Failed to download project zip");
      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = blobUrl;
      a.download = "smart_finance_tracker_python.zip";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => window.URL.revokeObjectURL(blobUrl), 1000);
    } catch (err: any) {
      console.error("ZIP download error:", err);
    } finally {
      setIsDownloading(false);
    }
  };

  if (!isOpen) return null;

  const fileList = Object.keys(files);

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-5xl w-full p-6 shadow-2xl border border-slate-200 flex flex-col h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-blue-50 border border-blue-100 text-blue-700">
              <Code2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Python Source Code Inspector & Package Export
              </h3>
              <p className="text-xs text-slate-500">
                Browse, review, and download the complete Object-Oriented Python application
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownloadZip}
              disabled={isDownloading}
              className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-lg text-white bg-slate-900 hover:bg-slate-800 transition-colors shadow-xs disabled:opacity-50"
              title="Download standalone Python project ZIP"
            >
              <Download className={`w-3.5 h-3.5 mr-1.5 text-emerald-400 ${isDownloading ? "animate-spin" : ""}`} />
              {isDownloading ? "Downloading..." : "Download Python ZIP"}
            </button>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Body (Sidebar + Code View) */}
        <div className="flex flex-1 overflow-hidden border border-slate-200 rounded-xl">
          {/* File Selector Sidebar */}
          <div className="w-64 bg-slate-50 border-r border-slate-200 overflow-y-auto p-2 space-y-1">
            <div className="px-2 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Python Files ({fileList.length})
            </div>
            {isLoading ? (
              <div className="p-4 text-center text-xs text-slate-400">
                <RefreshCw className="w-4 h-4 animate-spin mx-auto mb-1 text-slate-400" />
                Loading codebase...
              </div>
            ) : (
              fileList.map((filename) => (
                <button
                  key={filename}
                  onClick={() => setSelectedFile(filename)}
                  className={`w-full text-left px-2.5 py-1.5 text-xs rounded-lg transition-colors flex items-center space-x-2 truncate font-mono ${
                    selectedFile === filename
                      ? "bg-slate-900 text-white font-semibold"
                      : "text-slate-600 hover:bg-slate-200/60"
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5 shrink-0 opacity-70" />
                  <span className="truncate">{filename}</span>
                </button>
              ))
            )}
          </div>

          {/* Code Viewer */}
          <div className="flex-1 flex flex-col bg-slate-900 overflow-hidden">
            {/* Code Toolbar */}
            <div className="flex items-center justify-between px-4 py-2 bg-slate-950 border-b border-slate-800 text-slate-400 text-xs font-mono">
              <span>{selectedFile}</span>
              <button
                onClick={handleCopy}
                className="inline-flex items-center px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 mr-1 text-emerald-400" /> Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 mr-1" /> Copy Code
                  </>
                )}
              </button>
            </div>

            {/* Code Content */}
            <pre className="p-4 flex-1 text-slate-200 font-mono text-xs overflow-auto whitespace-pre leading-relaxed select-text">
              {files[selectedFile] || "Select a file to inspect source code."}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 flex justify-between items-center text-xs text-slate-500">
          <span>Python 3.8+ Compatible • Clean Architecture • Complete Test Suite</span>
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
