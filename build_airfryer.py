#!/usr/bin/env python3
"""
Crispy DaLe - statische site met airfryertijden.

Leest alle producten uit airfryer/*.json en schrijft een zelfstandige
mini-site naar docs/airfryer/. Eén overzichtspagina waarop je zoekt,
uitklapt en een timer start die je door meerdere bakstappen loodst,
en één hulppagina met de omrekening van oven naar airfryer.

Wordt vanzelf meegebouwd door build.py. Los draaien mag ook:
    python3 build_airfryer.py
"""

import json
import html
import shutil
import unicodedata
import re
from pathlib import Path

ROOT = Path(__file__).parent
BRON = ROOT / "airfryer"
FOTOS = BRON / "fotos"

SITE_TITEL = "Crispy DaLe"
SITE_ONDERTITEL = "Airfryertijden · Studio HeLeen"

# Waar het issueformulier staat, voor de knop "voorgoed op de site".
REPO = "studioheleengraphics-commits/DaLe-Kooksite"

# ---------------------------------------------------------------- stijl ----

CSS = """
:root{
  --rood:#AD2C2C; --zeegroen:#77968E; --inkt:#1F1D1A;
  --inkt-zacht:#7B7777; --inkt-licht:#ADA7A7;
  --papier:#F0EEEB; --wit:#FFFFFF; --kaart:#FAFAFA; --lijn:#E8E8E8;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
html{-webkit-text-size-adjust:100%;}
[hidden]{display:none !important;}
body{
  margin:0; background:var(--papier); color:var(--inkt);
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  font-size:17px; line-height:1.6; padding-bottom:70px;
}
body.timert{padding-bottom:172px;}
.wrap{max-width:760px; margin:0 auto; padding:0 20px;}
a{color:var(--rood); text-decoration:none;}

/* kop van de site */
.kop{background:var(--wit); border-bottom:1px solid var(--lijn); padding:24px 0 20px;}
.koprij{display:flex; align-items:center; justify-content:space-between; gap:14px;}
.kop h1{font-family:'DM Sans',sans-serif; font-weight:700; font-size:30px;
  margin:0; letter-spacing:-.4px;}
.kop h1 span{color:var(--rood);}
.kop p{margin:4px 0 0; color:var(--inkt-zacht); font-size:13px;
  letter-spacing:1.4px; text-transform:uppercase;}
.pil{border:1px solid var(--lijn); border-radius:999px; padding:8px 14px;
  font-size:13px; color:var(--zeegroen); background:var(--wit); white-space:nowrap;
  font-family:'DM Sans',sans-serif;}

/* uitleg bovenaan */
.noot{background:var(--wit); border:1px solid var(--lijn); border-radius:12px;
  padding:14px 18px; margin:20px 0 0; font-size:14px; color:var(--inkt-zacht);}
.noot b{color:var(--inkt); font-family:'DM Sans',sans-serif; font-weight:500;}

/* zoeken en filters */
.zoek{width:100%; padding:13px 16px; border:1px solid var(--lijn);
  border-radius:10px; background:var(--wit); font-size:16px;
  font-family:inherit; color:var(--inkt); margin:16px 0 12px;}
.zoek:focus{outline:none; border-color:var(--zeegroen);}
.chips{display:flex; gap:8px; margin-bottom:20px; overflow-x:auto;
  padding-bottom:4px; scrollbar-width:none; -webkit-overflow-scrolling:touch;}
.chips::-webkit-scrollbar{display:none;}
.chip{flex:none; border:1px solid var(--lijn); background:var(--wit);
  color:var(--inkt-zacht); padding:7px 14px; border-radius:999px; font-size:13px;
  font-family:inherit; cursor:pointer; letter-spacing:.3px; white-space:nowrap;}
.chip.aan{background:var(--rood); border-color:var(--rood); color:var(--wit);}
.chip.ster{color:var(--rood);}
.chip.ster.aan{color:var(--wit);}

/* groepen */
.groep{margin-bottom:26px;}
.groepkop{font-family:'DM Sans',sans-serif; font-size:11px; letter-spacing:2px;
  text-transform:uppercase; color:var(--rood); margin:0 0 4px;}
.groepintro{margin:0 0 12px; font-size:14px; color:var(--inkt-zacht);}

/* rijen */
.item{background:var(--wit); border:1px solid var(--lijn); border-radius:12px;
  margin-bottom:8px; overflow:hidden;}
.rij{display:flex; align-items:center; gap:12px; width:100%; text-align:left;
  background:none; border:0; padding:13px 16px; font-family:inherit;
  font-size:17px; color:var(--inkt); cursor:pointer;}
.rij .foto{width:46px; height:46px; border-radius:9px; object-fit:cover;
  background:var(--papier); flex:none;}
.rij .naam{flex:1; min-width:0; font-family:'DM Sans',sans-serif; font-weight:500;
  font-size:16px; line-height:1.3;}
.rij .naam i{color:var(--rood); font-style:normal; font-size:13px; margin-left:5px;}
.rij .tijd{font-family:'DM Sans',sans-serif; font-size:13.5px; color:var(--zeegroen);
  white-space:nowrap; text-align:right;}
.rij .pijl{color:var(--inkt-licht); font-size:12px; transition:transform .15s; flex:none;}
.rij.open{border-bottom:1px solid var(--lijn);}
.rij.open .pijl{transform:rotate(90deg);}
.rij.open .tijd{color:var(--rood);}

/* uitgeklapt paneel */
.paneel{padding:16px 18px 20px; background:var(--kaart);}
.lading{display:flex; gap:8px; margin-bottom:16px;}
.lknop{flex:1; border:1px solid var(--lijn); background:var(--wit);
  color:var(--inkt-zacht); border-radius:9px; padding:9px 6px; font-size:13px;
  font-family:inherit; cursor:pointer;}
.lknop.aan{background:var(--zeegroen); border-color:var(--zeegroen); color:var(--wit);}

/* bakstappen */
ol.stappen{list-style:none; margin:0; padding:0;}
ol.stappen li{display:flex; gap:12px; padding:11px 0; border-bottom:1px solid var(--lijn);}
ol.stappen li .nr{font-family:'DM Sans',sans-serif; font-weight:700; font-size:15px;
  color:var(--rood); min-width:16px;}
ol.stappen li .lijf{flex:1; min-width:0;}
ol.stappen li .wat{display:block; font-family:'DM Sans',sans-serif; font-size:10px;
  letter-spacing:1.4px; text-transform:uppercase; color:var(--inkt-licht);}
ol.stappen li .zet{font-family:'DM Sans',sans-serif; font-weight:500; font-size:17px;}
ol.stappen li .schud{display:block; font-size:13px; color:var(--zeegroen);}
ol.stappen li .stand, ol.stappen li .functie{display:inline-block; margin-left:8px;
  padding:2px 9px; border-radius:999px; font-family:'DM Sans',sans-serif;
  font-size:11px; font-weight:500; letter-spacing:.6px; vertical-align:2px;}
ol.stappen li .stand{background:var(--zeegroen); color:var(--wit);}
ol.stappen li .functie{border:1px solid var(--zeegroen); color:var(--zeegroen);}

.getest{margin:12px 0 0; font-size:13.5px; color:var(--zeegroen);}
.feiten{display:grid; grid-template-columns:repeat(2,1fr); gap:14px 18px;
  padding:14px 0 16px; border-bottom:1px solid var(--lijn);}
.feiten:empty{display:none;}
.feiten div span{display:block; font-family:'DM Sans',sans-serif; font-size:10px;
  letter-spacing:1.4px; text-transform:uppercase; color:var(--inkt-licht);}
.feiten div b{font-family:'DM Sans',sans-serif; font-weight:500; font-size:16px;}
.feiten div.kern b{color:var(--rood);}
.regels{margin:14px 0 0;}
.regels p{margin:0 0 10px; font-size:15px; color:var(--inkt);}
.regels p span{color:var(--inkt-licht); font-family:'DM Sans',sans-serif;
  font-size:10px; letter-spacing:1.4px; text-transform:uppercase; display:block;}
.ptip{background:var(--papier); border-left:3px solid var(--rood);
  border-radius:0 10px 10px 0; padding:10px 16px; margin:14px 0 0;
  display:flex; gap:10px; align-items:flex-start;}
.ptip .pen{color:var(--rood); font-size:14px; line-height:1.6;}
.ptip p{font-family:'Caveat',cursive; font-size:20px; line-height:1.3; margin:0;}
.volnoot{margin:12px 0 0; font-size:13px; color:var(--zeegroen);}
.timerknop:active{background:var(--rood); color:var(--wit);}

.paneelknoppen{display:flex; gap:8px; margin-top:16px;}
.timerknop{flex:2; margin:0; padding:13px; border-radius:10px;
  border:1px solid var(--rood); background:var(--wit); color:var(--rood);
  font-family:'DM Sans',sans-serif; font-weight:500; font-size:15px; cursor:pointer;}
.pasaan{flex:1; padding:13px 6px; border-radius:10px; border:1px solid var(--lijn);
  background:var(--wit); color:var(--inkt-zacht); font-family:inherit;
  font-size:14px; cursor:pointer;}
.eigenrij:empty{display:none;}
.eigennoot{margin:16px 0 8px; font-size:13.5px; color:var(--zeegroen);}
.voorgoed{flex:2; text-align:center; padding:13px 6px; border-radius:10px;
  border:1px solid var(--zeegroen); background:var(--zeegroen); color:var(--wit);
  font-family:'DM Sans',sans-serif; font-weight:500; font-size:14px;}
.terugzet{flex:1; padding:13px 6px; border-radius:10px; border:1px solid var(--lijn);
  background:var(--wit); color:var(--inkt-zacht); font-family:inherit;
  font-size:14px; cursor:pointer;}
.rij .hier{display:inline-block; margin-left:7px; padding:1px 8px; border-radius:999px;
  border:1px solid var(--inkt-licht); color:var(--inkt-licht);
  font-family:'DM Sans',sans-serif; font-size:10px; letter-spacing:.6px;
  vertical-align:1px;}
.item.eigen{border-color:var(--zeegroen);}
.balk button.nieuw{border-color:var(--rood); color:var(--rood);
  font-family:'DM Sans',sans-serif; font-weight:500;}

/* het venster om iets toe te voegen of bij te stellen */
.venster{position:fixed; inset:0; z-index:20; background:rgba(31,29,26,.55);
  display:flex; align-items:flex-end; justify-content:center;}
.venster-kaart{background:var(--wit); width:100%; max-width:520px;
  max-height:92vh; overflow-y:auto; border-radius:16px 16px 0 0;
  padding:22px 20px 24px;}
.venster-kaart h3{font-family:'DM Sans',sans-serif; font-size:20px; margin:0 0 18px;
  color:var(--rood);}
.venster-kaart .veld{margin-bottom:14px;}
.venster-kaart select, .venster-kaart textarea{width:100%; padding:12px 14px;
  border:1px solid var(--lijn); border-radius:10px; font-size:16px;
  font-family:inherit; color:var(--inkt); background:var(--wit);}
.venster-kaart textarea{resize:vertical;}
.venster-kaart .ronde{background:var(--kaart); border-radius:10px;
  padding:14px 14px 2px; margin-bottom:12px;}
.vink{display:flex; align-items:center; gap:10px; margin:0 0 14px;
  font-size:15px; color:var(--inkt);}
.vink input{width:20px; height:20px; accent-color:var(--zeegroen);}
.vensternoot{font-size:13px; color:var(--inkt-zacht); margin:0 0 16px;}
.venster-knoppen{display:flex; gap:10px;}
.venster-knoppen button{flex:1; padding:14px; border-radius:10px;
  border:1px solid var(--lijn); background:var(--wit); color:var(--inkt-zacht);
  font-family:inherit; font-size:15px; cursor:pointer;}
.venster-knoppen button.hoofd{background:var(--rood); border-color:var(--rood);
  color:var(--wit); font-family:'DM Sans',sans-serif; font-weight:500;}

.leeg{color:var(--inkt-zacht); text-align:center; padding:30px 0;}
.voet{text-align:center; color:var(--inkt-licht); font-size:12px;
  letter-spacing:.6px; padding:6px 0 30px;}

/* vaste balk onderaan */
.balk{position:fixed; left:0; right:0; bottom:0; background:var(--wit);
  border-top:1px solid var(--lijn); display:flex; gap:10px; padding:10px 16px;
  justify-content:center; z-index:9;}
.balk button, .balk a{flex:1; max-width:180px; text-align:center; padding:11px 4px;
  border-radius:10px; border:1px solid var(--lijn); background:var(--wit);
  color:var(--inkt); font-size:13.5px; font-family:inherit; cursor:pointer;
  white-space:nowrap;}
.balk button.aan{background:var(--zeegroen); border-color:var(--zeegroen); color:var(--wit);}

/* timerbalk, zweeft boven de vaste balk */
.timerbalk{position:fixed; left:0; right:0; bottom:62px; z-index:10;
  background:var(--inkt); color:var(--wit); padding:10px 16px 12px;}
.timerbalk.schud{background:var(--zeegroen);}
.timerbalk.af{background:var(--rood);}
.tb-boven{display:flex; align-items:center; gap:12px;}
.tb-links{flex:1; min-width:0;}
.tb-links b{display:block; font-family:'DM Sans',sans-serif; font-weight:500;
  font-size:15px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.tb-links span{display:block; font-size:12.5px; opacity:.8;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.tb-klok{font-family:'DM Sans',sans-serif; font-weight:700; font-size:27px;
  font-variant-numeric:tabular-nums; letter-spacing:-.5px;}
.tb-knoppen{display:flex; gap:8px; margin-top:9px;}
.tb-knoppen button{flex:1; border:1px solid rgba(255,255,255,.4); background:transparent;
  color:var(--wit); border-radius:9px; padding:9px 6px; font-size:13.5px;
  font-family:inherit; cursor:pointer;}
.tb-knoppen button#tb-next{background:var(--wit); color:var(--rood); border-color:var(--wit);
  font-family:'DM Sans',sans-serif; font-weight:500;}

/* omrekenpagina */
.kaart{background:var(--wit); border:1px solid var(--lijn); border-radius:12px;
  padding:20px 22px; margin-bottom:16px;}
.kaart h2{font-family:'DM Sans',sans-serif; font-size:20px; margin:0 0 6px;}
.kaart p.uit{margin:0 0 16px; font-size:15px; color:var(--inkt-zacht);}
.richting{display:flex; gap:8px; margin-bottom:16px;}
.richting button{flex:1; border:1px solid var(--lijn); background:var(--kaart);
  color:var(--inkt-zacht); border-radius:9px; padding:10px 6px; font-size:13px;
  font-family:inherit; cursor:pointer;}
.richting button.aan{background:var(--rood); border-color:var(--rood); color:var(--wit);}
.velden{display:flex; gap:12px;}
.veld{flex:1;}
.veld label{display:block; font-family:'DM Sans',sans-serif; font-size:10px;
  letter-spacing:1.4px; text-transform:uppercase; color:var(--inkt-licht);
  margin-bottom:5px;}
.veld input{width:100%; padding:12px 14px; border:1px solid var(--lijn);
  border-radius:10px; font-size:17px; font-family:'DM Sans',sans-serif;
  color:var(--inkt); background:var(--wit);}
.veld input:focus{outline:none; border-color:var(--zeegroen);}
.veld input::-webkit-outer-spin-button,
.veld input::-webkit-inner-spin-button{-webkit-appearance:none; margin:0;}
.veld input[type=number]{-moz-appearance:textfield;}
.uitkomst{margin-top:18px; background:var(--papier); border-radius:10px;
  padding:16px 18px; text-align:center;}
.uitkomst span{display:block; font-family:'DM Sans',sans-serif; font-size:10px;
  letter-spacing:1.4px; text-transform:uppercase; color:var(--inkt-licht);}
.uitkomst b{font-family:'DM Sans',sans-serif; font-weight:700; font-size:26px;
  color:var(--rood); letter-spacing:-.5px;}
table.kern{width:100%; border-collapse:collapse; font-size:15px;}
table.kern td{padding:10px 0; border-bottom:1px solid var(--lijn);}
table.kern td:last-child{text-align:right; font-family:'DM Sans',sans-serif;
  font-weight:500; color:var(--rood); white-space:nowrap;}
table.kern tr:last-child td{border-bottom:0;}
ul.regelset{margin:0; padding-left:20px;}
ul.regelset li{margin-bottom:9px; font-size:15px;}
ul.regelset li:last-child{margin-bottom:0;}

@media print{ .balk,.timerbalk,.chips,.zoek{display:none;} body{background:#fff;} }
"""

