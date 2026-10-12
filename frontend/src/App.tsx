import { FormEvent, useEffect, useState } from "react";

import "./App.css";
import { getHealth } from "./api/client";
import { getPresets } from "./api/presets";
import { renderArtwork } from "./api/render";
import { ArtworkPreview } from "./components/ArtworkPreview";
import { ParameterControl } from "./components/ParameterControl";
import type {
  ParameterValue,
  Preset,
  RenderedArtwork,
} from "./types/api";

type ApiState = "checking" | "online" | "offline";

function defaultsFor(preset: Preset): Record<string, ParameterValue> {
  return Object.fromEntries(
    Object.entries(preset.parameters).map(([name, schema]) => [name, schema.default]),
  );
}

function App() {
  const [apiState, setApiState] = useState<ApiState>("checking");
  const [presets, setPresets] = useState<Preset[]>([]);
  const [selectedSlug, setSelectedSlug] = useState("");
  const [parameters, setParameters] = useState<Record<string, ParameterValue>>({});
  const [width, setWidth] = useState(1024);
  const [height, setHeight] = useState(1024);
  const [seed, setSeed] = useState(0);
  const [artwork, setArtwork] = useState<RenderedArtwork | null>(null);
  const [rendering, setRendering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedPreset = presets.find((preset) => preset.slug === selectedSlug);

  useEffect(() => {
    const controller = new AbortController();
    getHealth(controller.signal)
      .then(() => setApiState("online"))
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") return;
        setApiState("offline");
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    getPresets(controller.signal)
      .then((availablePresets) => {
        setPresets(availablePresets);
        if (availablePresets[0]) {
          setSelectedSlug(availablePresets[0].slug);
          setParameters(defaultsFor(availablePresets[0]));
        }
      })
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") return;
        setError(requestError instanceof Error ? requestError.message : "Não foi possível carregar os presets");
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    return () => {
      if (artwork) URL.revokeObjectURL(artwork.imageUrl);
    };
  }, [artwork]);

  function selectPreset(slug: string) {
    const preset = presets.find((item) => item.slug === slug);
    if (!preset) return;
    setSelectedSlug(slug);
    setParameters(defaultsFor(preset));
    setError(null);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPreset) return;
    setRendering(true);
    setError(null);
    try {
      const result = await renderArtwork({
        preset_slug: selectedPreset.slug,
        width,
        height,
        seed,
        parameters,
      });
      setArtwork(result);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao renderizar a arte");
    } finally {
      setRendering(false);
    }
  }

  const statusLabel = {
    checking: "Verificando API…",
    online: "API conectada",
    offline: "API indisponível",
  }[apiState];

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Arte matemática generativa</p>
          <h1>Axiom</h1>
        </div>
        <div className={`api-status api-status--${apiState}`} role="status">
          <span aria-hidden="true" />
          {statusLabel}
        </div>
      </header>

      <div className="workspace">
        <form className="controls" onSubmit={submit}>
          <section>
            <p className="section-number">01 / Preset</p>
            <label className="field" htmlFor="preset">
              <span>Composição</span>
              <select
                id="preset"
                value={selectedSlug}
                onChange={(event) => selectPreset(event.target.value)}
                disabled={!presets.length}
              >
                {presets.map((preset) => (
                  <option key={preset.id} value={preset.slug}>
                    {preset.name}
                  </option>
                ))}
              </select>
            </label>
            {selectedPreset?.description && (
              <p className="preset-description">{selectedPreset.description}</p>
            )}
          </section>

          <section>
            <p className="section-number">02 / Canvas</p>
            <div className="field-row">
              <label className="field" htmlFor="width">
                <span>Largura</span>
                <input id="width" type="number" min="1" max="4096" value={width} onChange={(event) => setWidth(event.target.valueAsNumber)} />
              </label>
              <label className="field" htmlFor="height">
                <span>Altura</span>
                <input id="height" type="number" min="1" max="4096" value={height} onChange={(event) => setHeight(event.target.valueAsNumber)} />
              </label>
            </div>
            <label className="field" htmlFor="seed">
              <span>Seed</span>
              <input id="seed" type="number" min="0" max="4294967295" value={seed} onChange={(event) => setSeed(event.target.valueAsNumber)} />
            </label>
          </section>

          {selectedPreset && (
            <section>
              <p className="section-number">03 / Parâmetros</p>
              <div className="parameter-grid">
                {Object.entries(selectedPreset.parameters).map(([name, schema]) => (
                  <ParameterControl key={name} name={name} schema={schema} value={parameters[name] ?? schema.default} onChange={(parameterName, value) => setParameters((current) => ({ ...current, [parameterName]: value }))} />
                ))}
              </div>
            </section>
          )}

          {error && <p className="error-message" role="alert">{error}</p>}
          <button className="render-button" type="submit" disabled={!selectedPreset || rendering}>
            {rendering ? "Renderizando…" : "Gerar arte"}
          </button>
        </form>

        <ArtworkPreview artwork={artwork} rendering={rendering} />
      </div>
    </main>
  );
}

export default App;
