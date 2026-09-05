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

- Tweeëntachtig producten in acht categorieën, met zoeken op naam en trefwoord
- Uitklappen per product: temperatuur, tijd, schudmoment, kerntemperatuur en
  waaraan je ziet dat het klaar is
- Een timer die piept en trilt op elk schudmoment. Bij een product met twee
  bakstappen loodst hij je door beide en zegt wanneer je de temperatuur
  moet veranderen
- Een knop voor een volle mand, die overal ongeveer een vijfde tijd bijtelt
- Een rode ster bij alles wat thuis is uitgetest, met een knop die daarop filtert
- Een knop Toevoegen, en een knop Aanpassen bij elk product, zodat je aan de
  airfryer meteen kan noteren wat werkte
- Een aparte pagina die oven en airfryer in twee richtingen omrekent, met de
  kerntemperaturen en de vuistregels die er echt toe doen

Een product toevoegen of een tijd bijstellen doe je in `airfryer/*.json`, en
daarna `python3 build.py`. De velden staan uitgelegd in `CLAUDE.md`.

De veertien producten met een ster zijn thuis uitgetest en kloppen. De rest
zijn richttijden uit algemene airfryerbronnen, bedoeld als vertrekpunt. Wat je
uittest zet je erin, met `getest: true`, en dan klopt het voorgoed en op elke
telefoon in plaats van in het geheugen van één app.

## Iets toevoegen zonder JSON aan te raken

Er is geen server en geen login, dus er is ook geen plek waar de site zelf iets
kan bewaren voor iedereen. Daarom zijn er twee wegen, en ze sluiten op elkaar aan.

### Meteen, op de telefoon in je hand

Onderaan de airfryersite staat **+ Toevoegen**, en in elk opengeklapt product
staat **Aanpassen**. Je vult een naam, graden en minuten in, eventueel een
tweede ronde en een stand, en je bewaart. Het staat er meteen, doet mee met
zoeken en met de timer, en overleeft het sluiten van de browser.

Dat bewaren gebeurt in de browser van dat ene toestel. Niemand anders ziet het,
en een nieuwe telefoon begint weer blanco. Zulke producten dragen daarom het
label *deze telefoon*, en een bijgestelde tijd het label *aangepast*, met een
zeegroene rand eromheen. Zo weet je altijd wat van de site komt en wat van jou.

Bij elk van die twee staat een knop **Voorgoed op de site**. Die opent het
GitHub-formulier hieronder, al ingevuld met wat je net noteerde. Eén keer
versturen en het staat vast voor iedereen. Naast elke knop staat *Zet terug*
of *Verwijderen*, voor als het toch niet klopte.

### Voorgoed, voor iedereen

Ga naar het tabblad Issues, klik New issue en kies:

| Formulier | Waarvoor |
|---|---|
| Recept toevoegen | Een heel recept, hoe rommelig geplakt ook |
| Airfryertijd toevoegen of bijstellen | Iets nieuws, een tijd die niet klopt, of een ster |

Je vult in, je verstuurt, en een workflow schrijft de JSON, draait de generator
en zet het online. Een minuutje later staat het op alle telefoons. Loopt er iets
mis, dan blijft de issue open staan met een link naar wat er gebeurde.

Bij de airfryertijden hoef je alleen in te vullen wat er verandert. Bestaat het
product al, dan wordt het bijgewerkt en blijft alles wat je leeg laat gewoon
staan. Zo geef je een ster aan iets dat je eindelijk hebt uitgetest zonder de
tijd opnieuw in te tikken, of stel je een tijd bij zonder de ster kwijt te
raken. De ster zelf zet en haal je met het keuzemenu in datzelfde formulier.

Eén ding dat niet vanzelf spreekt: workflows die op een issue reageren draaien
altijd vanaf de standaardbranch. Een verbetering aan zo'n formulier of workflow
doet dus pas iets zodra ze op `main` staat.

Twee dingen om te weten. Alleen issues van de eigenaar van de repository zetten
dit in gang, dus de rest van de familie kan lezen en koken maar niets
publiceren. En de titel van een airfryertijd moet met `Airfryertijd:` beginnen,
want daaraan wordt het onderscheid met een recept gemaakt. Het formulier vult
dat vanzelf voor je in.

### Over die token

De workflows draaien op de servers van GitHub, niet op jouw computer. Wanneer
iemand het formulier verstuurt, moet GitHub daar Claude kunnen starten, en dan
is er iets nodig dat zegt: dit mag, en het gaat op de rekening van Leen. Dat
is de token. Een sleutel, meer niet.

Hij loopt op je Claude-abonnement, dus er komt geen aparte factuur van de API
bij. En omdat deze repository publiek staat, rekent GitHub ook de minuten van
Actions niet aan.

Aanmaken doe je zo:

1. Zorg dat Claude Code op je eigen computer staat, en meld je aan.
2. Draai in de terminal `claude setup-token`. Je krijgt een lange tekenreeks
   terug. Die is de token.
3. Ga in de repository naar Settings, Secrets and variables, Actions, en klik
   New repository secret.
4. Naam: `CLAUDE_CODE_OAUTH_TOKEN`. Waarde: die tekenreeks. Bewaren.

Het kan ook in één beweging: draai `/install-github-app` in Claude Code op je
computer. Dat installeert de Claude GitHub App op de repository en zet de token
er meteen bij. Daarvoor moet de GitHub CLI geïnstalleerd zijn.

Plak de token nergens anders. Niet in een bestand in de repository, niet in
een issue. Een secret is de enige plek waar hij hoort, want daar kan niemand
hem nog uitlezen, ook jij niet.

Zolang hij ontbreekt, stoppen de workflows meteen en netjes, zonder rode
kruisjes op elke issue die je opent. Beginnen ze later te klagen over
authenticatie, dan is de token verlopen of ingetrokken en maak je op dezelfde
manier een nieuwe.

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

Pas als de familie zelf recepten wil kunnen toevoegen, heb je een echte app nodig.
Tot dan is dit lichter, sneller en zo goed als onverwoestbaar.
