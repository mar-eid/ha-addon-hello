# My HA Add-ons (Hello World)

Dette repoet inneholder en minimal Home Assistant add-on: **Hello World**.

## Auto-oppdatering i Home Assistant

Selve auto-oppdateringen styres av Home Assistant Supervisor. Du trenger ikke å legge inn ekstra kode i add-onen.
Slik aktiverer du auto-oppdatering for denne add-onen:

1. Installer repoet i **Add-on Store** (Settings → Add-ons → Add-on Store → ⋮ → Repositories → legg inn repo-URL).
2. Åpne add-on-kortet **Hello World** etter installasjon.
3. Klikk **⋮** (meny) oppe til høyre eller bruk bryteren i UI, og aktiver **Auto update** (Auto-oppdater).
   - Når denne er på, vil Supervisor automatisk oppdatere add-onen når en ny versjon publiseres i dette repoet.

### Viktig for at auto-oppdatering skal fungere bra
- **Versjonsøkning:** Hver gang du endrer add-onen, øk `version` i `hello-world/config.json` (f.eks. `0.1.1` → `0.1.2`).
- **Tag/release (anbefalt):** Opprett en GitHub tag/release for samme versjon (f.eks. `v0.1.2`). Dette gjør det tydelig hva som er siste versjon.
- **Changelog:** Oppdater `CHANGELOG.md` med hva som er endret per versjon.

Home Assistant vil automatisk oppdage at en ny versjon er tilgjengelig når du pusher endringer til GitHub-repoet og øker versjonsnummeret i `config.json`.

## Struktur
```
ha-addons-hello/
├─ repository.json
└─ hello-world/
   ├─ config.json
   ├─ Dockerfile
   └─ run.sh
```

## Lokal testing (valgfritt)
- Du kan bygge containeren lokalt: `docker build -t hello-world-addon ./hello-world`
- Kjør lokalt (kun for test, ikke via Supervisor): `docker run --rm -it hello-world-addon`

## Endre beskrivelse/metadata
- Oppdater `hello-world/config.json` feltene `name`, `description`, `version`, `arch` osv. etter behov.
- `repository.json` i roten bør peke til riktig GitHub-URL og inneholde vedlikeholder-info.
