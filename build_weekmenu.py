#!/usr/bin/env python3
"""
Het weekmenu - derde deel van het kookboek, onder docs/weekmenu/.

Leest weekmenu/week-*.json en weekmenu/algemeen.json. Draait mee met
build.py, dat de paginaschil en de huisstijl aanlevert.

De overzichtspagina draagt alle weken en dagen mee. JavaScript toont er
telkens één dag van, en opent op vandaag. Zonder JavaScript staat alles
gewoon onder elkaar.
"""

import json
import html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
BRON = ROOT / "weekmenu"

SITE_TITEL = "Het weekmenu"
SITE_ONDERTITEL = "Studio HeLeen · wat eten we vandaag"

MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]
MAANDEN_KORT = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul",
                "aug", "sep", "okt", "nov", "dec"]
VOOR = {2: "twee", 4: "vier"}

# Komt bovenop de CSS van build.py. Zelfde kleuren, geen nieuwe.
CSS = """
.recept h1{font-size:30px; overflow-wrap:break-word; hyphens:auto;}
.weken{display:flex; gap:8px; flex-wrap:wrap; margin:22px 0 10px;}
.dagchips{display:flex; gap:6px; margin:0 0 16px;}
.dagchips .chip{flex:1; padding:8px 0; text-align:center; line-height:1.25;}
.dagchips .chip b{display:block; font-family:'DM Sans',sans-serif; font-size:16px;
  color:var(--inkt);}
.dagchips .chip.aan b{color:var(--wit);}
.dagchips .chip.nu{border-color:var(--rood);}

.dag.recept{padding:26px 22px 24px; margin-bottom:22px;}
.dag h2{font-family:'DM Sans',sans-serif; font-size:30px; font-weight:700;
  line-height:1.1; margin:8px 0 16px; letter-spacing:-.6px; color:var(--rood);}
.moment{display:flex; gap:14px; padding:13px 0; border-top:1px solid var(--lijn);
  cursor:pointer;}
.moment .uur{font-family:'DM Sans',sans-serif; font-size:10px; letter-spacing:1.2px;
  text-transform:uppercase; color:var(--inkt-licht); min-width:58px; padding-top:5px;}
.moment .wat{flex:1; font-size:16px;}
.moment .kcal{color:var(--inkt-licht); font-size:13px; white-space:nowrap;}
.moment .detail{display:block; color:var(--inkt-zacht); font-size:15px; margin-top:2px;}
.moment .extra{display:block; color:var(--zeegroen); font-size:15px; margin-top:4px;}
.extra b, .tag{font-family:'DM Sans',sans-serif; font-size:10px; letter-spacing:1.2px;
  text-transform:uppercase; font-weight:700; margin-right:4px;}
.moment.af{opacity:.4;}
.moment.af .uur{color:var(--zeegroen);}
.moment a.gerecht{font-family:'DM Sans',sans-serif; font-weight:700; font-size:18px;
  line-height:1.25; display:block;}
.moment a.gerecht:after{content:" \\2192";}
.dagtotaal{display:flex; gap:10px; margin-top:6px; padding-top:16px;
  border-top:1px solid var(--lijn);}
.dagtotaal div, .voeding div{flex:1; background:var(--zeegroen); color:var(--wit);
  border-radius:10px; padding:10px 14px; font-size:13px;}
.dagtotaal span, .voeding span{display:block; font-family:'DM Sans',sans-serif;
  font-size:10px; letter-spacing:1.4px; text-transform:uppercase; opacity:.85;}
.dagtotaal b, .voeding b{font-family:'DM Sans',sans-serif; font-size:17px;}
.voeding{display:flex; gap:10px; margin-top:20px;}

.weekblok{background:var(--wit); border:1px solid var(--lijn); border-radius:12px;
  padding:6px 22px 22px; margin-bottom:22px;}
.weekblok .kaarten{padding-bottom:0; gap:10px;}
.weekblok .kaart{padding:14px 16px; background:var(--kaart);}
.weekblok .kaart h2{font-size:17px; margin:4px 0 0;}
.weeknoot{font-size:15px; color:var(--inkt-zacht); margin:0;}
.nootregel{font-size:14px; color:var(--inkt-zacht); margin:0 0 6px;}
.recept p.klein{font-size:14px; color:var(--inkt-zacht); margin:14px 0 0;}
.stap p{padding-top:3px;}
.praktijk ul{margin:0; padding:0; list-style:none; font-size:15px; color:var(--inkt-zacht);}

.ritme div{display:flex;}
.ritme .tag{flex:none; width:66px; padding-top:6px; color:var(--inkt-licht);}
.afspraken .moment .uur{min-width:78px;}
ul.punten{margin:0; padding-left:20px; font-size:16px;}
ul.punten li{margin-bottom:8px;}

@media print{ .weken,.dagchips{display:none;} }
"""


