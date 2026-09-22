import express from "express";
import path from "path";
import { exec, spawn } from "child_process";
import fs from "fs";
import { createServer as createViteServer } from "vite";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Helper to run python api_bridge
  const runPythonBridge = (action: string, payload: any = {}): Promise<any> => {
    return new Promise((resolve, reject) => {
      const payloadStr = JSON.stringify(payload);
      // Spawn python3 api_bridge.py <action> finance_tracker.db '<payloadStr>'
      const pyProcess = spawn("python3", ["api_bridge.py", action, "finance_tracker.db", payloadStr]);

      let stdout = "";
      let stderr = "";

      pyProcess.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      pyProcess.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      pyProcess.on("close", (code) => {
        if (code !== 0) {
          try {
            const errObj = JSON.parse(stdout);
            return reject(new Error(errObj.error || stderr || `Python exited with code ${code}`));
          } catch {
            return reject(new Error(stderr || stdout || `Python exited with code ${code}`));
          }
        }
        try {
          const parsed = JSON.parse(stdout);
          resolve(parsed);
        } catch (err) {
          reject(new Error(`Failed to parse python output: ${stdout}`));
        }
      });
    });
  };

  // --- API Routes ---

  // Health
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  // Financial Dossier (Summary, Accounts, Budgets, Velocity, Forecast, Health Score)
  app.get("/api/finance/dossier", async (req, res) => {
    try {
      const result = await runPythonBridge("dossier");
      res.json(result);
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  });

  // Filtered Transactions
  app.get("/api/finance/transactions", async (req, res) => {
    try {
      const payload = {
        account_id: req.query.account_id || null,
        category: req.query.category || null,
        start_date: req.query.start_date || null,
        end_date: req.query.end_date || null,
        txn_type: req.query.txn_type || null,
        search_query: req.query.search_query || null,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : 100,
      };
      const result = await runPythonBridge("transactions", payload);
      res.json(result);
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  });

  // Add Transaction
  app.post("/api/finance/transactions", async (req, res) => {
    try {
      const result = await runPythonBridge("add_transaction", req.body);
      res.json(result);
    } catch (err: any) {
      res.status(400).json({ success: false, error: err.message });
    }
  });

  // Transfer Funds
  app.post("/api/finance/transfer", async (req, res) => {
    try {
      const result = await runPythonBridge("transfer", req.body);
      res.json(result);
    } catch (err: any) {
      res.status(400).json({ success: false, error: err.message });
    }
  });

  // Delete Transaction
  app.post("/api/finance/delete-transaction", async (req, res) => {
    try {
      const result = await runPythonBridge("delete_transaction", req.body);
      res.json(result);
    } catch (err: any) {
      res.status(400).json({ success: false, error: err.message });
    }
  });

  // Add Account
  app.post("/api/finance/accounts", async (req, res) => {
    try {
      const result = await runPythonBridge("add_account", req.body);
      res.json(result);
    } catch (err: any) {
      res.status(400).json({ success: false, error: err.message });
    }
  });

  // Set Budget
  app.post("/api/finance/budgets", async (req, res) => {
    try {
      const result = await runPythonBridge("set_budget", req.body);
      res.json(result);
    } catch (err: any) {
      res.status(400).json({ success: false, error: err.message });
    }
  });

  // Re-seed Sample Data
  app.post("/api/finance/seed", async (req, res) => {
    try {
      const result = await runPythonBridge("seed");
      res.json(result);
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  });

  // Executive Report (Text, HTML, CSV)
  app.get("/api/finance/report", async (req, res) => {
    try {
      const format = (req.query.format as string) || "text";
      const result = await runPythonBridge("report", { format });
      if (format === "html") {
        res.setHeader("Content-Type", "text/html");
        return res.send(result.content);
      }
      if (format === "csv") {
        res.setHeader("Content-Type", "text/csv");
        res.setHeader("Content-Disposition", 'attachment; filename="transactions.csv"');
        return res.send(result.content);
      }
      res.json(result);
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  });

  // Run Automated Python Test Suite (Unittest)
  app.post("/api/python/run-tests", (req, res) => {
    const startTime = Date.now();
    exec("python3 -m unittest discover tests -v", { cwd: process.cwd() }, (error, stdout, stderr) => {
      const durationMs = Date.now() - startTime;
      const combinedOutput = (stdout + "\n" + stderr).trim();
      const passed = !error;
      res.json({
        success: true,
        passed,
        exitCode: error ? error.code : 0,
        durationMs,
        output: combinedOutput,
      });
    });
  });

  // Inspect Python Source Code Files
  app.get("/api/python/source-code", async (req, res) => {
    try {
      const result = await runPythonBridge("source_files");
      res.json(result);
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  });

  // Download Python Project as ZIP
  app.get("/api/python/download-zip", async (req, res) => {
    try {
      await runPythonBridge("make_zip");
      const zipPath = path.join(process.cwd(), "smart_finance_tracker_python.zip");
      if (fs.existsSync(zipPath)) {
        res.download(zipPath, "smart_finance_tracker_python.zip");
      } else {
        res.status(404).json({ error: "ZIP file generation failed" });
      }
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // --- Vite Middleware & Static Serving ---
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Smart Personal Finance Tracker server running at http://localhost:${PORT}`);
  });
}

startServer();
