#!/usr/bin/env python3
"""Prepare the public NovaPlayHost Pages bundle. Administrative token issuance is excluded."""
from __future__ import annotations
import html, re, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "site.rar"
PUBLIC = ROOT / "public"
PRODUCTS = [
    ("lumora", "Lumora", "Plataforma de aprendizagem."),
    ("scriptlab", "ScriptLab", "Academia de programação e recursos."),
    ("mta-asset-viewer", "MTA Asset Viewer", "Visualização e empacotamento de assets para MTA:SA."),
]
PRIVATE_DIRS = {"token-generator", "gerador-de-tokens", "tokens-admin", "token-admin", "admin-token"}
PRIVATE_FILES = {"token.html", "tokens.html", "gerador-de-tokens.html", "token-generator.html"}
SKIP_DIRS = {".git", ".github", "node_modules", "__macosx", ".svn"}

def unpack() -> Path:
    if not ARCHIVE.is_file():
        raise FileNotFoundError("site.rar não foi encontrado na raiz do repositório.")
    temp = Path(tempfile.mkdtemp(prefix="novaplayhost-public-"))
    dest = temp / "extract"
    dest.mkdir()
    subprocess.run(["unar", "-q", "-o", str(dest), str(ARCHIVE)], check=True)
    entries = list(dest.iterdir())
    return entries[0] if len(entries) == 1 and entries[0].is_dir() else dest

def is_private(rel: Path) -> bool:
    parts = [p.lower().replace("_", "-").replace(" ", "-") for p in rel.parts]
    if any(p in PRIVATE_DIRS for p in parts[:-1]):
        return True
    return rel.name.lower() in PRIVATE_FILES

def copy_public(source: Path) -> int:
    count = 0
    for file in sorted(source.rglob("*")):
        if not file.is_file():
            continue
        rel = file.relative_to(source)
        if any(p.lower() in SKIP_DIRS for p in rel.parts) or is_private(rel):
            continue
        if file.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".keystore"} or file.name.lower() in {".env", ".slkey", "credentials.json"}:
            continue
        target = PUBLIC / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
        count += 1
    return count

def classify(path: Path) -> str | None:
    rel = path.relative_to(PUBLIC)
    parts = [p.lower().replace("_", "-").replace(" ", "-") for p in rel.parts[:-1]]
    mapping = {
        "lumora": "lumora",
        "scriptlab": "scriptlab",
        "script-lab": "scriptlab",
        "mta-asset-viewer": "mta-asset-viewer",
        "mtaasset": "mta-asset-viewer",
        "asset-viewer": "mta-asset-viewer",
    }
    for part in parts:
        if part in mapping:
            return mapping[part]
    stem = path.stem.lower().replace("_", "-").replace(" ", "-")
    names = {
        "lumora": "lumora",
        "scriptlab": "scriptlab",
        "script-lab": "scriptlab",
        "mtaasset": "mta-asset-viewer",
        "mta-asset-viewer": "mta-asset-viewer",
        "asset-viewer": "mta-asset-viewer",
    }
    if stem in names:
        return names[stem]
    content = path.read_text("utf-8", errors="ignore")[:24000].lower()
    title = re.search(r"<title[^>]*>(.*?)</title>", content, re.I | re.S)
    heading = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.I | re.S)
    identity = " ".join(x for x in [
        re.sub(r"\\s+", " ", title.group(1)) if title else "",
        re.sub(r"<[^>]+>", " ", heading.group(1)) if heading else "",
    ]).lower()
    if "mta asset viewer" in identity or "mta:sa asset viewer" in identity:
        return "mta-asset-viewer"
    if "scriptlab" in identity or "script lab" in identity:
        return "scriptlab"
    if "lumora" in identity:
        return "lumora"
    return None

