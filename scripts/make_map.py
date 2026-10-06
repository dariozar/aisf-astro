"""Generate ItalyMap.astro: committee dots positioned on the Italy SVG.

Calibrates lon/lat -> SVG coords via least squares on the dots already
embedded in public/italy-map.svg (class="lat|lon"), then projects
hand-listed committee city coordinates. Output positions are percentages
of the 1000x1000 viewBox.
"""
import re

# committee id -> (lat, lon), city of the ateneo
CITIES = {
    "bari": (41.12, 16.87),
    "bologna": (44.49, 11.34),
    "calabria": (39.36, 16.25),
    "ferrara": (44.84, 11.63),
    "firenze": (43.77, 11.25),
    "genova": (44.41, 8.93),
    "milano": (45.46, 9.16),
    "milano-bicocca": (45.52, 9.23),
    "napoli-e-caserta": (40.85, 14.27),
    "padova": (45.41, 11.88),
    "palermo": (38.12, 13.36),
    "pavia": (45.18, 9.13),
    "perugia": (43.11, 12.39),
    "pisa": (43.72, 10.40),
    "roma-sapienza": (41.90, 12.51),
    "roma-tor-vergata": (41.85, 12.62),
    "roma-tre": (41.86, 12.46),
    "salerno": (40.68, 14.77),
    "torino": (45.07, 7.69),
    "trento": (46.07, 11.12),
    "trieste": (45.65, 13.78),
}


def fit(pairs):
    # least squares for x = a*lon + b (and same for y/lat)
    n = len(pairs)
    sx = sum(p[0] for p in pairs)
    sy = sum(p[1] for p in pairs)
    sxx = sum(p[0] * p[0] for p in pairs)
    sxy = sum(p[0] * p[1] for p in pairs)
    a = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    b = (sy - a * sx) / n
    return a, b


def main():
    svg = open("public/italy-map.svg").read()
    pts = re.findall(
        r'<circle class="([\d.]+)\|([\d.]+)" cx="([\d.]+)" cy="([\d.]+)"', svg)
    ax, bx = fit([(float(lon), float(x)) for lat, lon, x, y in pts])
    ay, by = fit([(float(lat), float(y)) for lat, lon, x, y in pts])
    dots = []
    for cid, (lat, lon) in CITIES.items():
        x = (ax * lon + bx) / 10
        y = (ay * lat + by) / 10
        dots.append((cid, round(x, 2), round(y, 2)))
    items = "\n".join(
        f'    {{ id: "{cid}", x: {x}, y: {y} }},' for cid, x, y in dots)
    q = '"' * 3
    astro = open(__file__).read().split("TEMPLATE = " + q)[1].rsplit(q, 1)[0]
    astro = astro.replace("__DOTS__", items)
    open("src/components/ItalyMap.astro", "w").write(astro)
    print(f"wrote ItalyMap.astro with {len(dots)} dots")


