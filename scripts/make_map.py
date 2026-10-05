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

const dots = [
__DOTS__
];

const byId = new Map(committees.map((c) => [c.id, c]));
---

<div class="relative mx-auto w-full max-w-[520px]">
  <img src="/italy-map.svg" alt="Italia — comitati locali AISF" class="w-full" />
  {dots.map((d) => {
    const c = byId.get(d.id);
    const frozen = c?.status === "frozen";
    return (
      <a
        href={`${linkBase}#${d.id}`}
        title={c?.name ?? d.id}
        aria-label={c?.name ?? d.id}
        class="group absolute -translate-x-1/2 -translate-y-1/2 before:absolute before:-inset-3 before:content-['']"
        style={`left: ${d.x}%; top: ${d.y}%;`}
      >
        <span
          class:list={[
            "block size-[12px] rounded-full border-2 border-paper shadow",
            frozen ? "bg-ink-soft" : "bg-tangerine",
          ]}
        ></span>
        <span class="pointer-events-none absolute bottom-full left-1/2 mb-1 hidden -translate-x-1/2 rounded-full bg-ink px-2 py-0.5 font-mono text-[10px] whitespace-nowrap text-paper group-hover:block">
          {c?.name ?? d.id}
        </span>
      </a>
    );
  })}
</div>
"""

if __name__ == "__main__":
    main()
