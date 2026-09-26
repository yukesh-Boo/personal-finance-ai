/**
 * Robust API Client with safe JSON parsing, cold-start handling,
 * automatic retries for transient 502/503 Service Unavailable, and clean errors.
 */

interface FetchOptions extends RequestInit {
  retries?: number;
  retryDelayMs?: number;
  timeoutMs?: number;
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function fetchJson<T = any>(
  url: string,
  options: FetchOptions = {}
): Promise<T> {
  const { retries = 3, retryDelayMs = 800, timeoutMs = 7000, ...fetchInit } = options;

  let attempt = 0;
  while (attempt <= retries) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...fetchInit,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      // Check for transient server startup errors (502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout)
      if ([502, 503, 504].includes(response.status) && attempt < retries) {
        attempt++;
        await sleep(retryDelayMs * attempt);
        continue;
      }

      const contentType = response.headers.get("content-type") || "";
      const rawText = await response.text();

      let parsedData: any = null;
      if (rawText && (contentType.includes("application/json") || rawText.trim().startsWith("{") || rawText.trim().startsWith("["))) {
        try {
          parsedData = JSON.parse(rawText);
        } catch {
          parsedData = null;
        }
      }

      if (!response.ok) {
        // If server gave us JSON with an error message
        if (parsedData && (parsedData.error || parsedData.message)) {
          throw new Error(parsedData.error || parsedData.message);
        }

        // Handle raw HTML or text errors (e.g., Cloud Run 503 "Service Unavailable")
        if (response.status === 503 || rawText.includes("Service Unavailable")) {
          throw new Error("Backend service is initializing. Please wait a moment and try again.");
        }
        if (response.status === 502 || rawText.includes("Bad Gateway")) {
          throw new Error("Backend gateway is reconnecting. Please retry in a moment.");
        }

        throw new Error(
          rawText && rawText.length < 150
            ? rawText.trim()
            : `Request failed with status ${response.status} (${response.statusText || "Server Error"})`
        );
      }

      if (parsedData !== null) {
        return parsedData as T;
      }

      // If response is text but succeeded
      return rawText as unknown as T;
    } catch (err: any) {
      if (attempt < retries && (err.name === "TypeError" || err.message?.includes("fetch"))) {
        // Network failure during server boot
        attempt++;
        await sleep(retryDelayMs * attempt);
        continue;
      }
      throw err;
    }
  }

  throw new Error("Service temporarily unavailable. Please retry connection.");
}

export async function apiGet<T = any>(url: string, retries = 3, timeoutMs = 7000): Promise<T> {
  return fetchJson<T>(url, { method: "GET", retries, timeoutMs });
}

export async function apiPost<T = any>(url: string, body?: any): Promise<T> {
  return fetchJson<T>(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    retries: 1, // POSTs shouldn't aggressively auto-retry
  });
}

export async function apiDelete<T = any>(url: string, body?: any): Promise<T> {
  return fetchJson<T>(url, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    retries: 0,
  });
}