TEMPLATE = """---
interface Props {
  committees?: Array<{ id: string; name: string; status?: string }>;
  linkBase?: string;
}

const { committees = [], linkBase = "/comitati" } = Astro.props;
import { u } from "../lib/url";

const dots = [
__DOTS__
];

// Cities sharing one spot become a numbered cluster instead of
// stacked, untappable dots.
const CLUSTERS: Array<Array<string>> = [
  ["milano", "milano-bicocca"],
  ["roma-sapienza", "roma-tor-vergata", "roma-tre"],
];

const byId = new Map(committees.map((c) => [c.id, c]));
const clusteredIds = new Set(CLUSTERS.flat());
const singles = dots.filter((d) => !clusteredIds.has(d.id));
const clusters = CLUSTERS.map((ids) => {
  const pts = ids
    .map((id) => dots.find((d) => d.id === id))
    .filter((p) => p !== undefined);
  return {
    ids,
    x: pts.reduce((s, p) => s + p.x, 0) / pts.length,
    y: pts.reduce((s, p) => s + p.y, 0) / pts.length,
  };
});
---

<div class="relative mx-auto w-full max-w-[520px]" data-committee-map data-link-base={linkBase}>
  <img src={u("/italy-map.svg")} alt="Italia — comitati locali AISF" class="w-full" />
  {singles.map((d) => {
    const c = byId.get(d.id);
    const frozen = c?.status === "frozen";
    return (
      <button
        type="button"
        data-dot={d.id}
        title={c?.name ?? d.id}
        aria-label={c?.name ?? `${d.id} — mostra la scheda`}
        class="absolute -translate-x-1/2 -translate-y-1/2 p-3"
        style={`left: ${d.x}%; top: ${d.y}%;`}
      >
        <span
          data-dot-visual
          class:list={[
            "block size-[12px] rounded-full border-2 border-paper shadow transition-transform",
            frozen ? "bg-ink-soft" : "bg-tangerine",
          ]}
        ></span>
      </button>
    );
  })}
  {clusters.map((c, i) => (
    <button
      type="button"
      data-cluster={i}
      data-cluster-ids={JSON.stringify(c.ids)}
      aria-label={`${c.ids.length} comitati — mostra l'elenco`}
      aria-expanded="false"
      class="absolute flex size-7 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border-2 border-paper bg-ink font-mono text-[11px] font-medium text-paper shadow transition-transform"
      style={`left: ${c.x}%; top: ${c.y}%;`}
    >
      {c.ids.length}
    </button>
  ))}
  <div
    data-map-caption
    class="mt-2 min-h-[28px] text-center font-mono text-[12px] tracking-[0.06em] text-ink-soft"
    aria-live="polite"
  >
    Tocca un punto per il comitato
  </div>
  {clusters.map((c, i) => (
    <div data-cluster-panel={i} hidden class="mx-auto mt-1 flex max-w-[420px] flex-wrap justify-center gap-2">
      {c.ids.map((id) => (
        <button
          type="button"
          data-goto={id}
          class="rounded-full border border-rule-light bg-paper px-3 py-1.5 font-display text-[13px] font-medium text-ink"
        >
          {byId.get(id)?.name ?? id}
        </button>
      ))}
    </div>
  ))}
</div>

<style>
  [data-committee-map] [data-dot-active="true"] [data-dot-visual] {
    transform: scale(1.5);
    outline: 2px solid var(--color-tangerine-deep);
    outline-offset: 2px;
  }
  [data-committee-map] [data-cluster-active="true"] {
    transform: translate(-50%, -50%) scale(1.15);
    background: var(--color-tangerine);
    color: var(--color-ink);
  }
  .map-card-active {
    outline: 2px solid var(--color-tangerine);
    outline-offset: 3px;
  }
</style>

<script>
  const map = document.querySelector("[data-committee-map]");
  if (map) {
    const caption = map.querySelector("[data-map-caption]");
    const cards = [...document.querySelectorAll("[data-committee-card]")];
    const linkBase = map.getAttribute("data-link-base");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const dotOf = (id) => map.querySelector(`[data-dot="${id}"]`);
    const cardOf = (id) => document.getElementById(id);

    function paint(id) {
      map.querySelectorAll("[data-dot]").forEach((b) =>
        b.setAttribute("data-dot-active", String(b.getAttribute("data-dot") === id)),
      );
      map.querySelectorAll("[data-cluster]").forEach((b) => {
        const ids = JSON.parse(b.getAttribute("data-cluster-ids") || "[]");
        b.setAttribute("data-cluster-active", String(ids.includes(id)));
      });
      cards.forEach((c) => c.classList.toggle("map-card-active", c.id === id));
    }

    function showClusterPanel(index) {
      map.querySelectorAll("[data-cluster-panel]").forEach((p) => {
        const show = p.getAttribute("data-cluster-panel") === String(index);
        p.toggleAttribute("hidden", !show);
      });
      map.querySelectorAll("[data-cluster]").forEach((b) =>
        b.setAttribute("aria-expanded", String(b.getAttribute("data-cluster") === String(index))),
      );
    }

    function captionFor(id) {
      const goto = map.querySelector(`[data-goto="${id}"]`);
      const name = goto?.textContent?.trim() ?? dotOf(id)?.getAttribute("title") ?? id;
      if (caption) caption.textContent = name;
    }

    function select(id, opts) {
      const { scroll = true, say = true } = opts || {};
      paint(id);
      showClusterPanel(-1);
      if (say) captionFor(id);
      const card = cardOf(id);
      if (card) {
        if (scroll) card.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "center" });
      } else if (linkBase) {
        window.location.href = `${linkBase}#${id}`;
      }
    }

    map.querySelectorAll("[data-dot]").forEach((b) =>
      b.addEventListener("click", () => select(b.getAttribute("data-dot") || "")),
    );
    map.querySelectorAll("[data-cluster]").forEach((b) =>
      b.addEventListener("click", () => {
        const i = b.getAttribute("data-cluster") || "0";
        showClusterPanel(Number(i));
        map.querySelectorAll("[data-cluster]").forEach((o) =>
          o.setAttribute("data-cluster-active", String(o === b)),
        );
        if (caption) {
          const names = [...map.querySelectorAll(`[data-cluster-panel="${i}"] [data-goto]`)].map((g) =>
            g.textContent?.trim(),
          );
          caption.textContent = names.join(" · ");
        }
      }),
    );
    map.querySelectorAll("[data-goto]").forEach((g) =>
      g.addEventListener("click", () => select(g.getAttribute("data-goto") || "")),
    );

    // "Mappa" buttons on cards scroll back up to the highlighted dot.
    document.querySelectorAll("[data-locate]").forEach((b) =>
      b.addEventListener("click", () => {
        const id = b.getAttribute("data-locate") || "";
        paint(id);
        showClusterPanel(-1);
        captionFor(id);
        map.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "center" });
      }),
    );

    // Deep link: /comitati#palermo scrolls to the card and highlights it.
    // Takes over from the browser's native anchor jump so the scrollspy
    // converges on the right card instead of repainting over it.
    if (cards.length > 0 && window.location.hash.length > 1) {
      const id = decodeURIComponent(window.location.hash.slice(1));
      if (cardOf(id)) {
        if ("scrollRestoration" in history) history.scrollRestoration = "manual";
        window.scrollTo(0, 0);
        select(id);
      }
    }

    // Scrollspy: keep dot and card in sync while the list scrolls.
    if (cards.length > 0 && "IntersectionObserver" in window) {
      const spy = new IntersectionObserver(
        (entries) => {
          const vis = entries
            .filter((e) => e.isIntersecting)
            .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
          if (vis && vis.target.id) {
            paint(vis.target.id);
            showClusterPanel(-1);
          }
        },
        { rootMargin: "-40% 0px -40% 0px" },
      );
      cards.forEach((c) => spy.observe(c));
    }
  }
</script>
"""

if __name__ == "__main__":
    main()
