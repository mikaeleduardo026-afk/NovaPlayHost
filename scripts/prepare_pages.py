#!/usr/bin/env python3
"""Extract site.rar into a GitHub Pages-ready static site without flattening assets."""
from __future__ import annotations
import html, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "site.rar"
PUBLIC = ROOT / "public"
PRODUCTS = [
    ("lumora", "Lumora", "Experiência e plataforma Lumora"),
    ("scriptlab", "ScriptLab", "Cursos, ferramentas e recursos ScriptLab"),
    ("mta-asset-viewer", "MTA Asset Viewer", "Visualização e empacotamento de assets para MTA:SA"),
    ("token-generator", "Gerador de Tokens", "Painel de emissão de tokens NovaPlayHost"),
]
SENSITIVE_NAMES = {".env", ".env.local", ".env.production", ".slkey", "credentials.json", "secrets.json", "id_rsa", "id_ed25519", "authorized_keys"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".keystore"}
SKIP_DIRS = {".git", ".github", "node_modules", "__macosx", ".svn"}

def unpack_archive() -> Path:
    if not ARCHIVE.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARCHIVE}")
    temp_root = Path(tempfile.mkdtemp(prefix="novaplayhost-unpack-"))
    extract_dir = temp_root / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["unar", "-q", "-o", str(extract_dir), str(ARCHIVE)], check=True)
    entries = list(extract_dir.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_dir

def copy_archive(source: Path) -> list[Path]:
    copied = []
    for item in sorted(source.rglob("*")):
        if not item.is_file():
            continue
        rel = item.relative_to(source)
        if any(part.lower() in SKIP_DIRS for part in rel.parts):
            continue
        name = item.name.lower()
        if name in SENSITIVE_NAMES or item.suffix.lower() in SENSITIVE_SUFFIXES or name.startswith(".env.") or "private-key" in name or "private_key" in name:
            print(f"[omitido por segurança] {rel.as_posix()}")
            continue
        target = PUBLIC / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        copied.append(target)
    return copied

def classify(path: Path) -> str | None:
    rel = path.relative_to(PUBLIC).as_posix().lower()
    try:
        content = path.read_text("utf-8", errors="ignore")[:16000].lower()
    except OSError:
        content = ""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", content, re.I | re.S)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
    hay = f"{rel} {title} {content[:6000]}"
    if "token" in hay and ("gerador" in hay or "generator" in hay or "token generator" in hay):
        return "token-generator"
    if "gerador-de-tokens" in rel:
        return "token-generator"
    if "asset viewer" in hay or "asset-viewer" in hay or "mtaasset" in hay or ("viewer" in hay and "mta" in hay):
        return "mta-asset-viewer"
    if "lumora" in hay:
        return "lumora"
    if "scriptlab" in hay or "script lab" in hay:
        return "scriptlab"
    return None

def rel_url(path: Path) -> str:
    return "./" + quote(path.relative_to(PUBLIC).as_posix(), safe="/-_.~")

def root_prefix(rel_path: str) -> str:
    parent = PurePosixPath(rel_path).parent
    depth = 0 if str(parent) == "." else len(parent.parts)
    return "../" * depth

def portal(product_pages: dict[str, Path]) -> str:
    cards = []
    for slug, title, description in PRODUCTS:
        page = product_pages.get(slug)
        if not page:
            continue
        cards.append(f'''<a class="card" href="{html.escape(rel_url(page), quote=True)}"><span class="tag">NOVAPLAYHOST / {html.escape(slug.upper())}</span><h2>{html.escape(title)}</h2><p>{html.escape(description)}</p><b class="open">Abrir projeto →</b></a>''')
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#090f1d"><title>NovaPlayHost — Central de Projetos</title><meta name="description" content="Portal oficial dos projetos NovaPlayHost."><style>
:root{{--bg:#090f1d;--panel:#101b2e;--line:#243653;--text:#edf4ff;--muted:#9aacc7;--accent:#5592ff}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 15% 0%,#18345d 0,transparent 42%),var(--bg);color:var(--text);font:16px/1.55 Inter,system-ui,Segoe UI,sans-serif}}.wrap{{width:min(1120px,calc(100% - 36px));margin:auto}}header{{padding:28px 0;border-bottom:1px solid var(--line)}}.brand{{font-weight:900;letter-spacing:.04em}}.brand span{{color:var(--accent)}}.hero{{padding:72px 0 38px}}.tag{{font-size:11px;letter-spacing:.15em;color:#82b2ff;font-weight:800}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.02;letter-spacing:-.05em;margin:16px 0}}.hero p{{max-width:650px;color:var(--muted);font-size:18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px;padding:20px 0 70px}}.card{{display:flex;flex-direction:column;min-height:210px;padding:24px;border:1px solid var(--line);border-radius:18px;background:linear-gradient(145deg,#14233a,#0e1727);color:inherit;text-decoration:none;transition:transform .2s,border-color .2s}}.card:hover{{transform:translateY(-4px);border-color:#5592ff}}.card h2{{margin:18px 0 6px;font-size:22px}}.card p{{margin:0;color:var(--muted);font-size:14px}}.open{{margin-top:auto;padding-top:24px;color:#a8c8ff}}footer{{border-top:1px solid var(--line);padding:28px 0 34px;color:var(--muted);font-size:12px}}footer a{{color:#b9d3ff}}.warning{{margin-top:12px;max-width:900px}}</style></head><body><header><div class="wrap brand">NOVA<span>PLAY</span>HOST</div></header><main class="wrap"><section class="hero"><div class="tag">CENTRAL OFICIAL</div><h1>Seus projetos,<br>em um só lugar.</h1><p>Acesse as plataformas e ferramentas da NovaPlayHost. Cada projeto abre diretamente sua página publicada.</p></section><section class="grid">{''.join(cards)}</section></main><footer><div class="wrap"><b>NovaPlayHost</b> · Powered by NovaHost · v1.0.0<br><a href="./legal.html#termos">Termos de Uso</a> · <a href="./legal.html#privacidade">Privacidade</a> · <a href="./legal.html#reembolso">Reembolso</a> · <a href="./legal.html#cookies">Cookies</a> · <a href="https://discord.gg/bsYX83YYmt" target="_blank" rel="noopener">Discord / Suporte</a><div class="warning">© 2026 NovaPlayHost. Todos os direitos reservados. É proibido plagiar, redistribuir ou comercializar materiais proprietários fora dos canais oficiais. A extração, modificação ou exploração de arquivos exige autorização expressa da NovaPlayHost e dos respectivos titulares dos direitos.</div></div></footer></body></html>'''

def add_footer(page: Path, rel_path: str, product_pages: dict[str, Path]) -> None:
    content = page.read_text("utf-8", errors="ignore")
    if "novaplayhost-shared-footer" in content.lower():
        return
    prefix = root_prefix(rel_path)
    nav = []
    for slug, title, _description in PRODUCTS:
        target = product_pages.get(slug)
        if target:
            href = prefix + rel_url(target).removeprefix("./")
            nav.append(f'<a href="{html.escape(href, quote=True)}">{html.escape(title)}</a>')
    footer = f'''<footer id="novaplayhost-shared-footer" style="margin-top:48px;padding:26px 18px;background:#09111f;color:#dce8fb;border-top:1px solid #273b5b;font:13px/1.6 system-ui,sans-serif"><div style="max-width:1180px;margin:auto"><strong style="letter-spacing:.08em">NOVAPLAYHOST</strong> <span style="color:#9bb0ce">· Powered by NovaHost · v1.0.0</span><nav style="margin:12px 0;display:flex;flex-wrap:wrap;gap:8px 14px">{' · '.join(nav)} <a href="{prefix}index.html">Início</a> <a href="{prefix}legal.html#termos">Termos de Uso</a> <a href="{prefix}legal.html#privacidade">Privacidade</a> <a href="{prefix}legal.html#reembolso">Reembolso</a> <a href="{prefix}legal.html#cookies">Cookies</a> <a href="https://discord.gg/bsYX83YYmt" target="_blank" rel="noopener">Discord / Contato / Suporte</a></nav><small style="color:#9bb0ce">© 2026 NovaPlayHost. Todos os direitos reservados. É proibido plagiar, redistribuir gratuitamente ou comercializar materiais proprietários fora dos canais oficiais. A extração, modificação ou exploração de arquivos exige autorização expressa da NovaPlayHost e dos respectivos titulares dos direitos.</small></div></footer>'''
    if re.search(r"</body\s*>", content, re.I):
        content = re.sub(r"</body\s*>", footer + "\n</body>", content, count=1, flags=re.I)
    else:
        content += footer
    page.write_text(content, encoding="utf-8")

def main() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)
    source = unpack_archive()
    copied = copy_archive(source)
    if not copied:
        raise RuntimeError("Nenhum arquivo foi extraído de site.rar")
    repo_legal = ROOT / "legal.html"
    if not (PUBLIC / "legal.html").exists() and repo_legal.is_file():
        shutil.copy2(repo_legal, PUBLIC / "legal.html")

    detected: dict[str, list[Path]] = {slug: [] for slug, _title, _desc in PRODUCTS}
    for page in PUBLIC.rglob("*"):
        if page.is_file() and page.suffix.lower() in {".html", ".htm"}:
            product = classify(page)
            if product:
                detected[product].append(page)

    if not detected["scriptlab"]:
        fallback = ROOT / "index.html"
        if fallback.is_file() and "scriptlab" in fallback.read_text("utf-8", errors="ignore")[:8000].lower():
            target = PUBLIC / "scriptlab.html"
            shutil.copy2(fallback, target)
            detected["scriptlab"].append(target)

    product_pages: dict[str, Path] = {}
    for slug, _title, _desc in PRODUCTS:
        candidates = detected[slug]
        if not candidates:
            print(f"[aviso] Página não identificada: {slug}")
            continue
        selected = sorted(candidates, key=lambda p: (1 if slug in p.relative_to(PUBLIC).as_posix().lower() else 0, 1 if slug.replace("-", "") in p.stem.lower().replace("-", "") else 0, p.as_posix()), reverse=True)[0]
        if selected.parent == PUBLIC and selected.name.lower() == "index.html":
            alias = PUBLIC / f"{slug}.html"
            shutil.copy2(selected, alias)
            selected = alias
        product_pages[slug] = selected

    if not product_pages:
        raise RuntimeError("Nenhuma página de projeto reconhecida em site.rar; publicação cancelada.")
    for page in [p for p in PUBLIC.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".htm"}]:
        rel = page.relative_to(PUBLIC).as_posix()
        if rel not in {"index.html", "legal.html"}:
            add_footer(page, rel, product_pages)
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    (PUBLIC / "index.html").write_text(portal(product_pages), encoding="utf-8")
    print("=== Arquivos publicados ===")
    for path in sorted(PUBLIC.rglob("*")):
        if path.is_file():
            print(f"{path.relative_to(PUBLIC).as_posix()}\t{path.stat().st_size}")
    print("=== Páginas de produto ===")
    for slug, path in product_pages.items():
        print(f"{slug}: {path.relative_to(PUBLIC).as_posix()}")

if __name__ == "__main__":
    main()
