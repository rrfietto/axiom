export interface HealthResponse {
  status: "ok";
}

const apiUrl = import.meta.env.VITE_API_URL ?? "";

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${apiUrl}/api/health`, { signal });

  if (!response.ok) {
    throw new Error(`API respondeu com status ${response.status}`);
  }

  return response.json() as Promise<HealthResponse>;
}
