import type { Preset } from "../types/api";
import { apiRequest } from "./client";

export async function getPresets(signal?: AbortSignal): Promise<Preset[]> {
  const response = await apiRequest("/api/presets", { signal });
  return response.json() as Promise<Preset[]>;
}