FONTS = ("<link rel='preconnect' href='https://fonts.googleapis.com'>"
         "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>"
         "<link href='https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700"
         "&family=Inter:wght@400;600&family=Caveat:wght@500&display=swap' rel='stylesheet'>")


def pagina(titel, inhoud, extra_js=""):
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#AD2C2C">
<title>{html.escape(titel)}</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
{inhoud}
<script>{extra_js}</script>
</body>
</html>
"""


# ----------------------------------------------------------------- data ----

def slugify(tekst):
    """Naam naar een veilige bestandsnaam: kleine letters, streepjes, geen accenten."""
    kaal = unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", kaal.lower()).strip("-")


def stappen_van(it):
    """Eén bakstap of meerdere, de generator behandelt ze allemaal als een lijst."""
    if it.get("stappen"):
        return it["stappen"]
    stap = {"graden": it["graden"], "minuten": it["minuten"]}
    # Alleen meenemen als de bron er iets over zegt, anders zwijgt de site erover.
    if "schudden" in it:
        stap["schudden"] = it["schudden"]
    if it.get("stand"):
        stap["stand"] = it["stand"]
    if it.get("functie"):
        stap["functie"] = it["functie"]
    return [stap]


def tijd_tekst(laag, hoog):
    return f"{laag} min" if laag == hoog else f"{laag} tot {hoog} min"


def laad():
    groepen = []
    for f in sorted(BRON.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            groepen.append(json.load(fh))
    groepen.sort(key=lambda g: (g.get("volgorde", 99), g["categorie"]))
    return groepen


# ------------------------------------------------------------- overzicht ----

def bouw_item(it):
    naam = it["naam"]
    stappen = stappen_van(it)
    meerdere = len(stappen) > 1

    totaal_laag = sum(s["minuten"][0] for s in stappen)
    totaal_hoog = sum(s["minuten"][-1] for s in stappen)

    if meerdere:
        samenvatting = f"{len(stappen)} stappen &middot; {tijd_tekst(totaal_laag, totaal_hoog)}"
    else:
        samenvatting = (f"{stappen[0]['graden']}&deg; &middot; "
                        f"{tijd_tekst(totaal_laag, totaal_hoog)}")

    zoek = " ".join([naam] + it.get("trefwoorden", [])).lower()

    regels_stappen = []
    for n, s in enumerate(stappen, 1):
        schud = s.get("schudden") or 0
        wat = s.get("wat") or (f"Stap {n}" if meerdere else "Zet op")
        nr = f'<span class="nr">{n}</span>' if meerdere else ""
        # Staat er niets over schudden in de bron, dan zwijgt de site erover.
        if "schudden" not in s:
            schudregel = ""
        elif schud:
            schudregel = f'<span class="schud">Schudden om de {schud} min</span>'
        else:
            schudregel = '<span class="schud">Keren halverwege</span>'
        stand = s.get("stand", "")
        functie = s.get("functie", "")
        standbadge = (f'<span class="stand">{html.escape(stand)}</span>'
                      if stand else "")
        if functie:
            standbadge += f'<span class="functie">{html.escape(functie)} aan</span>'
        regels_stappen.append(
            f'<li class="stap" data-graden="{s["graden"]}" data-lo="{s["minuten"][0]}"'
            f' data-hi="{s["minuten"][-1]}" data-schud="{schud}"'
            f' data-wat="{html.escape(wat)}" data-stand="{html.escape(stand)}"'
            f' data-functie="{html.escape(functie)}">'
            f'{nr}<div class="lijf">'
            f'<span class="wat">{html.escape(wat)}</span>'
            f'<span class="zet">{s["graden"]} &deg;C &middot; '
            f'<b class="stijd">{tijd_tekst(s["minuten"][0], s["minuten"][-1])}</b>'
            f'{standbadge}</span>'
            f'{schudregel}</div></li>')

    feiten = []
    if "voorverwarmen" in it:
        feiten.append("<div><span>Voorverwarmen</span><b>{}</b></div>".format(
            "Ja, 3 min" if it["voorverwarmen"] else "Niet nodig"))
    if meerdere:
        feiten.append('<div><span>Samen</span><b class="ttot">'
                      f'{tijd_tekst(totaal_laag, totaal_hoog)}</b></div>')
    if it.get("kern"):
        feiten.append('<div class="kern"><span>Kerntemperatuur</span>'
                      f'<b>{it["kern"]} &deg;C</b></div>')

    regels = []
    if it.get("portie"):
        regels.append(f'<p><span>In de mand</span>{html.escape(it["portie"])}</p>')
    if it.get("klaar"):
        regels.append(f'<p><span>Klaar als</span>{html.escape(it["klaar"])}</p>')

    tip = ""
    if it.get("tip"):
        tip = ('<div class="ptip"><span class="pen">&#9998;</span>'
               f'<p>{html.escape(it["tip"])}</p></div>')

    foto = ""
    if it.get("foto"):
        foto = (f'<img class="foto" src="fotos/{html.escape(it["foto"])}"'
                f' alt="" loading="lazy">')

    ster = ' <i>&#9733;</i>' if it.get("getest") else ""
    getestregel = ('<p class="getest">&#9733; Bij ons uitgetest, deze tijd klopt.</p>'
                   if it.get("getest") else "")
    knoptekst = ("Timer starten" if meerdere else f"Timer op {totaal_laag} min")

    return f"""
      <div class="item" data-zoek="{html.escape(zoek)}"
           data-cat="{html.escape(it['_cat'])}" data-naam="{html.escape(naam)}"
           data-fav="{'1' if it.get('getest') else ''}" data-vol="0">
        <button class="rij" type="button">
          {foto}
          <span class="naam">{html.escape(naam)}{ster}</span>
          <span class="tijd">{samenvatting}</span>
          <span class="pijl">&#9654;</span>
        </button>
        <div class="paneel" hidden>
          <div class="lading">
            <button class="lknop aan" type="button" data-vol="0">Normale lading</button>
            <button class="lknop" type="button" data-vol="1">Mand goed vol</button>
          </div>
          <ol class="stappen">{''.join(regels_stappen)}</ol>
          {getestregel}
          <div class="feiten">{''.join(feiten)}</div>
          <div class="regels">{''.join(regels)}</div>
          {tip}
          <p class="volnoot" hidden>Vuistregel: een volle mand vraagt ongeveer een
            vijfde meer tijd. Schud vaker en kijk zeker op het einde.</p>
          <div class="paneelknoppen">
            <button class="timerknop" type="button">{knoptekst}</button>
            <button class="pasaan" type="button">Aanpassen</button>
          </div>
          <div class="eigenrij"></div>
        </div>
      </div>"""


def bouw_index(groepen):
    secties = []
    aantal = 0
    for g in groepen:
        rijen = []
        for it in g["items"]:
            it["_cat"] = g["categorie"]
            rijen.append(bouw_item(it))
            aantal += 1
        intro = (f'<p class="groepintro">{html.escape(g["intro"])}</p>'
                 if g.get("intro") else "")
        secties.append(f"""
    <section class="groep" data-cat="{html.escape(g['categorie'])}">
      <h2 class="groepkop">{html.escape(g['categorie'])}</h2>
      {intro}
      {''.join(rijen)}
    </section>""")

    chips = "".join(f'<button class="chip" data-cat="{html.escape(g["categorie"])}">'
                    f'{html.escape(g["categorie"])}</button>' for g in groepen)
    keuzes = "".join(f'<option>{html.escape(g["categorie"])}</option>' for g in groepen)

    inhoud = f"""
