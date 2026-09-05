#!/usr/bin/env python3
"""
Kookboek Studio HeLeen - statische site generator.

Leest alle recepten uit recepten/*.json en schrijft een complete,
zelfstandige website naar docs/. Elke pagina is een los HTML-bestand
zonder externe afhankelijkheden, dus alles werkt ook offline.

Gebruik:  python3 build.py
"""

import json
import shutil
import html
from pathlib import Path

ROOT = Path(__file__).parent
RECEPTEN = ROOT / "recepten"
PDF_BRON = ROOT / "pdf"
UIT = ROOT / "docs"

SITE_TITEL = "Het kookboek"
SITE_ONDERTITEL = "Studio HeLeen · uit de keuken"

# ---------------------------------------------------------------- stijl ----

CSS = """
:root{
  --rood:#AD2C2C; --zeegroen:#77968E; --inkt:#1F1D1A;
  --inkt-zacht:#7B7777; --inkt-licht:#ADA7A7;
  --papier:#F0EEEB; --wit:#FFFFFF; --kaart:#FAFAFA; --lijn:#E8E8E8;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
html{-webkit-text-size-adjust:100%;}
body{
  margin:0; background:var(--papier); color:var(--inkt);
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  font-size:17px; line-height:1.6; padding-bottom:64px;
}
.wrap{max-width:760px; margin:0 auto; padding:0 20px;}
a{color:var(--rood); text-decoration:none;}

/* kop van de site */
.kop{background:var(--wit); border-bottom:1px solid var(--lijn); padding:28px 0 24px;}
.kop h1{
  font-family:'DM Sans',sans-serif; font-weight:700; font-size:30px;
  margin:0; letter-spacing:-.4px;
}
.kop h1 span{color:var(--rood);}
.kop p{margin:4px 0 0; color:var(--inkt-zacht); font-size:13px;
  letter-spacing:1.4px; text-transform:uppercase;}

/* zoeken en filters */
.zoek{width:100%; padding:13px 16px; border:1px solid var(--lijn);
  border-radius:10px; background:var(--wit); font-size:16px;
  font-family:inherit; color:var(--inkt); margin:22px 0 12px;}
.zoek:focus{outline:none; border-color:var(--zeegroen);}
.chips{display:flex; gap:8px; flex-wrap:wrap; margin-bottom:22px;}
.chip{border:1px solid var(--lijn); background:var(--wit); color:var(--inkt-zacht);
  padding:7px 14px; border-radius:999px; font-size:13px; font-family:inherit;
  cursor:pointer; letter-spacing:.3px;}
.chip.aan{background:var(--rood); border-color:var(--rood); color:var(--wit);}

/* receptkaarten */
.kaarten{display:grid; gap:14px; padding-bottom:40px;}
.kaart{display:block; background:var(--wit); border:1px solid var(--lijn);
  border-radius:12px; padding:20px 22px; color:var(--inkt);}
.kaart .kicker{font-family:'DM Sans',sans-serif; font-size:10px;
  letter-spacing:1.8px; text-transform:uppercase; color:var(--rood);}
.kaart h2{font-family:'DM Sans',sans-serif; font-size:23px; font-weight:700;
  margin:6px 0 6px; letter-spacing:-.3px;}
.kaart p{margin:0; color:var(--inkt-zacht); font-size:15px;}
.kaart .regel{margin-top:12px; font-size:12px; color:var(--inkt-licht);
  letter-spacing:.4px;}
.leeg{color:var(--inkt-zacht); text-align:center; padding:40px 0;}

/* receptpagina */
.terug{display:inline-block; margin:22px 0 6px; font-size:14px; color:var(--inkt-zacht);}
.recept{background:var(--wit); border:1px solid var(--lijn); border-radius:12px;
  padding:30px 26px 34px; margin-bottom:30px;}
.recept .kicker{font-family:'DM Sans',sans-serif; font-size:10px;
  letter-spacing:2px; text-transform:uppercase; color:var(--rood);}
.recept h1{font-family:'DM Sans',sans-serif; font-size:36px; font-weight:700;
  line-height:1.1; margin:10px 0 14px; letter-spacing:-.8px; color:var(--rood);}
.intro{color:var(--inkt-zacht); font-size:16px; margin:0 0 24px;}

.meta{display:flex; flex-wrap:wrap; gap:22px; padding:16px 0;
  border-top:1px solid var(--lijn); border-bottom:1px solid var(--lijn);}
.meta div span{display:block; font-family:'DM Sans',sans-serif; font-size:10px;
  letter-spacing:1.4px; text-transform:uppercase; color:var(--inkt-licht);}
.meta div b{font-family:'DM Sans',sans-serif; font-weight:500; font-size:15px;}

h3.blokkop{font-family:'DM Sans',sans-serif; font-size:11px; letter-spacing:2px;
  text-transform:uppercase; color:var(--rood); margin:30px 0 14px;}

/* porties */
.porties{display:flex; align-items:center; gap:14px; background:var(--papier);
  border-radius:10px; padding:12px 16px; margin-bottom:16px;}
.porties .tekst{font-size:14px; color:var(--inkt-zacht); flex:1;}
.porties button{width:36px; height:36px; border-radius:9px; border:1px solid var(--lijn);
  background:var(--wit); font-size:20px; color:var(--rood); cursor:pointer;
  line-height:1; font-family:inherit;}
.porties .aantal{font-family:'DM Sans',sans-serif; font-weight:700; font-size:19px;
  min-width:26px; text-align:center;}

/* ingredienten */
ul.ing{list-style:none; padding:0; margin:0;}
ul.ing li{padding:11px 0 11px 30px; border-bottom:1px solid var(--lijn);
  position:relative; cursor:pointer; font-size:16px;}
ul.ing li:before{content:""; position:absolute; left:0; top:15px; width:16px;
  height:16px; border:1.5px solid var(--inkt-licht); border-radius:4px;}
ul.ing li.af{color:var(--inkt-licht); text-decoration:line-through;}
ul.ing li.af:before{background:var(--zeegroen); border-color:var(--zeegroen);}
ul.ing li b{font-family:'DM Sans',sans-serif; font-weight:600;}

/* stappen */
.stap{display:flex; gap:16px; padding:16px 0; border-bottom:1px solid var(--lijn);
  cursor:pointer;}
.stap .nr{font-family:'DM Sans',sans-serif; font-weight:700; font-size:20px;
  color:var(--rood); min-width:26px;}
.stap h4{font-family:'DM Sans',sans-serif; font-size:17px; margin:0 0 4px;}
.stap p{margin:0; font-size:16px; color:var(--inkt);}
.stap.af{opacity:.4;}
.stap.af .nr{color:var(--zeegroen);}

/* tip */
.tip{background:var(--papier); border-left:3px solid var(--rood); border-radius:0 10px 10px 0;
  padding:16px 20px; margin:26px 0 0;}
.tip p{font-family:'Caveat',cursive; font-size:22px; line-height:1.35; margin:0;}
.tip .pen{color:var(--rood); font-size:15px;}

/* praktijk */
.praktijk{display:grid; gap:12px;}
.praktijk div{background:var(--kaart); border:1px solid var(--lijn);
  border-radius:10px; padding:14px 18px;}
.praktijk h4{font-family:'DM Sans',sans-serif; font-size:15px; margin:0 0 4px;
  color:var(--zeegroen);}
.praktijk p{margin:0; font-size:15px; color:var(--inkt-zacht);}

/* voet en balk */
.voet{text-align:center; color:var(--inkt-licht); font-size:12px;
  letter-spacing:.6px; padding:10px 0 30px;}
.voet .bron{margin-top:8px;}
.voet .bron a{border-bottom:1px solid rgba(173,44,44,.35);}
.balk{position:fixed; left:0; right:0; bottom:0; background:var(--wit);
  border-top:1px solid var(--lijn); display:flex; gap:10px; padding:10px 16px;
  justify-content:center; z-index:9;}
.balk button, .balk a{flex:1; max-width:220px; text-align:center; padding:11px 8px;
  border-radius:10px; border:1px solid var(--lijn); background:var(--wit);
  color:var(--inkt); font-size:14px; font-family:inherit; cursor:pointer;}
.balk button.aan{background:var(--zeegroen); border-color:var(--zeegroen); color:var(--wit);}

@media print{
  .balk,.terug,.porties button{display:none;}
  body{background:var(--wit); padding:0;}
  .recept{border:none; padding:0;}
}
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


# ------------------------------------------------------------ overzicht ----

def bouw_index(recepten):
    kaarten = []
    for r in recepten:
        zoekwoorden = " ".join([
            r["titel"], r.get("categorie", ""), " ".join(r.get("trefwoorden", [])),
            " ".join(i["naam"] for i in r["ingredienten"]),
        ]).lower()
        meta_regel = " · ".join(m["waarde"] for m in r.get("meta", [])[:2])
        kaarten.append(f"""
    <a class="kaart" href="{r['slug']}.html"
       data-zoek="{html.escape(zoekwoorden)}"
       data-cat="{html.escape(r.get('categorie',''))}">
      <div class="kicker">{html.escape(r.get('kicker',''))}</div>
      <h2>{html.escape(r['titel'])}</h2>
      <p>{html.escape(r['intro'][:110])}...</p>
      <div class="regel">{html.escape(meta_regel)}</div>
    </a>""")

    categorieen = sorted({r.get("categorie", "") for r in recepten if r.get("categorie")})
    chips = "".join(f'<button class="chip" data-cat="{html.escape(c)}">{html.escape(c)}</button>'
                    for c in categorieen)

    inhoud = f"""