def e(s):
    return html.escape(str(s))


def datum_lang(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MAANDEN[d.month - 1]}"


def periode(w):
    a, b = date.fromisoformat(w["van"]), date.fromisoformat(w["tot"])
    if a.month == b.month:
        return f"{a.day}-{b.day} {MAANDEN_KORT[b.month - 1]}"
    return f"{a.day} {MAANDEN_KORT[a.month - 1]} - {b.day} {MAANDEN_KORT[b.month - 1]}"


def recept_bestand(w, nr):
    return f"week-{w['week']}-r{nr}.html"


def baksel_bestand(w):
    return f"week-{w['week']}-baksel.html"


def laad():
    weken = []
    for f in sorted(BRON.glob("week-*.json")):
        with open(f, encoding="utf-8") as fh:
            weken.append(json.load(fh))
    weken.sort(key=lambda w: w["van"])
    with open(BRON / "algemeen.json", encoding="utf-8") as fh:
        algemeen = json.load(fh)
    return weken, algemeen


# ------------------------------------------------------------ overzicht ----

def bouw_moment(w, m):
    kcal = f'<span class="kcal">{m["kcal"]} kcal</span>' if m.get("kcal") else ""
    if m.get("recept"):
        wat = (f'<a class="gerecht" href="{recept_bestand(w, m["recept"])}">{e(m["basis"])}</a>'
               f'<span class="detail">{e(m.get("detail", ""))}</span>')
    else:
        wat = e(m["basis"])
    extra = f'<span class="extra"><b>Extra</b>{e(m["extra"])}</span>' if m.get("extra") else ""
    return (f'<div class="moment"><div class="uur">{e(m["moment"])}</div>'
            f'<div class="wat">{wat}{extra}</div>{kcal}</div>')


def bouw_dag(w, d):
    # Met hoeveel er gegeten wordt, kan binnen een week wisselen. Het warme
    # gerecht van de dag weet het: dat recept is voor twee of voor vier.
    nr = next((m["recept"] for m in d["momenten"] if m.get("recept")), None)
    aantal = next((r["personen"] for r in w["recepten"] if r["nr"] == nr), w.get("voor"))
    kicker = f"Week {w['week']}"
    if aantal:
        kicker += f" · voor {VOOR.get(aantal, aantal)}"
    if d.get("thema"):
        kicker += f" · {d['thema']}"
    momenten = "".join(bouw_moment(w, m) for m in d["momenten"])
    return f"""
  <article class="recept dag" id="d{d['datum']}" data-datum="{d['datum']}">
    <div class="kicker">{e(kicker)}</div>
    <h2>{e(d['dag'])} {e(datum_lang(d['datum']))}</h2>
    {momenten}
    <div class="dagtotaal">
      <div><span>Basis</span><b>{d['basis']['kcal']} kcal</b> · {d['basis']['eiwit']} g eiwit</div>
      <div><span>Met extra</span><b>{d['extra']['kcal']} kcal</b> · {d['extra']['eiwit']} g eiwit</div>
    </div>
  </article>"""


def bouw_week(w):
    chips = "".join(
        f'<button class="chip" data-datum="{d["datum"]}">{e(d["dag"][:2])}'
        f'<b>{date.fromisoformat(d["datum"]).day}</b></button>'
        for d in w["dagen"])
    dagen = "".join(bouw_dag(w, d) for d in w["dagen"])
    voorbereiding = "".join(f"<li>{e(v)}</li>" for v in w["voorbereiding"])
    recepten = "".join(
        f'<a class="kaart" href="{recept_bestand(w, r["nr"])}">'
        f'<div class="kicker">{e(r["wanneer"])}</div><h2>{e(r["titel"])}</h2></a>'
        for r in w["recepten"])
    b = w["baksel"]
    noot = (f'<h3 class="blokkop">Zo werkt deze week</h3><p class="weeknoot">{e(w["noot"])}</p>'
            if w.get("noot") else "")
    return f"""
<section class="week" data-week="{w['week']}" data-van="{w['van']}" data-tot="{w['tot']}">
  <div class="dagchips">{chips}</div>
  {dagen}
  <div class="weekblok">
    {noot}
    <h3 class="blokkop">Voorbereiding deze week</h3>
    <ul class="punten">{voorbereiding}</ul>
    <h3 class="blokkop">Zondag bakken</h3>
    <div class="kaarten">
      <a class="kaart" href="{baksel_bestand(w)}">
        <div class="kicker">{e(b['opbrengst'])} · {e(b['tijd'])}</div><h2>{e(b['titel'])}</h2></a>
    </div>
    <h3 class="blokkop">De zeven recepten</h3>
    <div class="kaarten">{recepten}</div>
  </div>
</section>"""