def portal(pages: dict[str, Path]) -> str:
    cards = []
    for slug, title, description in PRODUCTS:
        page = pages.get(slug)
        if not page:
            continue
        href = "./" + page.relative_to(PUBLIC).as_posix()
        cards.append(f'<a class="card" href="{html.escape(href, quote=True)}"><span class="tag">NOVAPLAYHOST / {html.escape(slug.upper())}</span><h2>{html.escape(title)}</h2><p>{html.escape(description)}</p><b class="open">Abrir projeto →</b></a>')
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#090f1d"><title>NovaPlayHost — Central de Projetos</title><style>
:root{{--bg:#090f1d;--line:#243653;--text:#edf4ff;--muted:#9aacc7;--accent:#5592ff}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 15% 0%,#18345d 0,transparent 42%),var(--bg);color:var(--text);font:16px/1.55 Inter,system-ui,Segoe UI,sans-serif}}.wrap{{width:min(1120px,calc(100% - 36px));margin:auto}}header{{padding:28px 0;border-bottom:1px solid var(--line)}}.brand{{font-weight:900;letter-spacing:.04em}}.brand span{{color:var(--accent)}}.hero{{padding:72px 0 38px}}.tag{{font-size:11px;letter-spacing:.15em;color:#82b2ff;font-weight:800}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.02;letter-spacing:-.05em;margin:16px 0}}.hero p{{max-width:650px;color:var(--muted);font-size:18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px;padding:20px 0 70px}}.card{{display:flex;flex-direction:column;min-height:210px;padding:24px;border:1px solid var(--line);border-radius:18px;background:linear-gradient(145deg,#14233a,#0e1727);color:inherit;text-decoration:none;transition:transform .2s,border-color .2s}}.card:hover{{transform:translateY(-4px);border-color:#5592ff}}.card h2{{margin:18px 0 6px;font-size:22px}}.card p{{margin:0;color:var(--muted);font-size:14px}}.open{{margin-top:auto;padding-top:24px;color:#a8c8ff}}footer{{border-top:1px solid var(--line);padding:28px 0 34px;color:var(--muted);font-size:12px}}footer a{{color:#b9d3ff}}.warning{{margin-top:12px;max-width:900px}}</style></head><body><header><div class="wrap brand">NOVA<span>PLAY</span>HOST</div></header><main class="wrap"><section class="hero"><div class="tag">CENTRAL OFICIAL</div><h1>Seus projetos,<br>em um só lugar.</h1><p>Acesse as plataformas e ferramentas da NovaPlayHost.</p></section><section class="grid">{''.join(cards)}</section></main><footer><div class="wrap"><b>NovaPlayHost</b> · Powered by NovaHost · v1.0.0<br><a href="./legal.html#termos">Termos de Uso</a> · <a href="./legal.html#privacidade">Privacidade</a> · <a href="./legal.html#reembolso">Reembolso</a> · <a href="./legal.html#cookies">Cookies</a> · <a href="https://discord.gg/bsYX83YYmt" target="_blank" rel="noopener">Discord / Suporte</a><div class="warning">© 2026 NovaPlayHost. Todos os direitos reservados. É proibido plagiar, redistribuir ou comercializar materiais proprietários fora dos canais oficiais. A extração, modificação ou exploração de arquivos exige autorização expressa da NovaPlayHost e dos respectivos titulares dos direitos.</div></div></footer></body></html>"""

def prepare_html_pages(pages: dict[str, Path]) -> None:
    for page in list(PUBLIC.rglob("*.html")) + list(PUBLIC.rglob("*.htm")):
        if not page.is_file():
            continue
        content = page.read_text("utf-8", errors="ignore")
        content = re.sub(r'<a\\b[^>]*href=["\\'][^"\\']*(?:token-generator|gerador-de-tokens)[^"\\']*["\\'][^>]*>[\\s\\S]*?</a>', "", content, flags=re.I)
        content = re.sub(r'(?i)(href\\s*=\\s*["\\'])mailto:[^"\\']+(["\\'])', r'\\1https://discord.gg/bsYX83YYmt\\2', content)
        content = re.sub(r"(?i)\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b", "Atendimento pelo Discord", content)
        page.write_text(content, encoding="utf-8")
    for slug, page in pages.items():
        target = page.parent / "legal.html"
        if not target.exists() and (PUBLIC / "legal.html").exists():
            shutil.copy2(PUBLIC / "legal.html", target)

def main() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)
    source = unpack()
    copied = copy_public(source)
    if copied == 0:
        raise RuntimeError("Nenhum arquivo público foi extraído do site.rar.")
    if not (PUBLIC / "legal.html").exists() and (ROOT / "legal.html").exists():
        shutil.copy2(ROOT / "legal.html", PUBLIC / "legal.html")
    found: dict[str, list[Path]] = {slug: [] for slug, _, _ in PRODUCTS}
    for page in PUBLIC.rglob("*"):
        if page.is_file() and page.suffix.lower() in {".html", ".htm"}:
            category = classify(page)
            if category:
                found[category].append(page)
    pages: dict[str, Path] = {}
    for slug, _, _ in PRODUCTS:
        candidates = found[slug]
        if not candidates:
            raise RuntimeError(f"Página principal não identificada para {slug}.")
        pages[slug] = sorted(candidates, key=lambda p: (1 if p.name.lower() == "index.html" else 0, p.as_posix()), reverse=True)[0]
        if pages[slug].parent == PUBLIC and pages[slug].name.lower() == "index.html":
            alias = PUBLIC / f"{slug}.html"
            shutil.copy2(pages[slug], alias)
            pages[slug] = alias
    prepare_html_pages(pages)
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    (PUBLIC / "index.html").write_text(portal(pages), encoding="utf-8")
    if (PUBLIC / "token-generator").exists():
        shutil.rmtree(PUBLIC / "token-generator")
    leaks = []
    for f in PUBLIC.rglob("*"):
        if f.is_file() and (f.name.lower() in PRIVATE_FILES or any(x.lower() in PRIVATE_DIRS for x in f.relative_to(PUBLIC).parts[:-1])):
            leaks.append(f.relative_to(PUBLIC).as_posix())
    if leaks:
        raise RuntimeError("Arquivos administrativos encontrados na área pública: " + ", ".join(leaks))
    print("Public pages prepared:")
    for slug, page in pages.items():
        print(f"{slug}: {page.relative_to(PUBLIC).as_posix()}")
    print(f"Public files: {sum(1 for x in PUBLIC.rglob('*') if x.is_file())}")

if __name__ == "__main__":
    main()
