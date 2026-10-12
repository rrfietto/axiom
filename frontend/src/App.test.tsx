import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

describe("App", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows that the API is connected after a successful health check", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    render(<App />);

    expect(screen.getByRole("heading", { name: "Axiom" })).toBeInTheDocument();
    expect(await screen.findByText("API conectada")).toBeInTheDocument();
  });

  it("shows that the API is unavailable after a failed health check", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("network error"));

    render(<App />);

    expect(await screen.findByText("API indisponível")).toBeInTheDocument();
  });
});