<header class="kop"><div class="wrap">
  <h1>Het <span>kookboek</span></h1>
  <p>{SITE_ONDERTITEL}</p>
</div></header>
<main class="wrap">
  <input class="zoek" id="zoek" type="search" placeholder="Zoek op gerecht of ingredi&#235;nt...">
  <div class="chips">
    <button class="chip aan" data-cat="">Alles</button>{chips}
  </div>
  <div class="kaarten" id="lijst">{''.join(kaarten)}</div>
  <p class="leeg" id="leeg" style="display:none">Niets gevonden. Andere zoekterm proberen?</p>
</main>
<footer class="voet">{len(recepten)} recepten · Studio HeLeen</footer>
"""

    js = """
const zoek=document.getElementById('zoek');
const kaarten=[...document.querySelectorAll('.kaart')];
let cat='';
function filter(){
  const t=zoek.value.toLowerCase().trim(); let n=0;
  kaarten.forEach(k=>{
    const ok=(!t||k.dataset.zoek.includes(t))&&(!cat||k.dataset.cat===cat);
    k.style.display=ok?'block':'none'; if(ok)n++;
  });
  document.getElementById('leeg').style.display=n?'none':'block';
}
zoek.addEventListener('input',filter);
document.querySelectorAll('.chip').forEach(c=>c.addEventListener('click',()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('aan'));
  c.classList.add('aan'); cat=c.dataset.cat; filter();
}));
"""
    return pagina(SITE_TITEL, inhoud, js)


# ---------------------------------------------------------- receptpagina ----

def bronregel(bron):
    """Waar het recept vandaan komt, met een link als die er is.

    Mag een gewone tekst zijn ("Van oma Mieke") of een object met een naam
    en optioneel een url: {"naam": "Dagelijkse Kost", "url": "https://..."}.
    """
    if not bron:
        return ""
    if isinstance(bron, str):
        return f'<div class="bron">Bron: {html.escape(bron)}</div>'

    naam = bron.get("naam", "")
    url = bron.get("url", "")
    if not naam and not url:
        return ""
    # Alleen gewone weblinks, zodat er niets anders dan een url in de href belandt.
    if url.startswith(("http://", "https://")):
        tekst = html.escape(naam or url)
        return (f'<div class="bron">Bron: <a href="{html.escape(url)}" '
                f'target="_blank" rel="noopener noreferrer">{tekst}</a></div>')
    return f'<div class="bron">Bron: {html.escape(naam)}</div>'


def bouw_recept(r):
    meta = "".join(f"<div><span>{html.escape(m['label'])}</span><b>{html.escape(m['waarde'])}</b></div>"
                   for m in r.get("meta", []))

    ing = "".join(
        f'<li data-h="{html.escape(i.get("hoeveelheid",""))}"'
        f' data-vast="{"1" if i.get("schaal") is False else ""}">'
        f'<b class="hv">{html.escape(i.get("hoeveelheid",""))}</b> {html.escape(i["naam"])}</li>'
        for i in r["ingredienten"])

    stappen = "".join(
        f'<div class="stap"><div class="nr">{n}</div><div>'
        f'<h4>{html.escape(s["kop"])}</h4><p>{html.escape(s["tekst"])}</p></div></div>'
        for n, s in enumerate(r["stappen"], 1))

    praktijk = ""
    if r.get("uit_de_praktijk"):
        blokken = "".join(f'<div><h4>{html.escape(p["kop"])}</h4><p>{html.escape(p["tekst"])}</p></div>'
                          for p in r["uit_de_praktijk"])
        praktijk = f'<h3 class="blokkop">Uit de praktijk</h3><div class="praktijk">{blokken}</div>'

    tip = ""
    if r.get("tip"):
        tip = f'<div class="tip"><span class="pen">&#9998;</span><p>{html.escape(r["tip"])}</p></div>'

    # Elke receptpagina krijgt een printknop. Is er een A4, dan opent die;
    # zonder A4 print de browser de pagina zelf, met de printstijl onderaan de CSS.
    pdf_knop = (f'<a href="pdf/{r["pdf"]}" target="_blank">A4 printen</a>'
                if r.get("pdf")
                else '<button onclick="window.print()">Pagina printen</button>')

    # De eenheid mag als "enkelvoud|meervoud" staan, zodat "Voor 1 portie"
    # bij het omrekenen "Voor 2 porties" wordt en niet "Voor 2 portie".
    eenheid = r.get("portie_eenheid", "personen")
    enkelvoud, _, meervoud = eenheid.partition("|")
    meervoud = meervoud or enkelvoud
    eenheid_nu = enkelvoud if r["porties"] == 1 else meervoud

    inhoud = f"""
