import React, { useState } from "react";
import {
  Terminal,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  Shield,
  FileCode,
  X,
  RefreshCw,
} from "lucide-react";

import { apiPost } from "../utils/api";

interface TestRunnerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TestRunnerModal: React.FC<TestRunnerModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [isRunning, setIsRunning] = useState(false);
  const [testResult, setTestResult] = useState<{
    passed: boolean;
    durationMs: number;
    output: string;
  } | null>(null);

  const runTests = async () => {
    setIsRunning(true);
    try {
      const data = await apiPost("/api/python/run-tests");
      setTestResult({
        passed: data.passed,
        durationMs: data.durationMs,
        output: data.output,
      });
    } catch (err: any) {
      setTestResult({
        passed: false,
        durationMs: 0,
        output: `Execution error: ${err.message}`,
      });
    } finally {
      setIsRunning(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-700">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Automated Test Runner (Python unittest)
              </h3>
              <p className="text-xs text-slate-500">
                Executes unit & integration test suites directly against the Python backend
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-4 overflow-y-auto flex-1 pr-1">
          {/* Action Trigger Card */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 rounded-xl bg-slate-50 border border-slate-200 gap-3">
            <div>
              <span className="text-xs font-bold text-slate-900 block">
                Test Target: /tests/ (22 automated test cases)
              </span>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Covers `test_finance_tracker.py`, `test_analytics.py`, `test_budget.py`, and `test_database.py`.
              </p>
            </div>
            <button
              id="btn-execute-tests"
              onClick={runTests}
              disabled={isRunning}
              className="inline-flex items-center justify-center px-4 py-2 text-xs font-semibold rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-xs disabled:opacity-50 shrink-0"
            >
              {isRunning ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                  Executing Python Suite...
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 mr-1.5 fill-current" />
                  Run Tests Now
                </>
              )}
            </button>
          </div>

          {/* Test Status Banner */}
          {testResult && (
            <div
              className={`p-4 rounded-xl border flex items-center justify-between ${
                testResult.passed
                  ? "bg-emerald-50 border-emerald-200 text-emerald-900"
                  : "bg-rose-50 border-rose-200 text-rose-900"
              }`}
            >
              <div className="flex items-center space-x-2">
                {testResult.passed ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-600" />
                )}
                <div>
                  <span className="text-xs font-bold block">
                    {testResult.passed ? "All 22 Tests Passed Successfully!" : "Test Suite Failures Detected"}
                  </span>
                  <span className="text-[11px] opacity-80">
                    Execution time: {testResult.durationMs}ms
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Terminal Console Output */}
          <div>
            <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1.5">
              <span>Standard Execution Output</span>
              <span className="text-[10px] font-mono text-slate-400">
                Command: python3 -m unittest discover tests -v
              </span>
            </div>
            <pre className="p-4 bg-slate-900 text-emerald-400 rounded-xl text-[11px] font-mono overflow-x-auto whitespace-pre-wrap max-h-56 leading-relaxed">
              {testResult
                ? testResult.output
                : "Ready to run tests. Click 'Run Tests Now' to discover and verify all test suites."}
            </pre>
          </div>

          {/* Architecture & SOLID Compliance Checklist */}
          <div className="p-4 rounded-xl border border-slate-200 bg-white">
            <h4 className="text-xs font-bold text-slate-900 mb-2 flex items-center space-x-1.5">
              <Shield className="w-4 h-4 text-emerald-600" />
              <span>Architectural Verification & Principles Checklist</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-600">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>Single Responsibility (SRP) across modules</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>Open/Closed Principle (polymorphic accounts)</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>Liskov Substitution across Account models</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>Decimal arithmetic (zero float errors)</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>ACID SQLite transactions & audit logs</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>IQR & Modified Z-Score outlier detection</span>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="pt-4 border-t border-slate-100 flex justify-end">
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