INDEX_JS = """
const weken=[...document.querySelectorAll('.week')];
const dagen=[...document.querySelectorAll('.dag')];
const alleData=dagen.map(d=>d.dataset.datum);
function iso(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
const vandaag=iso(new Date());

function toon(datum){
  dagen.forEach(d=>{d.hidden=d.dataset.datum!==datum;});
  weken.forEach(w=>{
    const erin=datum>=w.dataset.van&&datum<=w.dataset.tot;
    w.hidden=!erin;
    document.querySelector('.weken .chip[data-week="'+w.dataset.week+'"]').classList.toggle('aan',erin);
  });
  document.querySelectorAll('.dagchips .chip').forEach(c=>{
    c.classList.toggle('aan',c.dataset.datum===datum);
    c.classList.toggle('nu',c.dataset.datum===vandaag);
  });
  try{history.replaceState(null,'','#'+datum);}catch(e){}
}
/* Vandaag als die in het schema staat. Ervoor de eerste dag, erna de laatste. */
function dichtstbij(){
  if(alleData.includes(vandaag))return vandaag;
  return vandaag<alleData[0]?alleData[0]:alleData[alleData.length-1];
}
document.querySelectorAll('.dagchips .chip').forEach(c=>c.onclick=()=>toon(c.dataset.datum));
document.querySelectorAll('.weken .chip').forEach(c=>c.onclick=()=>{
  const w=weken.find(x=>x.dataset.week===c.dataset.week);
  toon(vandaag>=w.dataset.van&&vandaag<=w.dataset.tot?vandaag:w.dataset.van);
});
document.getElementById('vandaag').onclick=()=>{toon(dichtstbij());window.scrollTo(0,0);};

/* Wat je al gegeten hebt, blijft aangevinkt op dit toestel tot de dag om is.
   Ieder vinkt dus op de eigen telefoon af; er wordt niets gedeeld. */
const GEGETEN='weekmenu-gegeten-v1';
let gegeten={};
try{gegeten=JSON.parse(localStorage.getItem(GEGETEN))||{};}catch(e){}
Object.keys(gegeten).forEach(d=>{if(d<vandaag)delete gegeten[d];});
function bewaar(){try{localStorage.setItem(GEGETEN,JSON.stringify(gegeten));}catch(e){}}
bewaar();
dagen.forEach(dag=>{
  const datum=dag.dataset.datum;
  [...dag.querySelectorAll('.moment')].forEach((m,i)=>{
    if((gegeten[datum]||[]).includes(i))m.classList.add('af');
    m.onclick=ev=>{
      if(ev.target.closest('a'))return;
      const aan=m.classList.toggle('af');
      const lijst=(gegeten[datum]||[]).filter(x=>x!==i);
      if(aan)lijst.push(i);
      if(lijst.length)gegeten[datum]=lijst; else delete gegeten[datum];
      bewaar();
    };
  });
});

const uitHash=location.hash.slice(1);
toon(alleData.includes(uitHash)?uitHash:dichtstbij());
"""


def bouw_index(weken):
    weekchips = "".join(
        f'<button class="chip" data-week="{w["week"]}">{e(periode(w))}</button>'
        for w in weken)
    inhoud = f"""
<header class="kop"><div class="wrap">
  <div class="koprij">
    <h1>Het <span>weekmenu</span></h1>
    <a class="pil" href="../index.html">Kookboek</a>
  </div>
  <p>{SITE_ONDERTITEL}</p>
</div></header>
<main class="wrap">
  <div class="weken">{weekchips}</div>
  {''.join(bouw_week(w) for w in weken)}
</main>
<footer class="voet">Alle voedingswaarden zijn schattingen · Studio HeLeen</footer>
<div class="balk">
  <button id="vandaag" class="nieuw">Vandaag</button>
  <a href="afspraken.html">Afspraken</a>
  <a href="../airfryer/index.html">Airfryer</a>
</div>
"""
    return inhoud, INDEX_JS