<header class="kop"><div class="wrap">
  <div class="koprij">
    <h1>Crispy <span>DaLe</span></h1>
    <a class="pil" href="../index.html">Kookboek</a>
  </div>
  <p>{SITE_ONDERTITEL}</p>
</div></header>
<main class="wrap">
  <p class="noot"><b>Een ster betekent: bij ons uitgetest, die tijd klopt.</b>
  De rest zijn richttijden voor een mand van vier &agrave; vijf liter in
  &eacute;&eacute;n laag. Daar springt de timer op de korte tijd, dus kijk dan en
  geef er gerust nog wat bij. Bij vlees telt de kerntemperatuur, niet de klok.</p>
  <input class="zoek" id="zoek" type="search"
         placeholder="Zoek een product, bijvoorbeeld kip of frieten...">
  <div class="chips">
    <button class="chip aan" data-cat="">Alles</button>
    <button class="chip ster" data-cat="~fav">&#9733; Bij ons getest</button>{chips}
  </div>
  {''.join(secties)}
  <p class="leeg" id="leeg" hidden>Niets gevonden. Andere zoekterm proberen?</p>
</main>
<footer class="voet">{aantal} producten &middot; Studio HeLeen</footer>
<div class="timerbalk" id="timerbalk" hidden>
  <div class="tb-boven">
    <div class="tb-links"><b id="tb-naam"></b><span id="tb-sub"></span></div>
    <div class="tb-klok" id="tb-klok">00:00</div>
  </div>
  <div class="tb-knoppen">
    <button id="tb-plus" type="button">+1 min</button>
    <button id="tb-next" type="button" hidden>Volgende stap</button>
    <button id="tb-stop" type="button">Stop</button>
  </div>
