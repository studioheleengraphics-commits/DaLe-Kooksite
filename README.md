# Het kookboek · Studio HeLeen

Een statische receptensite in de kookboek-huisstijl. Eén bron, twee uitgangen:
dezelfde receptdata voedt zowel de A4-PDF als de webpagina.

## Hoe het in elkaar zit

```
recepten/     één JSON per recept. Dit is je enige bron.
pdf/          de print-klare A4's, worden meegekopieerd
build.py      generator: JSON in, complete site uit
docs/         het resultaat. Niet handmatig aanpassen, wordt overschreven.
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
| `pdf` | Bestandsnaam in `pdf/`. Laat weg en de printknop verdwijnt vanzelf. |

## Wat de familie krijgt

- Zoeken op gerecht of op ingrediënt, want "wat kan ik met die halve chorizo" is
  een echte vraag
- Filteren per categorie
- Porties omrekenen van 4 naar 6 of naar 2, hoeveelheden passen zich live aan
- Ingrediënten aantikken tijdens het uitpakken, stappen aantikken tijdens het koken
- Een knop die het scherm aan houdt, zodat je niet met deegvingers hoeft te swipen
- De A4-PDF achter een printknop, voor wie liever papier heeft

Er is geen login en er wordt niets opgeslagen. Iedereen met de link kan lezen en
koken, niemand kan per ongeluk iets stukmaken.

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
2. Een boodschappenlijst. Kan volledig in de browser, met `localStorage`, dus nog
   altijd zonder server.
3. Een weekmenu, dat bouwt voort op diezelfde lijst.

Pas als de familie zelf recepten wil kunnen toevoegen, heb je een echte app nodig.
Tot dan is dit lichter, sneller en zo goed als onverwoestbaar.