<main class="wrap">
  <a class="terug" href="index.html">&#8592; Alle recepten</a>
  <article class="recept">
    <div class="kicker">{html.escape(r.get('kicker',''))}</div>
    <h1>{html.escape(r['titel'])}</h1>
    <p class="intro">{html.escape(r['intro'])}</p>
    <div class="meta">{meta}</div>

    <h3 class="blokkop">Ingredi&#235;nten</h3>
    <div class="porties">
      <div class="tekst">Voor <b id="lbl">{r['porties']}</b> <span id="eenheid">{html.escape(eenheid_nu)}</span></div>
      <button id="min" aria-label="minder">&#8722;</button>
      <div class="aantal" id="aantal">{r['porties']}</div>
      <button id="plus" aria-label="meer">+</button>
    </div>
    <ul class="ing" id="ing">{ing}</ul>

    <h3 class="blokkop">Zo maak je het</h3>
    {stappen}
    {tip}
    {praktijk}
  </article>
  <footer class="voet">{html.escape(r.get('voet',''))}{bronregel(r.get('bron'))}</footer>
</main>
<div class="balk">
  <button id="wakker">Scherm aan houden</button>
  {pdf_knop}
</div>
"""

    js = """
const ENK=%s, MV=%s;
const basis=%d; let nu=basis;
const items=[...document.querySelectorAll('#ing li')];
function toon(n){
  const f=n/basis;
  document.getElementById('aantal').textContent=n;
  document.getElementById('lbl').textContent=n;
  document.getElementById('eenheid').textContent=(n===1)?ENK:MV;
  items.forEach(li=>{
    const h=li.dataset.h||'';
    if(li.dataset.vast){li.querySelector('.hv').textContent=h;return;}
    const m=h.match(/^(\\d+(?:[.,]\\d+)?)(.*)$/);
    if(!m){li.querySelector('.hv').textContent=h;return;}
    let w=parseFloat(m[1].replace(',','.'))*f;
    // Grof afronden waar het kan: 133 ml leest beter dan 133,33 ml, en
    // niemand weegt een derde gram af.
    w=(w>=100)?Math.round(w):((w>=10)?Math.round(w*10)/10:Math.round(w*100)/100);
    let s=(Math.abs(w-Math.round(w))<0.005)?String(Math.round(w)):String(w).replace('.',',');
    li.querySelector('.hv').textContent=s+m[2];
  });
}
document.getElementById('plus').onclick=()=>{nu++;toon(nu);};
document.getElementById('min').onclick=()=>{if(nu>1){nu--;toon(nu);}};
items.forEach(li=>li.onclick=()=>li.classList.toggle('af'));
document.querySelectorAll('.stap').forEach(s=>s.onclick=()=>s.classList.toggle('af'));

