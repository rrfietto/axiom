import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const preset = {
  id: 1,
  slug: "emerald-waves",
  name: "Emerald Waves",
  description: "Organic waves",
  renderer_id: "wave-field",
  renderer_version: 1,
  revision: 1,
  parameters: {
    line_count: {
      type: "integer",
      default: 36,
      minimum: 1,
      maximum: 200,
      options: [],
      label: "Quantidade de linhas",
      description: null,
    },
    foreground: {
      type: "color",
      default: "#74e6c2",
      minimum: null,
      maximum: null,
      options: [],
      label: "Cor das linhas",
      description: null,
    },
  },
};

function successfulFetch(input: RequestInfo | URL): Promise<Response> {
  const url = String(input);
  if (url.endsWith("/api/health")) {
    return Promise.resolve(Response.json({ status: "ok" }));
  }
  if (url.endsWith("/api/presets")) {
    return Promise.resolve(Response.json([preset]));
  }
  if (url.endsWith("/api/render")) {
    return Promise.resolve(
      new Response(new Blob(["png"]), {
        status: 200,
        headers: {
          "Content-Type": "image/png",
          "X-Axiom-Artwork-Id": "7",
          "X-Axiom-Artwork-Url": "/api/artworks/7/image",
        },
      }),
    );
  }
  return Promise.resolve(new Response(null, { status: 404 }));
}

describe("App", () => {
  beforeEach(() => {
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn(() => "blob:artwork"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads presets and builds parameter controls", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(successfulFetch);

    render(<App />);

    expect(screen.getByRole("heading", { name: "Axiom" })).toBeInTheDocument();
    expect(await screen.findByText("API conectada")).toBeInTheDocument();
    expect(await screen.findByRole("option", { name: "Emerald Waves" })).toBeInTheDocument();
    expect(screen.getByLabelText("Quantidade de linhas")).toHaveValue(36);
    expect(screen.getByLabelText("Cor das linhas")).toHaveValue("#74e6c2");
  });

  it("renders and displays the generated artwork", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(successfulFetch);
    render(<App />);
    await screen.findByRole("option", { name: "Emerald Waves" });

    fireEvent.change(screen.getByLabelText("Quantidade de linhas"), {
      target: { value: "20", valueAsNumber: 20 },
    });
    fireEvent.click(screen.getByRole("button", { name: "Gerar arte" }));

    expect(await screen.findByAltText("Arte matemática gerada")).toHaveAttribute(
      "src",
      "blob:artwork",
    );
    expect(screen.getByText("Artwork #7")).toBeInTheDocument();
    await waitFor(() => {
      const renderCall = fetchMock.mock.calls.find(([url]) =>
        String(url).endsWith("/api/render"),
      );
      expect(renderCall).toBeDefined();
      expect(JSON.parse(String(renderCall?.[1]?.body))).toMatchObject({
        preset_slug: "emerald-waves",
        parameters: { line_count: 20 },
      });
    });
  });

  it("shows API failures", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("network error"));

    render(<App />);

    expect(await screen.findByText("API indisponível")).toBeInTheDocument();
    expect(await screen.findByRole("alert")).toHaveTextContent("network error");
  });
});
