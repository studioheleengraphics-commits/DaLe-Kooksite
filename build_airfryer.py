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

.feiten{display:grid; grid-template-columns:repeat(2,1fr); gap:14px 18px;
  padding:14px 0 16px; border-bottom:1px solid var(--lijn);}
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
.timerknop{width:100%; margin-top:16px; padding:13px; border-radius:10px;
  border:1px solid var(--rood); background:var(--wit); color:var(--rood);
  font-family:'DM Sans',sans-serif; font-weight:500; font-size:15px; cursor:pointer;}
.timerknop:active{background:var(--rood); color:var(--wit);}

.leeg{color:var(--inkt-zacht); text-align:center; padding:30px 0;}
.voet{text-align:center; color:var(--inkt-licht); font-size:12px;
  letter-spacing:.6px; padding:6px 0 30px;}

/* vaste balk onderaan */
.balk{position:fixed; left:0; right:0; bottom:0; background:var(--wit);
  border-top:1px solid var(--lijn); display:flex; gap:10px; padding:10px 16px;
  justify-content:center; z-index:9;}
.balk button, .balk a{flex:1; max-width:220px; text-align:center; padding:11px 8px;
  border-radius:10px; border:1px solid var(--lijn); background:var(--wit);
  color:var(--inkt); font-size:14px; font-family:inherit; cursor:pointer;}
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
    return [{"graden": it["graden"], "minuten": it["minuten"],
             "schudden": it.get("schudden") or 0}]


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
        schudregel = (f'<span class="schud">Schudden om de {schud} min</span>'
                      if schud else '<span class="schud">Keren halverwege</span>')
        regels_stappen.append(
            f'<li class="stap" data-graden="{s["graden"]}" data-lo="{s["minuten"][0]}"'
            f' data-hi="{s["minuten"][-1]}" data-schud="{schud}"'
            f' data-wat="{html.escape(wat)}">{nr}<div class="lijf">'
            f'<span class="wat">{html.escape(wat)}</span>'
            f'<span class="zet">{s["graden"]} &deg;C &middot; '
            f'<b class="stijd">{tijd_tekst(s["minuten"][0], s["minuten"][-1])}</b></span>'
            f'{schudregel}</div></li>')

    feiten = ["<div><span>Voorverwarmen</span><b>{}</b></div>".format(
        "Ja, 3 min" if it.get("voorverwarmen", True) else "Niet nodig")]
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

    ster = ' <i>&#9733;</i>' if it.get("favoriet") else ""
    knoptekst = ("Timer starten" if meerdere else f"Timer op {totaal_laag} min")

    return f"""
      <div class="item" data-zoek="{html.escape(zoek)}"
           data-cat="{html.escape(it['_cat'])}" data-naam="{html.escape(naam)}"
           data-fav="{'1' if it.get('favoriet') else ''}" data-vol="0">
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
          <div class="feiten">{''.join(feiten)}</div>
          <div class="regels">{''.join(regels)}</div>
          {tip}
          <p class="volnoot" hidden>Vuistregel: een volle mand vraagt ongeveer een
            vijfde meer tijd. Schud vaker en kijk zeker op het einde.</p>
          <button class="timerknop" type="button">{knoptekst}</button>
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

    inhoud = f"""
<header class="kop"><div class="wrap">
  <div class="koprij">
    <h1>Crispy <span>DaLe</span></h1>
    <a class="pil" href="../index.html">Kookboek</a>
  </div>
  <p>{SITE_ONDERTITEL}</p>
</div></header>
<main class="wrap">
  <p class="noot"><b>Richttijden voor een mand van vier &agrave; vijf liter, in
  &eacute;&eacute;n laag.</b> Elk toestel bakt anders, dus de timer springt op de
  korte tijd. Kijk dan, en geef er gerust nog wat bij. Bij vlees telt de
  kerntemperatuur, niet de klok.</p>
  <input class="zoek" id="zoek" type="search"
         placeholder="Zoek een product, bijvoorbeeld kip of frieten...">
  <div class="chips">
    <button class="chip aan" data-cat="">Alles</button>
    <button class="chip ster" data-cat="~fav">&#9733; Favorieten</button>{chips}
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
  <button id="wakker" type="button">Scherm aan houden</button>
  <a href="omrekenen.html">Oven omrekenen</a>
</div>
"""
    return pagina(SITE_TITEL, inhoud, INDEX_JS)


INDEX_JS = r"""
/* ---------------------------------------------------------- zoeken ---- */
const zoek=document.getElementById('zoek');
const items=[...document.querySelectorAll('.item')];
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

/* -------------------------------------------- uitklappen en lading ---- */
function volTijd(m){return Math.max(m+3,Math.round(m*1.2));}
function volSchud(s){return s?Math.max(3,s-2):0;}
function tijdTekst(l,h){return (l===h)?(l+' min'):(l+' tot '+h+' min');}

items.forEach(i=>{
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
      const schud=+s.dataset.schud;
      if(schud){s.querySelector('.schud').textContent=
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
      min: vol?volTijd(+s.dataset.lo):+s.dataset.lo,
      schud: vol?volSchud(+s.dataset.schud):(+s.dataset.schud)
    }));
    startTimer(i.dataset.naam,plan,0);
  });
});

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
    sub.textContent=laatste?'Kijk of het klaar is'
      :('Zet nu op '+T.plan[T.index+1].graden+' °C');
  }else if(schudden){
    balk.classList.add('schud');
    sub.textContent='Schudden!';
  }else{
    balk.classList.remove('schud');
    const volgend=T.momenten.find(m=>!m.gedaan);
    sub.textContent=nummer+(volgend?('schudden over '+fmt(volgend.t-nu))
                                   :(stap.graden+' °C'));
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
      wknop.classList.add('aan'); wknop.textContent='Scherm blijft aan';
      lock.addEventListener('release',()=>{
        lock=null; wknop.classList.remove('aan'); wknop.textContent='Scherm aan houden';
      });
    }
  }catch(e){}
}
wknop.addEventListener('click',async()=>{
  try{
    if(lock){await lock.release(); lock=null;
      wknop.classList.remove('aan'); wknop.textContent='Scherm aan houden';}
    else{await wakkerAan();
      if(!lock){wknop.textContent='Lukt niet op dit toestel';}}
  }catch(e){wknop.textContent='Lukt niet op dit toestel';}
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