</div>
<div class="balk">
  <button id="v-nieuw" class="nieuw" type="button">+ Toevoegen</button>
  <button id="wakker" type="button">Scherm aan</button>
  <a href="omrekenen.html">Omrekenen</a>
</div>

<div class="venster" id="venster" hidden>
  <div class="venster-kaart">
    <h3 id="v-kop">Nieuw product</h3>
    <div class="veld"><label for="v-naam">Wat bak je</label>
      <input id="v-naam" type="text" placeholder="Koteletten"></div>
    <div class="veld" id="v-catveld"><label for="v-cat">Waar hoort het thuis</label>
      <select id="v-cat">{keuzes}</select></div>

    <div class="ronde">
      <div class="velden">
        <div class="veld"><label for="v-g1">Graden</label>
          <input id="v-g1" type="number" inputmode="numeric" placeholder="180"></div>
        <div class="veld"><label for="v-m1">Minuten</label>
          <input id="v-m1" type="number" inputmode="numeric" placeholder="15"></div>
      </div>
      <div class="veld"><label for="v-s1">Stand, als je er een gebruikt</label>
        <input id="v-s1" type="text" placeholder="Max Crisp"></div>
    </div>

    <label class="vink"><input type="checkbox" id="v-tweede"> Er komt een tweede ronde</label>
    <div class="ronde" id="v-ronde2" hidden>
      <div class="velden">
        <div class="veld"><label for="v-g2">Graden</label>
          <input id="v-g2" type="number" inputmode="numeric" placeholder="240"></div>
        <div class="veld"><label for="v-m2">Minuten</label>
          <input id="v-m2" type="number" inputmode="numeric" placeholder="5"></div>
      </div>
      <div class="veld"><label for="v-s2">Stand, als je er een gebruikt</label>
        <input id="v-s2" type="text" placeholder="Max Crisp"></div>
    </div>

    <label class="vink"><input type="checkbox" id="v-ster"> Uitgetest, geef het een ster</label>
    <div class="veld"><label for="v-notitie">Notitie</label>
      <textarea id="v-notitie" rows="2" placeholder="Optioneel."></textarea></div>

    <p class="vensternoot">Wat je hier bewaart, staat op deze telefoon. Met de knop
      <b>Voorgoed op de site</b> zet je het door naar iedereen.</p>

    <div class="venster-knoppen">
      <button id="v-annuleer" type="button">Annuleren</button>
      <button id="v-bewaar" class="hoofd" type="button">Bewaren</button>
    </div>
  </div>
</div>
"""
    bron = {}
    for g in groepen:
        for it in g["items"]:
            gegevens = {k: v for k, v in it.items() if not k.startswith("_")}
            gegevens["categorie"] = g["categorie"]
            bron[it["naam"]] = gegevens
    voorop = (f"const REPO={json.dumps(REPO)};\n"
              f"const BRON={json.dumps(bron, ensure_ascii=False)};\n")
    return pagina(SITE_TITEL, inhoud, voorop + INDEX_JS)


INDEX_JS = r"""
/* ------------------------------------------------- eigen aanpassingen ---- */
/* Alles wat je hier zelf toevoegt of bijstelt, staat in de browser van dit
   toestel. Dat is meteen bruikbaar, maar het is niet hetzelfde als de site.
   Met de knop "voorgoed op de site" gaat het naar GitHub en dan staat het
   voor iedereen vast. */
