import type { RenderPayload, RenderedArtwork } from "../types/api";
import { apiRequest } from "./client";

export async function renderArtwork(
  payload: RenderPayload,
  signal?: AbortSignal,
): Promise<RenderedArtwork> {
  const response = await apiRequest("/api/render", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
  const image = await response.blob();
  return {
    imageUrl: URL.createObjectURL(image),
    artworkId: response.headers.get("X-Axiom-Artwork-Id"),
    artworkUrl: response.headers.get("X-Axiom-Artwork-Url"),
  };
}
