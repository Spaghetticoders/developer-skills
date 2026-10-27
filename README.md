<p align="center">
  <img src=".claude-plugin/icon.png" width="96" alt="Spaghetti Coders">
</p>

<h1 align="center">Come si lavora nel 2026</h1>

<p align="center">
  <b>Sei skill per Claude Code che usiamo in ogni progetto.</b><br>
  Dal ticket al rilascio, con un metodo invece che a caso.
</p>

<p align="center">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-skills-13F4C8?style=flat-square&labelColor=00070E">
  <img alt="Licenza MIT" src="https://img.shields.io/badge/licenza-MIT-E3FF2C?style=flat-square&labelColor=00070E">
  <img alt="Lingua" src="https://img.shields.io/badge/lingua-italiano-006DFF?style=flat-square&labelColor=00070E">
</p>

---

L'AI scrive codice più veloce di chiunque. **Il difficile non è più scriverlo**:
è sapere cosa chiederle, controllare quello che ha fatto e consegnarlo pulito.

Queste skill sono il nostro metodo, scritto in modo che Claude Code lo segua da
solo. Non sono prompt magici. Sono le regole che abbiamo imparato sbagliando:
ogni riga è nata da un difetto vero.

## Il metodo in quattro passaggi

```
  ticket ──▶ 01 PIANO ──▶ 02 SQUADRA ──▶ 03 VERIFICA ──▶ 04 CONSEGNA
              │             │               │               │
          start-work     squadra      verify-for-real     deliver
                                      gui-test
                                      figma-check
```

| | Skill | Cosa fa | Perché |
|---|---|---|---|
| 01 | [`start-work`](skills/start-work/SKILL.md) | Legge le card e **i loro commenti**, scrive un piano e **si ferma** ad aspettare il via libera. Poi sviluppo, test, cicli di audit, report. | Senza un piano, l'AI ti dà codice a caso. |
| 02 | [`squadra`](skills/squadra/SKILL.md) | Una squadra di agenti con ruoli separati (analista, sviluppatore, revisore, tester, approvatore) su un tabellone condiviso, a cancelli. | Chi scrive il codice non deve essere chi lo controlla. |
| 03 | [`verify-for-real`](skills/verify-for-real/SKILL.md) | Rompi la correzione e guarda il test fallire. Inietta il guasto invece di dedurlo. Conta invece di stimare. | Quando l'AI dice "fatto!", non è vero finché non lo vedi. |
| 03 | [`gui-test`](skills/gui-test/SKILL.md) | Pilota il simulatore iOS con idb: trova gli elementi per etichetta, tocca, scorre, scrive, cattura. Script incluso. | Una schermata non è verificata finché non la si è guardata. |
| 03 | [`figma-check`](skills/figma-check/SKILL.md) | Scarica nodo e render dal Figma e li confronta con la schermata vera, misure comprese. | Testi, misure e ordine. Non l'impressione generale. |
| 04 | [`deliver`](skills/deliver/SKILL.md) | Trasforma un albero sporco in commit disgiunti e leggibili. Non pusha mai se non glielo dici. | Il lavoro finisce quando arriva al cliente, non quando compila. |

## Installazione

**Come plugin** (consigliato), dentro Claude Code:

```
/plugin marketplace add Spaghetticoders/developer-skills
/plugin install metodo@spaghetticoders
```

Le skill si invocano come `/metodo:start-work`, `/metodo:squadra` e così via.
Claude le usa anche da solo quando il compito lo richiede.

**Oppure a mano**, copiando le cartelle tra le tue skill personali:

```sh
git clone https://github.com/Spaghetticoders/developer-skills.git
cp -R developer-skills/skills/* ~/.claude/skills/
```

## Come si usa, in pratica

```
/metodo:start-work PROJ-142 PROJ-143
```

1. Claude legge le due card e i commenti, guarda il codice, e ti presenta un piano.
2. **Si ferma.** Tu leggi, correggi, dai il via.
3. Sviluppa a fette. Ogni fetta passa dai test e dal simulatore (`gui-test`),
   e se c'è un design dal confronto col Figma (`figma-check`).
4. Ogni correzione passa da `verify-for-real`: si rompe, si guarda il test
   fallire, si ripristina.
5. Cicli di audit finché un giro intero trova solo cosmetica.
6. Report finale. Il commit lo chiedi tu, con `deliver`.

Per il lavoro grosso, `squadra` mette in piedi un team di agenti che si passano
il testimone, con un approvatore nuovo alla fine che può rimandare tutto indietro.

## Requisiti

- [Claude Code](https://claude.com/claude-code)
- Per `squadra`: gli agent team attivi, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Per `gui-test`: macOS, Xcode e [idb](https://fbidb.io)
  (`brew tap facebook/fb && brew install idb-companion`, `pip install fb-idb`)
- Per `figma-check`: un token personale Figma in `FIGMA_TOKEN`

Gli esempi parlano di Flutter e iOS perché è quello che facciamo ogni giorno, ma
`start-work`, `squadra`, `verify-for-real` e `deliver` valgono per qualunque stack.

## Le regole dietro a tutto

- **Prima il piano, poi il codice.** E in mezzo, un umano che dice sì.
- **Chi scrive non controlla.** Revisore e tester sono sempre altri.
- **"Fatto" vuol dire verificato.** Una correzione che non hai visto fallire non
  è una correzione.
- **Niente commit e niente push senza che tu lo chieda.** La storia del repo è tua.

## Chi siamo

<a href="https://www.spaghetticoders.it"><b>Spaghetti Coders</b></a> sviluppa app
Flutter, siti e prodotti digitali, con l'AI dentro il metodo e non al posto suo.

Queste skill sono il regalo della live **"Come si lavora nel 2026: AI, codice e
metodo"**. Se le usi e le migliori, apri una issue o una pull request.

Hai un progetto da far crescere? [Parliamone](https://www.spaghetticoders.it/spiegaciiltuoprogetto/).

## Licenza

[MIT](LICENSE). Usale, cambiale, portale nel tuo team.