const SLEUTEL = 'crispy-dale-eigen-v1';
let eigen = { items: [], wijzig: {} };

function laadOpslag(){
  try{
    const rauw = localStorage.getItem(SLEUTEL);
    if(rauw){
      const d = JSON.parse(rauw);
      eigen = { items: d.items || [], wijzig: d.wijzig || {} };
    }
  }catch(e){}
}
function bewaarOpslag(){
  try{ localStorage.setItem(SLEUTEL, JSON.stringify(eigen)); }
  catch(e){ alert('Deze telefoon wil niets bewaren. Staat privénavigatie aan?'); }
}
laadOpslag();

/* ---------------------------------------------------------- zoeken ---- */
const zoek=document.getElementById('zoek');
let items=[...document.querySelectorAll('.item')];
const groepen=[...document.querySelectorAll('.groep')];
let cat='';
function filter(){
  const t=zoek.value.toLowerCase().trim(); let n=0;
  items.forEach(i=>{
    const past=(cat==='~fav')?(i.dataset.fav==='1'):(!cat||i.dataset.cat===cat);
    const ok=(!t||i.dataset.zoek.includes(t))&&past;
    i.hidden=!ok; if(ok)n++;
  });
  groepen.forEach(g=>{
    g.hidden=![...g.querySelectorAll('.item')].some(i=>!i.hidden);
  });
  document.getElementById('leeg').hidden=(n>0);
}
zoek.addEventListener('input',filter);
document.querySelectorAll('.chip').forEach(c=>c.addEventListener('click',()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('aan'));
  c.classList.add('aan'); cat=c.dataset.cat; filter();
  window.scrollTo({top:0,behavior:'smooth'});
}));

