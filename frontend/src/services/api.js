/**
 * Resilient API fetch client for LaptopDSS.
 * Directly targets IPv4 http://127.0.0.1:8000 first (fastest & bypasses proxy hangs),
 * with automatic fallback to Vite proxy ('') and http://localhost:8000.
 */

const BACKEND_TARGETS = [
  'http://127.0.0.1:8000', // Direct IPv4 (bypasses any Vite proxy hang)
  '',                      // Relative (Vite proxy)
  'http://localhost:8000', // Fallback
];

export async function apiFetch(endpoint, options = {}) {
  let lastError = null;

  for (const base of BACKEND_TARGETS) {
    const url = `${base}${endpoint}`;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);

      const res = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (res.status !== 502 && res.status !== 504) {
        return res;
      }
      lastError = new Error(`Server returned ${res.status} at ${url}`);
    } catch (err) {
      lastError = err;
    }
  }

  throw lastError || new Error(`Không thể kết nối Backend: ${endpoint}`);
}