# ---------------------------------------------------------- receptpagina ----

RECEPT_JS = """
document.querySelectorAll('#ing li').forEach(li=>li.onclick=()=>li.classList.toggle('af'));
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
"""


def lijst_ingredienten(items):
    return "".join(
        f'<li><b class="hv">{e(i.get("hoeveelheid", ""))}</b> {e(i["naam"])}</li>'
        for i in items)


def lijst_stappen(stappen):
    # Dezelfde afvinkbare stappen als in het kookboek, alleen zonder kopje:
    # het weekmenu geeft per stap enkel de tekst.
    return "".join(
        f'<div class="stap"><div class="nr">{n}</div><div><p>{e(s)}</p></div></div>'
        for n, s in enumerate(stappen, 1))


def receptschil(terug, terug_tekst, kicker, titel, intro, meta, noot, ingredienten,
                stappen, onder):
    meta_html = "".join(f"<div><span>{e(l)}</span><b>{e(v)}</b></div>" for l, v in meta)
    return f"""
<main class="wrap">
  <a class="terug" href="{terug}">&#8592; {e(terug_tekst)}</a>
  <article class="recept">
    <div class="kicker">{e(kicker)}</div>
    <h1>{e(titel)}</h1>
    <p class="intro">{e(intro)}</p>
    <div class="meta">{meta_html}</div>

    <h3 class="blokkop">Ingredi&#235;nten</h3>
    <p class="nootregel">{e(noot)}</p>
    <ul class="ing" id="ing">{lijst_ingredienten(ingredienten)}</ul>

    <h3 class="blokkop">Zo maak je het</h3>
    {lijst_stappen(stappen)}
    {onder}
  </article>
  <footer class="voet">Voedingswaarden zijn schattingen</footer>
</main>
<div class="balk">
  <button id="wakker">Scherm aan houden</button>
  <button onclick="window.print()">Pagina printen</button>
</div>
"""


def bouw_recept(w, r):
    dag = next(d for d in w["dagen"]
               if any(m.get("recept") == r["nr"] for m in d["momenten"]))
    extra = "".join(f"<li>{e(x)}</li>" for x in r["verdelen"]["extra"])
    noten = "".join(f'<p class="klein">{e(n)}</p>' for n in r.get("noten", []))
    v = r["voeding"]
    onder = f"""
    <h3 class="blokkop">Zo verdelen</h3>
    <div class="praktijk">
      <div><h4>Basis</h4><p>{e(r['verdelen']['basis'])}</p></div>
      <div><h4>Extra erbij</h4><ul>{extra}</ul></div>
    </div>
    {noten}
    <div class="voeding">
      <div><span>Basis</span><b>{v['basis']['kcal']} kcal</b> · {v['basis']['eiwit']} g eiwit</div>
      <div><span>Met extra</span><b>{v['extra']['kcal']} kcal</b> · {v['extra']['eiwit']} g eiwit</div>
    </div>"""
    eenheid = "persoon" if r["personen"] == 1 else "personen"
    return receptschil(
        f"index.html#{dag['datum']}", f"{dag['dag']} {datum_lang(dag['datum'])}",
        f"Week {w['week']} · {r['wanneer']}", r["titel"], r["ondertitel"],
        [("Voor", f"{r['personen']} {eenheid}"), ("Tijd", r["tijd"])],
        r["noot"], r["ingredienten"], r["stappen"], onder)


def bouw_baksel(w):
    b = w["baksel"]
    noten = "".join(f'<p class="klein">{e(n)}</p>' for n in b.get("noten", []))
    v = b["voeding"]
    onder = f"""
    <h3 class="blokkop">Zo gebruiken</h3>
    <div class="praktijk">
      <div><h4>Per portie</h4><p>{e(b['per_portie'])}</p></div>
      <div><h4>Bewaren</h4><p>{e(b['bewaren'])}</p></div>
    </div>
    {noten}
    <div class="voeding">
      <div><span>{e(v['label'])}</span><b>{e(v['kcal'])}</b> · {e(v['eiwit'])}</div>
    </div>"""
    return receptschil(
        f"index.html#{w['van']}", f"Week {w['week']}",
        f"Week {w['week']} · zondag bakken", b["titel"], b["ondertitel"],
        [("Goed voor", b["opbrengst"]), ("Tijd", b["tijd"])],
        b["noot"], b["ingredienten"], b["stappen"], onder)


