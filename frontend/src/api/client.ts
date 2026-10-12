export interface HealthResponse {
  status: "ok";
}

export const apiUrl = import.meta.env.VITE_API_URL ?? "";

export async function apiRequest(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  const response = await fetch(`${apiUrl}${path}`, init);
  if (!response.ok) {
    let message = `API respondeu com status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // Keep the status-based message for non-JSON errors.
    }
    throw new Error(message);
  }
  return response;
}

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await apiRequest("/api/health", { signal });
  return response.json() as Promise<HealthResponse>;
}
