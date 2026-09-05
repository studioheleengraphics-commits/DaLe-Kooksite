# Kookboek Studio HeLeen

Statische receptensite in de Studio HeLeen kookboek-huisstijl, voor de familie.
Alleen lezen en koken: geen login, geen formulieren op de site zelf, niets
dat kapot kan. Toevoegen gebeurt via een issueformulier op GitHub, dat de
JSON laat schrijven en de generator laat draaien.

## Vaste werkafspraken

- `recepten/*.json` en `airfryer/*.json` zijn de enige bronnen. Alles wat je
  verandert, verander je daar.
- `docs/` wordt volledig overschreven door de generator. Nooit handmatig aanpassen.
- Na elke wijziging: `python3 build.py`. Zonder die stap verandert de site niet.
- Controleer het resultaat voor je commit. Open de gegenereerde pagina of maak
  een screenshot op 390px breed, want de site wordt vooral op een telefoon
  gelezen die op het aanrecht ligt.
- Commit in het Nederlands, kort en concreet: "recept toegevoegd: gambas al ajillo".
- Push naar `main`. GitHub Pages publiceert automatisch vanuit `/docs`.

## Structuur van een recept

```json
{
  "slug": "gambas-al-ajillo",
  "titel": "Gambas al ajillo",
  "kicker": "Tapas · Spanje",
  "categorie": "Tapas",
  "trefwoorden": ["spaans", "snel", "garnalen"],
  "intro": "Drie zinnen. Zie schrijfregels hieronder.",
  "porties": 4,
  "portie_eenheid": "persoon|personen",
  "meta": [{ "label": "Tijd", "waarde": "15 minuten" }],
  "ingredienten": [
    { "hoeveelheid": "400 g", "naam": "gepelde garnalen" },
    { "hoeveelheid": "1", "naam": "laurierblad", "schaal": false }
  ],
  "stappen": [{ "kop": "Knoflook aanzetten", "tekst": "Twee tot vier zinnen." }],
  "tip": "De handgeschreven tip in het rode kader.",
  "uit_de_praktijk": [{ "kop": "Optioneel blok", "tekst": "Extra tips onderaan." }],
  "voet": "Korte serveer- of bewaarzin.",
  "bron": { "naam": "Dagelijkse Kost", "url": "https://dagelijksekost.vrt.be/..." },
  "pdf": "gambas-al-ajillo.pdf"
}
```

Aandachtspunten:

- `slug` bepaalt de bestandsnaam en de URL: kleine letters, streepjes, geen accenten.
- `porties` is het aantal waarop de hoeveelheden kloppen. De site rekent hierop om.
- `portie_eenheid` schrijf je als `enkelvoud|meervoud`, zodat "Voor 1 portie" bij het
  omrekenen "Voor 2 porties" wordt. Eén woord mag ook, dat blijft dan onveranderd.
- `schaal: false` bij alles wat niet mag meeschalen: één laurierblad, een snuf zout,
  een scheutje olie om in te bakken.
- Zet de hoeveelheid vooraan in het veld `hoeveelheid`, niet in `naam`, anders kan
  de omrekening er niet bij.
- `meta` bevat twee tot vier velden. Meer past niet netjes op een smal scherm.
- `bron` vermeldt waar het recept vandaan komt, onderaan de receptpagina. Een
  gewone tekst mag ook: `"bron": "Van oma Mieke"`. Bij een object is `url`
  optioneel, en alleen http- en https-links worden klikbaar gemaakt. Laat het
  veld weg als je de herkomst niet weet, en verzin geen bron.
- `pdf` mag weg als er geen A4 bestaat. Elke receptpagina houdt een printknop:
  met een A4 opent die de PDF, zonder A4 print de browser de pagina zelf.

## Airfryertijden: Crispy DaLe

Tweede site in dezelfde repo, onder `docs/airfryer/`. Zelfde huisstijl, andere
inhoud: een lange lijst producten met temperatuur, tijd en een timer. Wordt
gegenereerd door `build_airfryer.py`, dat vanzelf meedraait met `build.py`.

- `airfryer/*.json` is de bron. Eén bestand per categorie, niet per product,
  want anders sta je bij elke wijziging in tachtig bestanden te zoeken.
- `volgorde` bepaalt waar de categorie in de lijst komt.
- Foto's komen in `airfryer/fotos/` en worden meegekopieerd. Zet de bestandsnaam
  in het veld `foto` van het product. Zonder foto blijft de rij gewoon smaller.

