#!/usr/bin/env python3
"""Make public app sessions persistent and add a return-to-portal button."""
from pathlib import Path
import re

PUBLIC = Path("public")
BUTTON = (
    '<a class="nph-central-return" href="../index.html" '
    'aria-label="Voltar à Central Oficial NovaPlayHost" '
    'style="position:fixed;z-index:999999;top:12px;left:12px;display:inline-flex;'
    'align-items:center;gap:8px;padding:10px 14px;border:1px solid #45658f;'
    'border-radius:24px;background:#10213b;color:#fff;text-decoration:none;'
    'font:700 13px/1.2 system-ui,sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.28)">'
    '← Central oficial</a>'
)

def replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        print(f"[info] {label}: trecho não encontrado ou já aplicado")
        return text
    print(f"[ok] {label}")
    return text.replace(old, new, 1)

def main() -> None:
    lumora = PUBLIC / "lumora" / "index.html"
    scriptlab = PUBLIC / "scriptlab" / "index.html"
    viewer = PUBLIC / "mta-asset-viewer" / "index.html"
    for page in (lumora, scriptlab, viewer):
        if not page.is_file():
            raise FileNotFoundError(f"Página não encontrada: {page}")

    text = lumora.read_text("utf-8", errors="ignore")
    text = replace(text,
        "let currentEmail=null,currentSubject=null",
        "let currentEmail=(db.session&&db.users[db.session])?db.session:null,currentSubject=null",
        "restaurar sessão Lumora")
    text = replace(text,
        "if(!user.licenseActive){alertBox('loginAlert','Esta conta ainda não possui uma licença ativa.');return;}",
        "",
        "permitir login Lumora com licença a renovar")
    text = replace(text,
        "if(db.session&&db.users[db.session]?.licenseActive){currentEmail=db.session;openStudentApp();}else updatePublicHeader();",
        "if(db.session&&db.users[db.session]){currentEmail=db.session;openStudentApp();}else{db.session=null;currentEmail=null;updatePublicHeader();}",
        "restaurar sessão Lumora na inicialização")
    lumora.write_text(text, encoding="utf-8")

    text = scriptlab.read_text("utf-8", errors="ignore")
    text = replace(text,
        "    if (!hasActiveAccess(user)) { showAlert('loginAlert', 'Seu acesso não está ativo ou o prazo do token terminou.'); return; }\n",
        "",
        "permitir login ScriptLab com licença a renovar")
    old = """  if (activeUser) {
    const savedUser = store.users[activeUser];
    if (savedUser && hasActiveAccess(savedUser)) {
      if (savedUser.learning) { renderDashboard(); showPage('dashboard'); }
      else showAssessment();
    } else {
      activeUser = null;
      store.currentUser = null;
      saveStore();
      updateNavState();
    }
  }"""
    new = """  if (activeUser) {
    const savedUser = store.users[activeUser];
    if (savedUser) {
      if (savedUser.learning) { renderDashboard(); showPage('dashboard'); }
      else showAssessment();
    } else {
      activeUser = null;
      store.currentUser = null;
      saveStore();
      updateNavState();
    }
  }"""
    text = replace(text, old, new, "manter sessão ScriptLab quando licença expirar")
    scriptlab.write_text(text, encoding="utf-8")

    for page in (lumora, scriptlab, viewer):
        text = page.read_text("utf-8", errors="ignore")
        if "nph-central-return" not in text:
            text = re.sub(r"</body\\s*>", BUTTON + "\\n</body>", text, count=1, flags=re.I)
            page.write_text(text, encoding="utf-8")
            print(f"[ok] botão Central oficial: {page}")
        else:
            print(f"[info] botão Central oficial já existe: {page}")

if __name__ == "__main__":
    main()
