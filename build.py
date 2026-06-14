import json, os, html as H, re

POSTS_DIR = "posts"

def build_all():
    index_data = build_blog()
    print(f"Built {len(index_data)} posts")
    for p in index_data:
        print(f"  - {p['title']} ({p['date']})")

def build_blog():
    os.makedirs(POSTS_DIR, exist_ok=True)
    index = []
    if not os.path.isdir(POSTS_DIR):
        return index
    files = sorted(
        [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")],
        reverse=True
    )
    for f in files:
        slug = f[:-3]
        with open(os.path.join(POSTS_DIR, f), "r", encoding="utf-8") as fp:
            raw = fp.read()
        meta, body = parse_md(raw)
        html_content = md_to_html(body)
        out_path = os.path.join(POSTS_DIR, slug + ".html")
        with open(out_path, "w", encoding="utf-8") as fp:
            fp.write(html_content)
        index.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "date": meta.get("date", ""),
            "excerpt": meta.get("excerpt", ""),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        })
    with open(os.path.join(POSTS_DIR, "index.json"), "w", encoding="utf-8") as fp:
        json.dump(index, fp, ensure_ascii=False, indent=2)
    return index

def parse_md(raw):
    meta = {}
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = parts[2].strip()
    return meta, body

def md_to_html(text):
    lines = text.split("\n")
    out = []
    in_code = False
    in_list = False
    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append("<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(H.escape(line))
            continue
        # Close list if needed
        if in_list and not line.startswith("- "):
            out.append("</ul>")
            in_list = False
        if line.startswith("### "):
            out.append(f"<h3>{H.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{H.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{H.escape(line[2:])}</h1>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline_md(line[2:])}</li>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline_md(line[2:])}</blockquote>")
        elif line.strip() == "":
            out.append("<br>")
        else:
            out.append(f"<p>{inline_md(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)

def inline_md(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank">\1</a>', text)
    return text

if __name__ == "__main__":
    build_all()