```json
{
  "categorie": "Diepvries",
  "volgorde": 1,
  "intro": "Eén zin boven de categorie.",
  "items": [
    {
      "naam": "Frieten uit de diepvries",
      "trefwoorden": ["friet", "patat"],
      "getest": true,
      "foto": "frieten.jpg",
      "graden": 200,
      "minuten": [15, 18],
      "schudden": 7,
      "voorverwarmen": true,
      "portie": "400 g, hooguit twee lagen dik",
      "kern": 75,
      "klaar": "Waaraan je ziet dat het klaar is.",
      "tip": "De handgeschreven notitie in het rode kader."
    }
  ]
}
```

Aandachtspunten:

- `minuten` is altijd een lijst van twee: de korte en de lange tijd. De timer
  neemt de korte, want dan ga je kijken. Is er maar één tijd, schrijf dan
  `[10, 10]`.
- `schudden` is het aantal minuten tussen twee schudmomenten. De timer piept
  dan. Zet `0` bij alles wat je één keer keert. Laat het veld weg als je het
  niet weet, dan zegt de site er niets over in plaats van iets te verzinnen.
  Hetzelfde geldt voor `voorverwarmen`.
- `kern` alleen bij vlees en vis, in graden. Die staat in het rood, want daar
  hangt meer van af dan van de klok.
- `stand` is een programma met een eigen temperatuur, zoals Max Crisp. Die komt
  als een gevuld zeegroen label naast de tijd te staan.
- `functie` is iets wat je bij eender welke stand kan aanzetten, zoals Double
  Stack Pro, dat de bovenste laag van het mandje extra warmte geeft. Die krijgt
  een omlijnd label, zodat je in één oogopslag ziet dat het iets anders is dan
  een stand. Beide velden mogen samen op dezelfde stap staan, en de timer zegt
  ze allebei bij de overgang naar een volgende stap.
- `getest: true` is het belangrijkste veld van de hele site: het betekent dat
  die tijd thuis is uitgeprobeerd en klopt. Het product krijgt een rode ster en
  komt achter de sterknop bovenaan. Zet het alleen bij wat echt gemeten is.
  Een uitgeteste tijd vervangt de richttijd, er komt geen tweede regel bij.
- Meerdere bakstappen na elkaar, zoals frieten die eerst garen en dan afbakken,
  schrijf je als `stappen` in plaats van `graden` en `minuten`. De timer loodst
  je er dan doorheen en zegt wanneer je de temperatuur moet veranderen:

```json
"stappen": [
  { "wat": "Garen",    "graden": 160, "minuten": [15, 15], "schudden": 5 },
  { "wat": "Afbakken", "graden": 200, "minuten": [8, 10],  "schudden": 4 }
]
```

**Verzin hier al helemaal geen cijfers.** Een verkeerde tijd bij kip is geen
schoonheidsfoutje. Neem tijden uit een betrouwbare bron of uit wat thuis is
uitgetest, en zet in de tip dat het uitgetest is.

## Schrijfregels

Dit wordt gelezen door iemand met vettige handen en een pan op het vuur.

**Intro**: drie zinnen. Wat het gerecht is en waarom je het wil, wat er praktisch
gebeurt, en dan de haak. Een concreet beeld werkt, holle superlatieven niet.

**Stapkoppen**: kort en handelend. "Wijn toevoegen", niet "Stap 3" en niet
"Bereidingswijze".

**Stapteksten**: twee tot vier zinnen. Zeg niet alleen wat er moet gebeuren maar
ook waarom, zeker waar het kan mislopen. Dat waarom is het verschil tussen dit
kookboek en een willekeurige receptenkaart.

**Vier tot zes stappen** leest het best. Het aantal mag afwijken van het
bronrecept. Een bewaar- of rustmoment als laatste stap mag je toevoegen.

**Tip**: twee tot drie zinnen over het enige punt waarop het echt kan misgaan,
of een kneep die tijd of afwas scheelt.

**Verzin geen cijfers.** Geen kooktijden, gewichten of houdbaarheden die niet in
het bronrecept staan of er betrouwbaar uit af te leiden zijn.

Vermijd emdashes. Vermijd clichés als "impact maken", "transformeren", "balans".

## Huisstijl

Rood `#AD2C2C` is het enige accent, zeegroen `#77968E` de stille tweede stem,
inkt `#1F1D1A` voor tekst, warm papier `#F0EEEB` als achtergrond. DM Sans voor
koppen, Inter voor lopende tekst, Caveat voor de tip. Deze waarden staan in de
CSS bovenaan `build.py`. Voeg geen tweede rood toe.

## Wat hier niet thuishoort

Geen accounts, geen database, geen backend. Wil iemand recepten kunnen toevoegen
via de site, dan is dat een apart project en geen uitbreiding van dit.
