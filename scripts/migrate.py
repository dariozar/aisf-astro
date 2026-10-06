"""One-shot migration: old Jekyll site -> Astro content collections.

Source: /tmp/opencode/ai-sf-github (https://github.com/ai-sf/ai-sf.github.io)
Outputs (all git-managed, PagesCMS-editable):
  src/content/events/*.md  (54 historic + cisf-2026 added by hand)
  src/content/news/*.md    (74 blog posts)
  src/data/committees.yml  (top-level array, list:true in PagesCMS)
  src/data/executive.yml   (current mandate, top-level array)
  src/data/executive-past.yml (past mandates, compact)
  src/data/documents.yml   (flat rows: year, group, name, url)
"""
import os
import re
import glob
import yaml

SRC = "/tmp/opencode/ai-sf-github"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[àáâä]", "a", s)
    s = re.sub(r"[èéêë]", "e", s)
    s = re.sub(r"[ìíîï]", "i", s)
    s = re.sub(r"[òóôö]", "o", s)
    s = re.sub(r"[ùúûü]", "u", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "untitled"


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def dump(path, front, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = body.replace("/img/", "/images/")
    with open(path, "w") as f:
        f.write("---\n" + yaml.safe_dump(front, allow_unicode=True,
                                         sort_keys=False) + "---\n" + body.lstrip())


MONTHS = {"gen": "01", "feb": "02", "mar": "03", "apr": "04",
          "mag": "05", "giu": "06", "lug": "07", "ago": "08",
          "set": "09", "ott": "10", "nov": "11", "dic": "12"}


def to_iso(s):
    s = str(s).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r"^(\d{1,2})\s+([a-zàé]+)\s+(\d{4})", s.lower())
    if m and m.group(2)[:3] in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(2)[:3]]}-{int(m.group(1)):02d}"
    m = re.match(r"^(\d{4})", s)
    return f"{m.group(1)}-01-01" if m else "1900-01-01"


def migrate_events():
    out = os.path.join(HERE, "src", "content", "events")
    n = 0
    for f in sorted(glob.glob(os.path.join(SRC, "_events", "*.md"))):
        front, body = split_frontmatter(open(f).read())
        base = os.path.splitext(os.path.basename(f))[0]
        date = str(front.get("startingdate") or front.get("date") or base[:10])
        dump(os.path.join(out, slugify(front.get("title", base)) + ".md"), {
            "id": slugify(front.get("title", base)),
            "title": front.get("title", base),
            "date": date,
            "dateISO": to_iso(date),
            "endDate": str(front.get("endingdate") or ""),
            "location": front.get("place") or "",
            "type": front.get("categories") or "evento",
            "cover": (front.get("cover") or "").replace("/img/", "/images/"),
            "status": "past",
        }, body)
        n += 1
    print(f"events: {n}")


def migrate_news():
    out = os.path.join(HERE, "src", "content", "news")
    n = 0
    for f in sorted(glob.glob(os.path.join(SRC, "blog", "_posts", "*.md"))):
        front, body = split_frontmatter(open(f).read())
        base = os.path.splitext(os.path.basename(f))[0]
        title = front.get("title", base[11:].replace("_", " "))
        dump(os.path.join(out, slugify(title) + ".md"), {
            "title": title,
            "date": str(front.get("date") or base[:10]),
        }, body)
        n += 1
    print(f"news: {n}")


def migrate_committees():
    data = yaml.safe_load(open(os.path.join(SRC, "_data", "LC.yml")))
    rows = []
    for c in data:
        name = c.get("nome", "")
        frozen = bool(c.get("congelato") or c.get("commissariato"))
        rows.append({
            "id": slugify(name),
            "name": name,
            "president": c.get("presidente") or "",
            "founded": str(c.get("fondazione") or ""),
            "email": ((c.get("mail") or "") + "@ai-sf.it") if c.get("mail") else "",
            "status": "frozen" if frozen else "active",
            "photo": (c.get("img") or "").replace("/img/", "/images/"),
            "logo": (c.get("logo") or "").replace("/img/", "/images/"),
            "past_presidents": str(c.get("ex") or ""),
            "link": c.get("fb") or "",
            "rules": c.get("regolamento") or "",
        })
    path = os.path.join(HERE, "src", "data", "committees.yml")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    yaml.safe_dump(rows, open(path, "w"), allow_unicode=True, sort_keys=False)
    print(f"committees: {len(rows)}")


