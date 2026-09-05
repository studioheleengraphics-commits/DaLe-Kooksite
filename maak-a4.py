#!/usr/bin/env python3
"""
Rendert de A4-kookboekpagina's uit a4/*.html naar pdf/<slug>.pdf.

De bronbestanden in a4/ zijn ingevulde kopieën van het sjabloon uit de skill
sh-kookboekpagina. Het echte renderen gebeurt door het build-script van die
skill, zodat de opmaak en de A4-maat daar op één plek vastliggen.

Gebruik:
    python3 maak-a4.py                        alle pagina's
    python3 maak-a4.py zalm-orzo-uit-de-oven  alleen deze
"""

import runpy
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
A4 = ROOT / "a4"
PDF = ROOT / "pdf"


def zoek_skill() -> Path:
    """De skill wordt gesynct naar een map met een wisselende naam."""
    treffers = sorted(Path("/root/.claude/skills").glob(
        "synced/*/sh-kookboekpagina/scripts/build.py"))
    if not treffers:
        sys.exit("Skill sh-kookboekpagina niet gevonden. Is ze nog ingeschakeld?")
    return treffers[-1]


def zoek_chromium() -> str | None:
    """Playwright vindt zijn browser niet altijd zelf in deze omgeving."""
    for pad in sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome")):
        return str(pad)
    return None


def wijs_chromium_aan(chromium: str) -> None:
    """Eenmalig, want een tweede laag over dezelfde functie botst met zichzelf."""
    from playwright.sync_api import BrowserType
    origineel = BrowserType.launch
    BrowserType.launch = (
        lambda self, **kw: origineel(self, executable_path=chromium, **kw))


def render(bron: Path, skill_build: Path) -> None:
    slug = bron.stem
    with tempfile.TemporaryDirectory() as tmp:
        werkmap = Path(tmp)
        shutil.copy(bron, werkmap / bron.name)
        oud = Path.cwd()
        try:
            import os
            os.chdir(werkmap)
            sys.argv = ["build.py", bron.name, slug]
            runpy.run_path(str(skill_build), run_name="__main__")
            gemaakt = werkmap / f"{slug}-kookboekpagina.pdf"
            if not gemaakt.exists():
                sys.exit(f"{slug}: geen PDF gemaakt, de inhoud past waarschijnlijk niet op één A4.")
            PDF.mkdir(exist_ok=True)
            shutil.copy(gemaakt, PDF / f"{slug}.pdf")
        finally:
            os.chdir(oud)
    print(f"  {slug}.pdf")


def main() -> None:
    skill_build = zoek_skill()
    chromium = zoek_chromium()
    gevraagd = sys.argv[1:]
    bronnen = ([A4 / f"{s}.html" for s in gevraagd] if gevraagd
               else sorted(A4.glob("*.html")))
    ontbreekt = [b for b in bronnen if not b.exists()]
    if ontbreekt:
        sys.exit("Niet gevonden: " + ", ".join(b.name for b in ontbreekt))

    if chromium:
        wijs_chromium_aan(chromium)

    print(f"Renderen met {skill_build}")
    for bron in bronnen:
        render(bron, skill_build)
    print(f"Klaar. {len(bronnen)} pagina's naar {PDF}/")


if __name__ == "__main__":
    main()