/* -------------------------------------------------------- opbouwen ---- */
function volTijd(m){return Math.max(m+3,Math.round(m*1.2));}
function volSchud(s){return s?Math.max(3,s-2):0;}
function tijdTekst(l,h){return (l===h)?(l+' min'):(l+' tot '+h+' min');}
function veilig(t){
  return String(t==null?'':t).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function stappenVan(g){
  if(g.stappen&&g.stappen.length)return g.stappen;
  const s={graden:g.graden,minuten:g.minuten};
  if('schudden' in g)s.schudden=g.schudden;
  if(g.stand)s.stand=g.stand;
  if(g.functie)s.functie=g.functie;
  return [s];
}

/* Dezelfde opbouw als in build_airfryer.py, maar dan in de browser. Verander
   je daar de vorm van een rij, verander hem hier dan mee. */
function maakItemHtml(g){
  const stappen=stappenVan(g), meer=stappen.length>1;
  let laag=0, hoog=0;
  stappen.forEach(s=>{laag+=s.minuten[0]; hoog+=s.minuten[s.minuten.length-1];});
  const samen=meer?(stappen.length+' stappen · '+tijdTekst(laag,hoog))
                  :(stappen[0].graden+'° · '+tijdTekst(laag,hoog));

  const regels=stappen.map((s,n)=>{
    const wat=s.wat||(meer?('Stap '+(n+1)):'Zet op');
    const nr=meer?('<span class="nr">'+(n+1)+'</span>'):'';
    let badge='';
    if(s.stand)badge+='<span class="stand">'+veilig(s.stand)+'</span>';
    if(s.functie)badge+='<span class="functie">'+veilig(s.functie)+' aan</span>';
    let schud='';
    if('schudden' in s){
      schud='<span class="schud">'+(s.schudden?('Schudden om de '+s.schudden+' min')
                                              :'Keren halverwege')+'</span>';
    }
    return '<li class="stap" data-graden="'+s.graden+'" data-lo="'+s.minuten[0]+
      '" data-hi="'+s.minuten[s.minuten.length-1]+'" data-schud="'+(s.schudden||0)+
      '" data-wat="'+veilig(wat)+'" data-stand="'+veilig(s.stand||'')+
      '" data-functie="'+veilig(s.functie||'')+'">'+nr+'<div class="lijf">'+
      '<span class="wat">'+veilig(wat)+'</span><span class="zet">'+s.graden+
      ' °C · <b class="stijd">'+tijdTekst(s.minuten[0],s.minuten[s.minuten.length-1])+
      '</b>'+badge+'</span>'+schud+'</div></li>';
  }).join('');

  let feiten='';
  if('voorverwarmen' in g){
    feiten+='<div><span>Voorverwarmen</span><b>'+
      (g.voorverwarmen?'Ja, 3 min':'Niet nodig')+'</b></div>';
  }
  if(meer)feiten+='<div><span>Samen</span><b class="ttot">'+tijdTekst(laag,hoog)+'</b></div>';
  if(g.kern)feiten+='<div class="kern"><span>Kerntemperatuur</span><b>'+g.kern+' °C</b></div>';

  let tekst='';
  if(g.portie)tekst+='<p><span>In de mand</span>'+veilig(g.portie)+'</p>';
  if(g.klaar)tekst+='<p><span>Klaar als</span>'+veilig(g.klaar)+'</p>';

  const tip=g.tip?('<div class="ptip"><span class="pen">&#9998;</span><p>'+
    veilig(g.tip)+'</p></div>'):'';
  const foto=g.foto?('<img class="foto" src="fotos/'+veilig(g.foto)+'" alt="" loading="lazy">'):'';
  const ster=g.getest?' <i>&#9733;</i>':'';
  const merk=g._eigen?'<span class="hier">deze telefoon</span>'
            :(g._gewijzigd?'<span class="hier">aangepast</span>':'');
  const getestregel=g.getest?
    '<p class="getest">&#9733; Bij ons uitgetest, deze tijd klopt.</p>':'';
  const zoekwoorden=[g.naam].concat(g.trefwoorden||[]).join(' ').toLowerCase();

  return '<div class="item'+((g._eigen||g._gewijzigd)?' eigen':'')+
    '" data-zoek="'+veilig(zoekwoorden)+'" data-cat="'+veilig(g.categorie)+
    '" data-naam="'+veilig(g.naam)+'" data-fav="'+(g.getest?'1':'')+'" data-vol="0">'+
    '<button class="rij" type="button">'+foto+
    '<span class="naam">'+veilig(g.naam)+ster+merk+'</span>'+
    '<span class="tijd">'+samen+'</span><span class="pijl">&#9654;</span></button>'+
    '<div class="paneel" hidden>'+
    '<div class="lading"><button class="lknop aan" type="button" data-vol="0">Normale lading</button>'+
    '<button class="lknop" type="button" data-vol="1">Mand goed vol</button></div>'+
    '<ol class="stappen">'+regels+'</ol>'+getestregel+
    '<div class="feiten">'+feiten+'</div><div class="regels">'+tekst+'</div>'+tip+
    '<p class="volnoot" hidden>Vuistregel: een volle mand vraagt ongeveer een vijfde ' +
    'meer tijd. Schud vaker en kijk zeker op het einde.</p>'+
    '<div class="paneelknoppen"><button class="timerknop" type="button">Timer</button>'+
    '<button class="pasaan" type="button">Aanpassen</button></div>'+
    '<div class="eigenrij"></div></div></div>';
}

function maakItemEl(g){
  const houder=document.createElement('div');
  houder.innerHTML=maakItemHtml(g);
  return houder.firstChild;
}

/* ------------------------------------------------- rij aan de praat ---- */
function koppel(i){
  const rij=i.querySelector('.rij'), paneel=i.querySelector('.paneel');
  const stappen=[...i.querySelectorAll('.stap')];
  const knop=i.querySelector('.timerknop'), noot=i.querySelector('.volnoot');
  const ttot=i.querySelector('.ttot');

  function toon(vol){
    i.dataset.vol=vol?'1':'0';
    let laag=0, hoog=0;
    stappen.forEach(s=>{
      const lo=vol?volTijd(+s.dataset.lo):+s.dataset.lo;
      const hi=vol?volTijd(+s.dataset.hi):+s.dataset.hi;
      laag+=lo; hoog+=hi;
      s.querySelector('.stijd').textContent=tijdTekst(lo,hi);
      const schud=+s.dataset.schud, regel=s.querySelector('.schud');
      if(schud&&regel){regel.textContent=
        'Schudden om de '+(vol?volSchud(schud):schud)+' min';}
    });
    if(ttot){ttot.textContent=tijdTekst(laag,hoog);}
    knop.textContent=(stappen.length>1)?'Timer starten':('Timer op '+laag+' min');
    noot.hidden=!vol;
  }
  toon(false);

  i.querySelectorAll('.lknop').forEach(b=>b.addEventListener('click',()=>{
    i.querySelectorAll('.lknop').forEach(x=>x.classList.remove('aan'));
    b.classList.add('aan'); toon(b.dataset.vol==='1');
  }));

  rij.addEventListener('click',()=>{
    const open=!paneel.hidden;
    items.forEach(o=>{
      o.querySelector('.paneel').hidden=true;
      o.querySelector('.rij').classList.remove('open');
    });
    if(!open){paneel.hidden=false; rij.classList.add('open');}
  });

  knop.addEventListener('click',()=>{
    const vol=i.dataset.vol==='1';
    const plan=stappen.map((s,n)=>({
      wat:s.dataset.wat||('Stap '+(n+1)),
      graden:+s.dataset.graden,
      stand:s.dataset.stand||'',
      functie:s.dataset.functie||'',
      min: vol?volTijd(+s.dataset.lo):+s.dataset.lo,
      schud: vol?volSchud(+s.dataset.schud):(+s.dataset.schud)
    }));
    startTimer(i.dataset.naam,plan,0);
  });

  i.querySelector('.pasaan').addEventListener('click',()=>opendVenster(i.dataset.naam));
  vulEigenrij(i);
}

/* De regel onderaan het paneel bij alles wat van deze telefoon komt. */
function vulEigenrij(i){
  const naam=i.dataset.naam, rij=i.querySelector('.eigenrij');
  const zelf=eigen.items.find(x=>x.naam===naam);
  const aangepast=eigen.wijzig[naam];
  if(!zelf&&!aangepast){rij.innerHTML=''; return;}
  rij.innerHTML=
    '<p class="eigennoot">'+(zelf
      ? 'Dit product staat alleen op deze telefoon.'
      : 'Je hebt deze tijd zelf bijgesteld, alleen op deze telefoon.')+'</p>'+
    '<div class="paneelknoppen">'+
    '<a class="voorgoed" target="_blank" rel="noopener">Voorgoed op de site</a>'+
    '<button class="terugzet" type="button">'+(zelf?'Verwijderen':'Zet terug')+'</button>'+
    '</div>';
  rij.querySelector('.voorgoed').href=githubLink(zelf||Object.assign(
    {}, BRON[naam]||{}, aangepast, {naam:naam}));
  rij.querySelector('.terugzet').addEventListener('click',()=>{
    if(zelf){eigen.items=eigen.items.filter(x=>x.naam!==naam);}
    else{delete eigen.wijzig[naam];}
    bewaarOpslag(); herteken(naam);
  });
}

/* ----------------------------------------------------- herbouwen ---- */
function gegevensVan(naam){
  const zelf=eigen.items.find(x=>x.naam===naam);
  if(zelf)return Object.assign({}, zelf, {_eigen:true});
  const basis=BRON[naam];
  if(!basis)return null;
  const w=eigen.wijzig[naam];
  if(!w)return Object.assign({}, basis);
  const g=Object.assign({}, basis, {_gewijzigd:true});
  g.stappen=w.stappen; delete g.graden; delete g.minuten;
  delete g.schudden; delete g.stand; delete g.functie;
  g.getest=w.getest;
  if(w.notitie)g.tip=w.notitie;
  return g;
}

function herteken(naam){
  const oud=document.querySelector('.item[data-naam="'+naam.replace(/"/g,'\\"')+'"]');
  const g=gegevensVan(naam);
  if(!oud)return;
  if(!g){ // eigen product weggehaald
    const sectie=oud.closest('.groep');
    items=items.filter(x=>x!==oud); oud.remove();
    if(sectie)sectie.hidden=![...sectie.querySelectorAll('.item')].some(i=>!i.hidden);
    filter(); return;
  }
  const nieuw=maakItemEl(g);
  oud.replaceWith(nieuw);
  items[items.indexOf(oud)]=nieuw;
  koppel(nieuw);
  filter();
}

/* Eigen producten in hun categorie zetten, bij het laden van de pagina. */
function plaatsEigen(){
  eigen.items.forEach(g=>{
    if(document.querySelector('.item[data-naam="'+g.naam.replace(/"/g,'\\"')+'"]'))return;
    const sectie=document.querySelector('.groep[data-cat="'+g.categorie.replace(/"/g,'\\"')+'"]');
    if(!sectie)return;
    const el=maakItemEl(Object.assign({}, g, {_eigen:true}));
    sectie.appendChild(el); items.push(el); koppel(el);
  });
  Object.keys(eigen.wijzig).forEach(naam=>{
    if(BRON[naam])herteken(naam);
  });
}

/* ------------------------------------------------------- het venster ---- */
const venster=document.getElementById('venster');
let bewerkt=null;

function ronde(n){
  return {
    graden: +document.getElementById('v-g'+n).value||0,
    minuten: +document.getElementById('v-m'+n).value||0,
    stand: document.getElementById('v-s'+n).value.trim()
  };
}
function vulRonde(n,s){
  document.getElementById('v-g'+n).value=s?s.graden:'';
  document.getElementById('v-m'+n).value=s?s.minuten[0]:'';
  document.getElementById('v-s'+n).value=(s&&s.stand)?s.stand:'';
}

function opendVenster(naam){
  bewerkt=naam||null;
  const g=naam?gegevensVan(naam):null;
  document.getElementById('v-kop').textContent=g?('Aanpassen: '+g.naam):'Nieuw product';
  document.getElementById('v-naam').value=g?g.naam:'';
  document.getElementById('v-naam').disabled=!!g;
  document.getElementById('v-catveld').hidden=!!g;
  const stappen=g?stappenVan(g):[];
  vulRonde(1,stappen[0]);
  const tweede=stappen.length>1;
  document.getElementById('v-tweede').checked=tweede;
  document.getElementById('v-ronde2').hidden=!tweede;
  vulRonde(2,tweede?stappen[1]:null);
  document.getElementById('v-ster').checked=!!(g&&g.getest);
  document.getElementById('v-notitie').value=(g&&g.tip)?g.tip:'';
  venster.hidden=false;
  document.body.style.overflow='hidden';
}
function sluitVenster(){
  venster.hidden=true; document.body.style.overflow='';
}

document.getElementById('v-nieuw').addEventListener('click',()=>opendVenster(null));
document.getElementById('v-tweede').addEventListener('change',e=>{
  document.getElementById('v-ronde2').hidden=!e.target.checked;
});
document.getElementById('v-annuleer').addEventListener('click',sluitVenster);
venster.addEventListener('click',e=>{if(e.target===venster)sluitVenster();});

document.getElementById('v-bewaar').addEventListener('click',()=>{
  const naam=bewerkt||document.getElementById('v-naam').value.trim();
  if(!naam){alert('Geef eerst een naam.');return;}
  const r1=ronde(1);
  if(!r1.graden||!r1.minuten){alert('Vul graden en minuten in.');return;}
  const stappen=[{wat:'Zet op',graden:r1.graden,minuten:[r1.minuten,r1.minuten]}];
  if(r1.stand)stappen[0].stand=r1.stand;
  if(document.getElementById('v-tweede').checked){
    const r2=ronde(2);
    if(!r2.graden||!r2.minuten){alert('Vul de tweede ronde in of vink hem uit.');return;}
    stappen[0].wat='Eerste ronde';
    const s2={wat:'Tweede ronde',graden:r2.graden,minuten:[r2.minuten,r2.minuten]};
    if(r2.stand)s2.stand=r2.stand;
    stappen.push(s2);
  }
  const getest=document.getElementById('v-ster').checked;
  const notitie=document.getElementById('v-notitie').value.trim();

  if(bewerkt&&BRON[bewerkt]){
    eigen.wijzig[bewerkt]={stappen:stappen,getest:getest,notitie:notitie};
  }else{
    const bestaand=eigen.items.find(x=>x.naam===naam);
    const cat=bestaand?bestaand.categorie:document.getElementById('v-cat').value;
    const nieuw={naam:naam,categorie:cat,stappen:stappen,getest:getest,
                 tip:notitie,trefwoorden:[]};
    if(bestaand)Object.assign(bestaand,nieuw);
    else eigen.items.push(nieuw);
  }
  bewaarOpslag();
  sluitVenster();
  if(document.querySelector('.item[data-naam="'+naam.replace(/"/g,'\\"')+'"]')){
    herteken(naam);
  }else{
    plaatsEigen(); filter();
  }
  const el=document.querySelector('.item[data-naam="'+naam.replace(/"/g,'\\"')+'"]');
  if(el)el.scrollIntoView({block:'center',behavior:'smooth'});
});

/* Het formulier op GitHub alvast ingevuld openen. */
function githubLink(g){
  const stappen=stappenVan(g);
  const tijden=stappen.map(s=>s.minuten[0]+' min op '+s.graden+
    (s.stand?(' '+s.stand):'')).join(', dan ');
  const p=new URLSearchParams({
    template:'airfryertijd.yml',
    title:'Airfryertijd: '+g.naam,
    naam:g.naam,
    tijden:tijden,
    ster:g.getest?'Zet er een ster bij, dit is uitgetest'
                 :'Laat de ster zoals hij nu staat',
    categorie:g.categorie||'Kies zelf maar',
    extra:(g.tip||g.notitie||'')
  });
  return 'https://github.com/'+REPO+'/issues/new?'+p.toString();
}

items.forEach(koppel);
plaatsEigen();
filter();

/* ----------------------------------------------------------- timer ---- */
const balk=document.getElementById('timerbalk');
const klok=document.getElementById('tb-klok');
const sub=document.getElementById('tb-sub');
const volgendeKnop=document.getElementById('tb-next');
let T=null, ac=null;

function fmt(ms){
  const s=Math.max(0,Math.round(ms/1000));
  return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');
}

function piep(keer){
  try{
    ac=ac||new (window.AudioContext||window.webkitAudioContext)();
    if(ac.state==='suspended'){ac.resume();}
    for(let k=0;k<keer;k++){
      const o=ac.createOscillator(), g=ac.createGain();
      o.connect(g); g.connect(ac.destination);
      o.frequency.value=880; const t0=ac.currentTime+k*0.3;
      g.gain.setValueAtTime(0.0001,t0);
      g.gain.exponentialRampToValueAtTime(0.35,t0+0.02);
      g.gain.exponentialRampToValueAtTime(0.0001,t0+0.24);
      o.start(t0); o.stop(t0+0.26);
    }
  }catch(e){}
  if(navigator.vibrate){navigator.vibrate(keer>1?[200,120,200]:[300]);}
}

function startTimer(naam,plan,index){
  const stap=plan[index], nu=Date.now();
  const momenten=[];
  if(stap.schud>0){
    for(let m=stap.schud;m*60000<stap.min*60000-30000;m+=stap.schud){
      momenten.push({t:nu+m*60000,gedaan:false,tot:0});
    }
  }
  T={naam:naam,plan:plan,index:index,eind:nu+stap.min*60000,
     momenten:momenten,af:false};
  document.getElementById('tb-naam').textContent=naam;
  balk.classList.remove('af','schud');
  volgendeKnop.hidden=true;
  balk.hidden=false;
  document.body.classList.add('timert');
  try{ac=ac||new (window.AudioContext||window.webkitAudioContext)();
      if(ac.state==='suspended'){ac.resume();}}catch(e){}
  wakkerAan();
  tik();
}

function stopTimer(){
  T=null; balk.hidden=true; balk.classList.remove('af','schud');
  volgendeKnop.hidden=true;
  document.body.classList.remove('timert');
}

function tik(){
  if(!T)return;
  const nu=Date.now(), rest=T.eind-nu;
  const stap=T.plan[T.index], laatste=(T.index===T.plan.length-1);
  const nummer=(T.plan.length>1)?('stap '+(T.index+1)+' van '+T.plan.length+' · '):'';
  klok.textContent=fmt(rest);

  let schudden=false;
  T.momenten.forEach(m=>{
    if(!m.gedaan&&nu>=m.t){m.gedaan=true; m.tot=nu+25000; piep(2);}
    if(m.tot&&nu<m.tot){schudden=true;}
  });

  if(rest<=0&&!T.af){
    T.af=true; piep(3); balk.classList.add('af');
    if(!laatste){volgendeKnop.hidden=false;
      volgendeKnop.textContent='Start stap '+(T.index+2);}
  }

  if(T.af){
    balk.classList.remove('schud');
    if(laatste){sub.textContent='Kijk of het klaar is';}
    else{
      const volgende=T.plan[T.index+1];
      sub.textContent='Zet nu op '+volgende.graden+' °C'
        +(volgende.stand?(', '+volgende.stand):'')
        +(volgende.functie?(', '+volgende.functie+' aan'):'');
    }
  }else if(schudden){
    balk.classList.add('schud');
    sub.textContent='Schudden!';
  }else{
    balk.classList.remove('schud');
    const volgend=T.momenten.find(m=>!m.gedaan);
    const zet=stap.graden+' °C'+(stap.stand?(' · '+stap.stand):'')
      +(stap.functie?(' · '+stap.functie):'');
    sub.textContent=nummer+(volgend?('schudden over '+fmt(volgend.t-nu)):zet);
  }
}
setInterval(tik,250);

document.getElementById('tb-stop').addEventListener('click',stopTimer);
volgendeKnop.addEventListener('click',()=>{
  if(T&&T.index+1<T.plan.length){startTimer(T.naam,T.plan,T.index+1);}
});
document.getElementById('tb-plus').addEventListener('click',()=>{
  if(!T)return;
  if(T.af){T.af=false; T.eind=Date.now()+60000;
    balk.classList.remove('af'); volgendeKnop.hidden=true;}
  else{T.eind+=60000;}
  tik();
});

/* ------------------------------------------------- scherm aan houden ---- */
let lock=null;
const wknop=document.getElementById('wakker');
async function wakkerAan(){
  try{
    if(!lock&&navigator.wakeLock){
      lock=await navigator.wakeLock.request('screen');
      wknop.classList.add('aan'); wknop.textContent='Blijft aan';
      lock.addEventListener('release',()=>{
        lock=null; wknop.classList.remove('aan'); wknop.textContent='Scherm aan';
      });
    }
  }catch(e){}
}
wknop.addEventListener('click',async()=>{
  try{
    if(lock){await lock.release(); lock=null;
      wknop.classList.remove('aan'); wknop.textContent='Scherm aan';}
    else{await wakkerAan();
      if(!lock){wknop.textContent='Lukt niet';}}
  }catch(e){wknop.textContent='Lukt niet';}
});
document.addEventListener('visibilitychange',()=>{
  if(document.visibilityState==='visible'&&T&&!lock){wakkerAan();}
});
"""


# ------------------------------------------------------------ omrekenen ----

KERNTEMPERATUREN = [
    ("Kip en gevogelte, altijd door en door gaar", "75 &deg;C"),
    ("Gehakt, worst en burgers", "72 &deg;C"),
    ("Varkensvlees, nog net ros&eacute;", "63 &deg;C"),
    ("Rundvlees ros&eacute;", "55 &deg;C"),
    ("Rundvlees doorbakken", "68 &deg;C"),
    ("Vis", "55 tot 60 &deg;C"),
    ("Restjes opwarmen", "75 &deg;C"),
]

VUISTREGELS = [
    "Verwarm drie minuten voor. Koud beginnen kost je de krokante buitenkant, "
    "want dan verdampt het vocht trager dan het gaart.",
    "E&eacute;n laag in de mand. Stapel je, dan stoom je, en stomen is precies "
    "het tegenovergestelde van wat je wil.",
    "Een halve lepel olie is genoeg voor een hele mand groenten. Meng ze door "
    "in een kom, niet in de mand, anders zit alle olie op drie stukken.",
    "Nat beslag loopt door de mand. Paneermeel werkt, frituurdeeg niet.",
    "Bakpapier alleen onder iets zwaars. Los papier vliegt tegen het element "
    "en dat is de kortste weg naar een brandlucht.",
    "Giet het vet uit de lade voor je iets nieuws bakt. Achtergebleven vet van "
    "spek of worst begint te roken bij de volgende ronde.",
]


def bouw_omrekenen():
    kern = "".join(f"<tr><td>{n}</td><td>{t}</td></tr>" for n, t in KERNTEMPERATUREN)
    regels = "".join(f"<li>{r}</li>" for r in VUISTREGELS)

    inhoud = f"""
<header class="kop"><div class="wrap">
  <div class="koprij">
    <h1>Oven <span>omrekenen</span></h1>
    <a class="pil" href="index.html">Tijden</a>
  </div>
  <p>{SITE_ONDERTITEL}</p>
</div></header>
<main class="wrap">
  <div class="kaart" style="margin-top:22px">
    <h2>Van oven naar airfryer</h2>
    <p class="uit">Een airfryer is een kleine oven met een harde ventilator.
      Twintig graden lager en ongeveer een vijfde korter brengt je heel dicht
      bij het recept dat voor de oven geschreven is.</p>
    <div class="richting">
      <button class="aan" type="button" data-r="naar">Oven &rarr; airfryer</button>
      <button type="button" data-r="van">Airfryer &rarr; oven</button>
    </div>
    <div class="velden">
      <div class="veld"><label for="gr">Temperatuur</label>
        <input id="gr" type="number" inputmode="numeric" value="200"></div>
      <div class="veld"><label for="mn">Minuten</label>
        <input id="mn" type="number" inputmode="numeric" value="30"></div>
    </div>
    <div class="uitkomst"><span id="ulabel">In de airfryer</span>
      <b id="uit">180 &deg;C, 24 min</b></div>
    <p class="volnoot" style="text-align:center">Kijk vanaf driekwart van de tijd.
      Dit is een vuistregel, geen natuurwet.</p>
  </div>

  <div class="kaart">
    <h2>Wanneer is het gaar</h2>
    <p class="uit">Bij vlees is de kerntemperatuur het enige eerlijke antwoord.
      Meet in het dikste stuk, niet tegen een bot.</p>
    <table class="kern">{kern}</table>
  </div>

  <div class="kaart">
    <h2>Zes dingen die het verschil maken</h2>
    <ul class="regelset">{regels}</ul>
  </div>
</main>
<footer class="voet">Studio HeLeen</footer>
<div class="balk">
  <a href="index.html">Terug naar de tijden</a>
  <a href="../index.html">Het kookboek</a>
</div>
"""

    js = r"""
const gr=document.getElementById('gr'), mn=document.getElementById('mn');
const uit=document.getElementById('uit'), ulabel=document.getElementById('ulabel');
let richting='naar';
function reken(){
  const g=parseFloat(gr.value)||0, m=parseFloat(mn.value)||0;
  let ng,nm;
  if(richting==='naar'){ng=g-20; nm=Math.round(m*0.8); ulabel.textContent='In de airfryer';}
  else{ng=g+20; nm=Math.round(m*1.25); ulabel.textContent='In de oven';}
  ng=Math.max(0,Math.round(ng)); nm=Math.max(1,nm);
  uit.innerHTML=ng+' °C, '+nm+' min';
}
gr.addEventListener('input',reken);
mn.addEventListener('input',reken);
document.querySelectorAll('.richting button').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.richting button').forEach(x=>x.classList.remove('aan'));
  b.classList.add('aan'); richting=b.dataset.r; reken();
}));
reken();
"""
    return pagina(f"Oven omrekenen · {SITE_TITEL}", inhoud, js)


# ------------------------------------------------------------------ main ----

def bouw(uit):
    """Schrijft de airfryersite naar de map uit, meestal docs/airfryer."""
    groepen = laad()
    if not groepen:
        print("Geen producten gevonden in airfryer/")
        return 0

    uit = Path(uit)
    if uit.exists():
        shutil.rmtree(uit)
    uit.mkdir(parents=True)

    (uit / "index.html").write_text(bouw_index(groepen), encoding="utf-8")
    (uit / "omrekenen.html").write_text(bouw_omrekenen(), encoding="utf-8")

    if FOTOS.exists():
        shutil.copytree(FOTOS, uit / "fotos")

    aantal = sum(len(g["items"]) for g in groepen)
    print(f"Crispy DaLe: {aantal} producten in {len(groepen)} categorieen naar {uit}/")
    return aantal


if __name__ == "__main__":
    bouw(ROOT / "docs" / "airfryer")