# -------------------------------------------------------------- afspraken ----

def bouw_afspraken(a):
    def punten(items):
        return '<ul class="punten">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"

    ritme = "".join(
        f'<div class="moment"><div class="uur">{e(r["moment"])}</div>'
        f'<div class="wat">{e(r["wat"])}'
        + (f'<span class="detail">{e(r["opmerking"])}</span>' if r.get("opmerking") else "")
        + "</div></div>"
        for r in a["dagritme"])
    weekritme = "".join(
        f'<div class="moment"><div class="uur">{e(r["dag"])}</div><div class="wat ritme">'
        + "".join(f'<div><b class="tag">{uur}</b>{e(r[sleutel])}</div>' for uur, sleutel in
                  [("10 u", "tien"), ("14.30 u", "half_drie"), ("16.30 u", "half_vijf"), ("20 u", "acht")])
        + "</div></div>"
        for r in a["weekritme"])
    ruil = "".join(
        f'<div><h4>{e(g["soort"])}</h4><ul>'
        + "".join(f"<li>{e(k)}</li>" for k in g["keuzes"]) + "</ul></div>"
        for g in a["ruillijst"])
    voorbereiding = "".join(f"<li>{e(v)}</li>" for v in a["voorbereiding"])
    let_op = (f'<div class="tip"><span class="pen">&#9998;</span><p>{e(a["let_op"])}</p></div>'
              if a.get("let_op") else "")

    return f"""
<main class="wrap">
  <a class="terug" href="index.html">&#8592; Het weekmenu</a>
  <article class="recept afspraken">
    <div class="kicker">Geldt voor alle weken, met twee en met vier</div>
    <h1>Afspraken en voorbereiding</h1>
    {let_op}

    <h3 class="blokkop">Dagritme</h3>
    {ritme}
    <p class="klein">{e(a['vaste_dagen'])}</p>

    <h3 class="blokkop">Porties en rekenafspraken</h3>
    {punten(a['porties'])}

    <h3 class="blokkop">Wat we bewust doen</h3>
    {punten(a['bewust'])}

    <h3 class="blokkop">Basisvoorbereiding op zondag</h3>
    <ul class="punten">{voorbereiding}</ul>

    <h3 class="blokkop">Tussendoortjes door de week</h3>
    {weekritme}
    <p class="klein">{e(a['weekritme_noot'])}</p>

    <h3 class="blokkop">Ruillijst</h3>
    <p class="nootregel">{e(a['ruillijst_intro'])}</p>
    <div class="praktijk">{ruil}</div>
    <p class="klein">{e(a['ruillijst_noot'])}</p>
  </article>
</main>
<div class="balk">
  <a href="index.html">Terug naar het weekmenu</a>
  <a href="../index.html">Het kookboek</a>
</div>
"""


# ------------------------------------------------------------------ main ----

def bouw(uit, pagina):
    """Schrijft de weekmenusite naar uit/. pagina is de schil uit build.py."""
    if not BRON.exists():
        return 0
    weken, algemeen = laad()
    if not weken:
        return 0
    uit.mkdir(parents=True, exist_ok=True)

    inhoud, js = bouw_index(weken)
    (uit / "index.html").write_text(pagina(SITE_TITEL, inhoud, js, CSS, "../"), encoding="utf-8")
    (uit / "afspraken.html").write_text(
        pagina(f"Afspraken · {SITE_TITEL}", bouw_afspraken(algemeen), "", CSS, "../"),
        encoding="utf-8")
    for w in weken:
        (uit / baksel_bestand(w)).write_text(
            pagina(f"{w['baksel']['titel']} · {SITE_TITEL}", bouw_baksel(w), RECEPT_JS, CSS, "../"),
            encoding="utf-8")
        for r in w["recepten"]:
            (uit / recept_bestand(w, r["nr"])).write_text(
                pagina(f"{r['titel']} · {SITE_TITEL}", bouw_recept(w, r), RECEPT_JS, CSS, "../"),
                encoding="utf-8")
    return len(weken)
