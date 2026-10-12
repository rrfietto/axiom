import type { RenderedArtwork } from "../types/api";

interface ArtworkPreviewProps {
  artwork: RenderedArtwork | null;
  rendering: boolean;
}

export function ArtworkPreview({ artwork, rendering }: ArtworkPreviewProps) {
  return (
    <section className="preview" aria-live="polite">
      {artwork ? (
        <>
          <img src={artwork.imageUrl} alt="Arte matemática gerada" />
          <div className="preview-meta">
            <span>Artwork #{artwork.artworkId ?? "—"}</span>
            <a href={artwork.imageUrl} download="axiom.png">
              Baixar PNG
            </a>
          </div>
        </>
      ) : (
        <div className="preview-empty">
          <span>{rendering ? "Calculando…" : "Sua arte aparecerá aqui"}</span>
        </div>
      )}
    </section>
  );
}
