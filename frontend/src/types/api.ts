export type ParameterValue = number | boolean | string;
export type ParameterType = "integer" | "number" | "boolean" | "color" | "select";

export interface ParameterSchema {
  type: ParameterType;
  default: ParameterValue;
  minimum: number | null;
  maximum: number | null;
  options: string[];
  label: string;
  description: string | null;
}

export interface Preset {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  renderer_id: string;
  renderer_version: number;
  parameters: Record<string, ParameterSchema>;
  revision: number;
}

export interface RenderPayload {
  preset_slug: string;
  width: number;
  height: number;
  seed: number;
  parameters: Record<string, ParameterValue>;
}

export interface RenderedArtwork {
  imageUrl: string;
  artworkId: string | null;
  artworkUrl: string | null;
}