let lock=null;
const knop=document.getElementById('wakker');
knop.onclick=async()=>{
  try{
    if(lock){await lock.release();lock=null;knop.classList.remove('aan');
      knop.textContent='Scherm aan houden';}
    else{lock=await navigator.wakeLock.request('screen');knop.classList.add('aan');
      knop.textContent='Scherm blijft aan';
      lock.addEventListener('release',()=>{lock=null;knop.classList.remove('aan');
        knop.textContent='Scherm aan houden';});}
  }catch(e){knop.textContent='Lukt niet op dit toestel';}
};
""" % (json.dumps(enkelvoud), json.dumps(meervoud), r["porties"])

    return pagina(f"{r['titel']} · {SITE_TITEL}", inhoud, js)


# ------------------------------------------------------------------ main ----

def main():
    recepten = []
    for f in sorted(RECEPTEN.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            recepten.append(json.load(fh))

    if not recepten:
        print("Geen recepten gevonden in recepten/")
        return

    recepten.sort(key=lambda r: r["titel"].lower())

    if UIT.exists():
        shutil.rmtree(UIT)
    UIT.mkdir(parents=True)
    (UIT / ".nojekyll").write_text("")

    (UIT / "index.html").write_text(bouw_index(recepten), encoding="utf-8")
    for r in recepten:
        (UIT / f"{r['slug']}.html").write_text(bouw_recept(r), encoding="utf-8")

    if PDF_BRON.exists():
        shutil.copytree(PDF_BRON, UIT / "pdf")

    print(f"Klaar. {len(recepten)} recepten naar {UIT}/")
    for r in recepten:
        print(f"  - {r['titel']}")


if __name__ == "__main__":
    main()
