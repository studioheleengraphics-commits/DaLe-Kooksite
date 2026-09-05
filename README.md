# Het kookboek · Studio HeLeen

Een statische receptensite in de kookboek-huisstijl. Eén bron, twee uitgangen:
dezelfde receptdata voedt zowel de A4-PDF als de webpagina.

## Hoe het in elkaar zit

```
recepten/         één JSON per recept. Dit is je enige bron.
pdf/              de print-klare A4's, worden meegekopieerd
airfryer/         één JSON per categorie airfryertijden
build.py          generator: JSON in, complete site uit
build_airfryer.py generator van de airfryersite, draait mee met build.py
docs/             het resultaat. Niet handmatig aanpassen, wordt overschreven.
```

Elke pagina in `docs/` staat op zichzelf: stijl en scripts zitten ingesloten.
Geen framework, geen build-tools, geen npm. Open een bestand rechtstreeks in je
browser en het werkt.

## Een recept toevoegen

1. Kopieer een bestaand bestand uit `recepten/` naar `recepten/jouw-gerecht.json`.
2. Vul in. De `slug` bepaalt de URL, dus houd hem kleine letters en met streepjes.
3. Draai `python3 build.py`.
4. Push. Klaar.

Velden die niet vanzelf spreken:

| Veld | Wat het doet |
|---|---|
| `categorie` | Verschijnt als filterknop op de overzichtspagina |
| `trefwoorden` | Extra zoekwoorden, alleen voor de zoekbalk |
| `porties` | Het aantal waarop de ingrediënten kloppen. Hierop rekent de site om. |
| `schaal: false` | Zet dit bij een ingrediënt dat niet mag meeschalen, zoals één laurierblad of een snuf zout |
| `uit_de_praktijk` | Optioneel blok met extra tips onderaan |
| `pdf` | Bestandsnaam in `pdf/`. Laat weg en de printknop print de webpagina zelf. |

## Wat de familie krijgt

- Zoeken op gerecht of op ingrediënt, want "wat kan ik met die halve chorizo" is
  een echte vraag
- Filteren per categorie
- Porties omrekenen van 4 naar 6 of naar 2, hoeveelheden passen zich live aan
- Ingrediënten aantikken tijdens het uitpakken, stappen aantikken tijdens het koken
- Een knop die het scherm aan houdt, zodat je niet met deegvingers hoeft te swipen
- Een printknop op elke receptpagina, met de A4-PDF erachter waar die bestaat

Er is geen login en er wordt niets opgeslagen. Iedereen met de link kan lezen en
koken, niemand kan per ongeluk iets stukmaken.

## Crispy DaLe: de airfryertijden

Onder `docs/airfryer/` staat een tweede site met bereidingstijden, in dezelfde
huisstijl. Hij is bereikbaar via de knop rechtsboven op het kookboek, en terug
via de knop rechtsboven daar.

Wat hij doet:

- Eenenzeventig producten in acht categorieën, met zoeken op naam en trefwoord
- Uitklappen per product: temperatuur, tijd, schudmoment, kerntemperatuur en
  waaraan je ziet dat het klaar is
- Een timer die piept en trilt op elk schudmoment. Bij een product met twee
  bakstappen loodst hij je door beide en zegt wanneer je de temperatuur
  moet veranderen
- Een knop voor een volle mand, die overal ongeveer een vijfde tijd bijtelt
- Favorieten achter de sterknop bovenaan
- Een aparte pagina die oven en airfryer in twee richtingen omrekent, met de
  kerntemperaturen en de vuistregels die er echt toe doen

Een product toevoegen of een tijd bijstellen doe je in `airfryer/*.json`, en
daarna `python3 build.py`. De velden staan uitgelegd in `CLAUDE.md`.

De tijden in de lijst zijn richttijden uit algemene airfryerbronnen, geen
metingen van jouw toestel. Wat je uittest, zet je erin: dan klopt het voorgoed
en op elke telefoon, in plaats van in het geheugen van één app.

## Online zetten met GitHub Pages

1. Maak een repository, bijvoorbeeld `kookboek`. Zet hem op private als je dat
   liever hebt, Pages werkt dan nog steeds bij een betaald plan. Bij een gratis
   plan moet de repo publiek staan.
2. Push deze hele map.
3. Ga naar Settings, Pages. Kies bij Source: Deploy from a branch, branch `main`,
   map `/docs`.
4. Een minuut later staat je site op `https://<gebruikersnaam>.github.io/kookboek/`.

Stuur die link door en zet hem op de telefoon van de familie op het startscherm
(Deel, Zet op beginscherm). Het opent dan als een app, zonder browserbalk.

Eigen domein? Zet een bestand `CNAME` in `docs/` met daarin bijvoorbeeld
`kookboek.studioheleen.be`, en wijs een CNAME-record aan bij je DNS.

## Later uitbreiden

De volgorde die het minste werk oplevert:

1. Een foto per recept. Voeg een veld `foto` toe en toon hem bovenaan de kaart.
   Bij de airfryertijden kan dat nu al: zet de foto in `airfryer/fotos/`.
2. Een boodschappenlijst. Kan volledig in de browser, met `localStorage`, dus nog
   altijd zonder server.
3. Een weekmenu, dat bouwt voort op diezelfde lijst.
4. Een eigen tijd per product bewaren op de telefoon zelf, naast de richttijd.
   Handig om iets uit te proberen voor je het definitief in de JSON zet.

Pas als de familie zelf recepten wil kunnen toevoegen, heb je een echte app nodig.
Tot dan is dit lichter, sneller en zo goed als onverwoestbaar.