def migrate_executive():
    data = yaml.safe_load(open(os.path.join(SRC, "_data", "EC.yml")))
    current, past = data[0], data[1:]
    members = [{
        "id": slugify(m.get("nome", "")),
        "name": m.get("nome", ""),
        "role": m.get("ruolo", ""),
        "bio": m.get("descr") or "",
        "email": ((m.get("mail") or "") + "@ai-sf.it") if m.get("mail") else "",
        "photo": (m.get("img") or "").replace("/img/", "/images/"),
    } for m in current.get("membri", [])]
    d = os.path.join(HERE, "src", "data")
    os.makedirs(d, exist_ok=True)
    yaml.safe_dump(members, open(os.path.join(d, "executive.yml"), "w"),
                   allow_unicode=True, sort_keys=False)
    past_rows = [{"id": slugify(f"mandato-{p.get('anno', '')}"),
                    "mandate": p.get("anno", ""),
                    "members": [{"name": m.get("nome", ""),
                                 "role": m.get("ruolo", "")}
                                for m in p.get("membri", [])]}
                   for p in past]
    yaml.safe_dump(past_rows, open(os.path.join(d, "executive-past.yml"), "w"),
                   allow_unicode=True, sort_keys=False)
    print(f"executive: {len(members)} current, {len(past_rows)} past mandates")


PRESS_KIT = [
    ("Flyer AISF", "https://drive.google.com/file/d/1MvvBdEfrkAJUPbWm7aULKVYEyK-7jbdH/view?usp=sharing"),
    ("Flyer verticale AISF", "https://drive.google.com/file/d/1oit9c9RRuonS0B54syB_qmrapjIuTItX/view?usp=sharing"),
    ("Poster AISF", "https://drive.google.com/file/d/1JFLHtNyb2JqeQBeJ1sGMtbZ2akTTeQ9z/view?usp=sharing"),
]
VOLUNTEER_BOOK = (
    "Libro dei volontari",
    "https://drive.google.com/file/d/1sTT_SZs0jZAiUlGKASXv6L1VZM0g1fE3/view?ts=6a11d09e",
)


def migrate_documents():
    rows = []
    for name, url in PRESS_KIT:
        rows.append({"id": slugify(f"press-{name}"), "year": "",
                     "group": "Press kit", "name": name, "url": url})
    rows.append({"id": "libro-dei-volontari", "year": "",
                 "group": "Libro dei volontari", "name": VOLUNTEER_BOOK[0],
                 "url": VOLUNTEER_BOOK[1]})
    for fname in ("documenti.yml", "verbali.yml"):
        data = yaml.safe_load(open(os.path.join(SRC, "_data", fname)))
        for group in data or []:
            year = str(group.get("anno", ""))
            for doc in group.get("documenti", []) or []:
                rows.append({"id": slugify(f"{year}-{doc.get('nome','')}"),
                             "year": year, "group": "Documenti",
                             "name": doc.get("nome", ""),
                             "url": doc.get("link", "")})
            for verb in group.get("verbali", []) or []:
                for meeting in verb.get("riunioni", []) or []:
                    rows.append({
                        "id": slugify(f"{year}-{verb.get('tipo','')}-{meeting.get('data','')}"),
                        "year": year, "group": verb.get("tipo", "Verbali"),
                        "name": meeting.get("dettagli") or meeting.get("data", ""),
                        "url": meeting.get("link", "")})
    seen = {}
    for i, r in enumerate(rows):
        r["ord"] = i
    for r in rows:
        if r["id"] in seen:
            seen[r["id"]] += 1
            r["id"] = f"{r['id']}-{seen[r['id']]}"
        else:
            seen[r["id"]] = 0
    path = os.path.join(HERE, "src", "data", "documents.yml")
    yaml.safe_dump(rows, open(path, "w"), allow_unicode=True, sort_keys=False)
    print(f"documents: {len(rows)}")


if __name__ == "__main__":
    migrate_events()
    migrate_news()
    migrate_committees()
    migrate_executive()
    migrate_documents()
