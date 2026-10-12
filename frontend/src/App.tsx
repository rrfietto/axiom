import { useEffect, useState } from "react";

import { getHealth } from "./api/client";
import "./App.css";

type ApiState = "checking" | "online" | "offline";

function App() {
  const [apiState, setApiState] = useState<ApiState>("checking");

  useEffect(() => {
    const controller = new AbortController();

    getHealth(controller.signal)
      .then(() => setApiState("online"))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setApiState("offline");
      });

    return () => controller.abort();
  }, []);

  const statusLabel = {
    checking: "Verificando API…",
    online: "API conectada",
    offline: "API indisponível",
  }[apiState];

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">Arte matemática generativa</p>
        <h1>Axiom</h1>
        <p className="intro">
          Explore padrões matemáticos, ajuste seus parâmetros e transforme
          equações em imagens.
        </p>
        <div className={`api-status api-status--${apiState}`} role="status">
          <span aria-hidden="true" />
          {statusLabel}
        </div>
      </section>
      <div className="orb" aria-hidden="true" />
    </main>
  );
}

export default App;
