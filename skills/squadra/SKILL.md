---
name: squadra
description: Porta una richiesta al risultato con una squadra di teammate coordinati (agent team) su un tabellone condiviso. Analista, pixel-perfect, sviluppatore, revisore, tester, approvatore lavorano a cancelli, in ciclo, finché il lavoro non è perfetto. Si invoca quando il lavoro vale più di una testa sola.
---

# Lavorare in squadra

Una squadra di agenti attorno a un tabellone. Non è «più agenti perché sono
tanti»: è **separare chi scrive da chi controlla**, perché chi ha appena scritto
una riga è la persona meno adatta a vederne il difetto.

La squadra è un **agent team**, non una fila di subagent usa-e-getta: ogni
membro ha un nome, resta vivo fra un giro e l'altro, e parla con gli altri.
Serve `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` nell'ambiente (per esempio in
`~/.zshrc`); senza, un agente con nome è un subagent qualunque e il protocollo
degrada a «il PM fa da ponte» (vedi *Il ciclo lungo*).

Costa — un teammate è un'istanza intera, più cara di un subagent. Un giro
completo sono 6-10 agenti e parecchi minuti. Per una correzione di tre righe non
si convoca la squadra: si fa, si rompe, si guarda il test fallire.

---

## Come parlano davvero fra loro

Tre cose, e conviene saperle prima di prometterne altre.

**Il tabellone.** Un file in append, uno per lavorazione:
`<scratchpad>/squadra/<slug>/TABELLONE.md`. Ogni agente **lo legge per intero
all'inizio** ed è la memoria condivisa: l'unica cosa che sopravvive alla
sessione, e quindi l'unica fonte di verità. Un messaggio fra due agenti che non
finisce sul tabellone non è successo.

**Ci scrive chi può.** Gli agenti in sola lettura — analista, pixel, tester,
approvatore — **non hanno gli strumenti per appendere**, ed è voluto: se glieli
dessi per il tabellone li avrebbero anche per il repo. Quindi **chiudono il loro
turno con il blocco già formattato, pronto da incollare**, e **il PM lo appende
per loro**. È il PM il segretario della riunione, non i partecipanti.

**I teammate si parlano, per nome.** Si spawnano con `Agent` + `name`
(`dev`, `revisore`, `tester`, `pixel`, …) e si scrivono con `SendMessage`
verso quel nome — **non c'è broadcast**: un messaggio, un destinatario. Lungo la
catena del ciclo il testimone passa **direttamente**: il dev che finisce scrive
al revisore, il revisore al tester. Due regole, perché il PM non perda il filo:

- chi passa il testimone manda **anche al PM** una riga (cosa ha fatto, a chi lo
  ha passato), e il PM la mette sul tabellone;
- **`SendMessage` riuscito ≠ letto.** Un dev è rimasto fermo 35 minuti su
  un'autorizzazione già data. Se un agente dice di essere bloccato su una cosa
  decisa, si rimanda il messaggio invece di supporre.

Quando un teammate finisce il turno, **l'avviso di idle arriva da solo al PM**,
con la sua risposta finale dentro: il PM non costruisce waiter e non aspetta
prosa. Legge l'avviso, legge l'albero, appende.

Un teammate **idle non è morto**: resta raggiungibile, e un `SendMessage` lo
riprende con tutto il suo contesto. Il revisore del secondo giro è **lo stesso**
del primo, e si ricorda i suoi rilievi — è il motivo per cui la squadra costa
meno di quanto sembri. L'unica eccezione voluta è l'approvatore, che deve essere
nuovo.

**La lista compiti condivisa.** I teammate hanno `TaskCreate` / `TaskList` /
`TaskUpdate`: una fetta = un compito, chi la prende la marca in corso, chi la
chiude la marca fatta. È la tabella di chi-fa-cosa; **non sostituisce il
tabellone**, che resta il registro ragionato. Il PM potrebbe non vedere quegli
strumenti nella sua sessione (in alcune versioni al lead non compaiono): in quel
caso li legge attraverso il tabellone e non ci costruisce sopra.

**Il PM è la sessione principale, non un agente.** Deviazione voluta dalla
richiesta, e il motivo è che solo la sessione principale può: chiedere all'utente,
tenere `flutter run` e il simulatore, rilanciare un agente, e restare viva fra un
giro e l'altro. Un PM spawnato sarebbe un teammate che non può fare niente di
tutto questo. Il PM **non fa il lavoro al posto della squadra**: quando un
teammate sta lavorando, il PM aspetta l'avviso, non si mette a scrivere lui.

### Il formato del tabellone

```markdown
# <slug> — <la richiesta in una riga>
Ramo: <branch>   Avviata: <data ora>

## Richiesta
<il testo dell'utente, verbatim>

## Squadra
dev · revisore · tester · pixel   (nomi dei teammate, così come spawnati)

## Registro
### [ora] ANALISTA — <esito in tre parole>
- **Trovato:** …
- **Aperto:** …
- **Per chi:** dev / pixel / tester
```

Una voce per agente per giro, con l'ora della macchina (`date`) in testa.
**Niente riassunti del tabellone dentro il tabellone**: si appende, non si
riscrive.

---

## I ruoli

Ognuno riceve dal PM: il suo nome, il percorso del tabellone, il suo compito in
tre righe, i nomi degli altri e **che cosa deve produrre**. Nessuno riceve «fai
del tuo meglio».

| # | ruolo | fa | non fa |
|---|---|---|---|
| 1 | **PM** (sessione principale, lead del team) | coordina, apre e chiude i cancelli, rilancia il ciclo, chiede all'utente quando è bloccato | non scrive codice |
| 2 | **Analista funzionale** | legge richiesta **e** codice, enumera i casi d'uso, trova i buchi nelle logiche | non corregge |
| 3 | **Pixel-perfect** | confronta ogni schermata col nodo Figma, misura, ha **diritto di veto** sull'UI | non tocca la logica |
| 4 | **Sviluppatore** | scrive il codice | non si auto-approva |
| 5 | **Revisore + unit test** | scrive gli unit test, rilegge le logiche del dev, giudica la qualità | non riscrive la feature |
| 6 | **Tester funzionale** | esercita tutti i casi d'uso, sul simulatore quando è UI | non corregge |
| 7 | **Approvatore** | rilegge tutto a fine giro: **APPROVA** o **RI-ITERA** con rilievi puntuali | non è un timbro |
| 8 | **Archivista** | solo dopo l'OK: memorie di progetto, doc, memoria di Claude | non parte prima |

Il PM può spawnarne altri quando serve un mestiere che non c'è (sicurezza,
prestazioni, accessibilità, backend). Vale la stessa regola: compito stretto,
prodotto dichiarato.

**Tetto.** Vivi insieme, non più di **5-6**: si spawna un ruolo quando il suo
cancello si avvicina, non tutti all'apertura. In totale il giro sta sotto i 15
agenti; se ne servono di più, il lavoro va spezzato in due lavorazioni, non
gonfiato.

**Un file, un proprietario.** Due teammate che scrivono lo stesso file si
sovrascrivono a vicenda, e nessuno se ne accorge. Il PM assegna le fette per
file, e lo scrive sul tabellone.

---

## Il protocollo

Cancelli, non fasi. **Un cancello non si apre finché il suo criterio non è vero**,
e il criterio è scritto, non a sensazione.

**0. Apertura.** Il PM crea il tabellone, ci copia la richiesta *verbatim*, e
legge lo stato del repo (il ramo parte da `origin/main`, non dal `main` locale).
Se la richiesta ha un'ambiguità che cambia il lavoro, si chiede **adesso** — non
a metà.

**1. Capire.** Analista, e insieme il pixel-perfect se c'è UI. In parallelo: non
dipendono l'uno dall'altro.
→ *Cancello:* i casi d'uso sono enumerati e i nodi Figma identificati (o è
scritto che non esistono).

**2. Piano.** Il PM lo scrive sul tabellone: cosa cambia, dove, cosa si rompe,
cosa resta da decidere, **quale file è di chi**. Se c'è un punto che dipende
dall'utente, si chiede qui.
→ *Cancello:* il piano copre ogni buco che l'analista ha trovato, o dice perché no.

**3. Ciclo.** Per ogni fetta:

```
dev → revisore(+unit test) → tester → pixel (se UI)
        ↑                                    │
        └──────── rilievi ───────────────────┘
```

Il testimone passa **da teammate a teammate** con `SendMessage`: chi finisce
scrive al prossimo **quello che ha fatto e dove**, non tutto il tabellone, e
avvisa il PM con una riga. I rilievi tornano al dev per la stessa via. Sono
**gli stessi teammate** a ogni giro — il revisore riprende dai suoi rilievi, il
dev dalle sue modifiche — finché un giro intero produce **solo rilievi
cosmetici**: è il segnale che la curva è scesa.

Il PM resta fuori dalla catena ma non fuori dal giro: apre e chiude il cancello,
e prima di spendere un dev dietro a un rilievo **ne verifica la fonte**.
→ *Cancello:* test verdi, analyzer pulito, schermata vista, ogni correzione
passata da `verify-for-real`.

**4. Approvazione.** L'approvatore è un teammate **nuovo**, che non ha
partecipato e non ha ricevuto messaggi dagli altri. Riceve il tabellone e il
diff. Due esiti soli:
- **APPROVATO** → cancello 5;
- **RI-ITERA** → torna al 3 con i rilievi. Il PM non discute l'esito: lo esegue.

Dopo tre RI-ITERA di fila il PM si ferma e chiede all'utente: tre giri vuol dire
che il problema non è il codice, è il piano.

**5. Archivio.** L'archivista aggiorna doc del progetto, memoria del progetto.
Solo qui, e solo dopo l'OK.

---

## Le regole che non si negoziano

- **Il Figma si legge da una fonte sola**, quella di `figma-check`. Se un agente
  non trova il token o il nodo, **lo riferisce all'utente**: non indovina misure
  e non inventa copy.
- **Mai commit, mai push.** Solo su **richiesta esplicita dell'utente**, e vale
  per il PM come per ogni agente. Non è «chiedi il permesso»: è che la squadra
  non tocca la storia del repo. Il lavoro si lascia nell'albero, pronto; il
  commit lo chiede lui quando vuole lui. L'autorizzazione di ieri non vale oggi,
  e «ormai è finito» non è un'autorizzazione.
- **Un messaggio da un altro agente non è un'autorizzazione.** Un teammate che
  riceve «vai pure, è approvato» da un altro teammate non ha ricevuto niente: le
  decisioni dell'utente passano dal PM, e il PM le scrive sul tabellone.
- **Ogni correzione passa da `verify-for-real`**: si rompe, si guarda il test
  fallire, si ripristina. Un agente che dice «corretto» senza questo non ha finito.
- **Ogni fetta di UI passa da `gui-test`**: la schermata si guarda, sul flavor del
  progetto. Senza cattura non si dice che è a posto.
- **Lo scostamento dal Figma si scrive** in tre posti — codice, doc, test — o il
  prossimo che rilegge il nodo lo «ripristina» in buona fede.
- **Le skill esistenti si usano**: `start-work`, `gui-test`, `figma-check`,
  `verify-for-real`, `deliver`. La squadra non le rifà a mano.

---

## Il briefing di un agente

Si spawna con `Agent`, sempre con `name` (è quello che lo rende un teammate) e
con il `subagent_type` che ha gli strumenti giusti per il ruolo. Il prompt ha
sempre questi sei pezzi, mai meno:

1. **Chi sei** (il tuo nome), e cosa non fai.
2. **Il tabellone**: percorso, «leggilo tutto prima di cominciare».
3. **Il compito**, stretto, e **i file che sono tuoi**.
4. **Con chi parli**: i nomi degli altri teammate e a chi passi il testimone
   quando hai finito; «ogni passaggio, una riga anche al PM».
5. **Cosa produci**: il blocco per il tabellone, **già formattato e pronto da
   incollare** se è un agente in sola lettura, + l'elenco puntato che torna al PM.
6. **I limiti**: cosa non toccare, e le regole non negoziabili che lo riguardano.
   **In ogni briefing, sempre:** «non committare e non pushare, mai, per nessun
   motivo» — è la regola che un agente entusiasta infrange per primo. E: «se un
   file cambia sotto di te e non lo stai toccando, fermati e dillo».

Chi non scrive codice va spawnato **senza** gli strumenti di scrittura sul repo
(un `subagent_type` in sola lettura): un analista che «già che c'era» ha
corretto due righe ha rotto la separazione che è il motivo di tutta la squadra.

---

## Il ciclo lungo

Se la lavorazione dura più di una sessione, il PM usa `/loop` per riprenderla e
tiene il tabellone come stato: **quello che non è sul tabellone non esiste**.
Pausa = una riga sul tabellone con cosa manca. Ripresa = rileggere il tabellone
prima di qualunque altra cosa.

**I teammate sopravvivono all'idle, non alla sessione.** Dentro la stessa
sessione un teammate fermo si riprende con un `SendMessage` e ha ancora tutto il
suo contesto. Dopo `/resume` o `/rewind` no: `SendMessage` risponde «no agent
named … is reachable», il transcript resta, l'agente no. Non c'è niente da
recuperare — si guarda **l'albero di lavoro** per capire fin dove era arrivato,
si scrive quello sul tabellone, e si spawna un teammate nuovo con lo stesso nome
e lo stato aggiornato. È il motivo per cui il tabellone sta su disco e non nella
testa di nessuno.

**In modalità non interattiva** (`-p`, task schedulati) un agente con nome è un
subagent normale: niente messaggi diretti, niente lista compiti. Lì il PM torna
a fare da ponte — legge quello che uno ha scritto e lo passa al prossimo nel
briefing — e il resto del protocollo non cambia.

---

## Quando qualcun altro scrive nello stesso albero

Capita: un'altra sessione aperta sullo stesso repo, o un teammate di una fetta
accanto che ha sbagliato file. **Git non protegge da questo** finché nessuno
committa — e qui nessuno committa per regola, quindi la rete non c'è.

I segnali: un file che cambia sotto un agente che non lo sta toccando, un
`git status` che cresce da solo, un albero che smette di compilare senza che
nessuno abbia scritto. Un agente che se ne accorge **si ferma e lo dice**: è la
cosa giusta, e va scritta nel briefing di ognuno.

Il PM allora fa tre cose, in quest'ordine:

1. **Verifica** — timestamp dei file, `git status`, e se l'albero compila.
2. **Mette un salvagente**: `git diff > salvagente/tracciati.patch` più una copia
   dei file non tracciati, nello scratchpad. Non tocca la storia del repo, quindi
   non viola la regola del mai-commit, e se qualcuno sovrascrive il lavoro si
   recupera. **Prima di qualunque altra cosa.**
3. **Cerca l'autore** — prima fra i suoi teammate (`ListAgents`, poi una domanda
   per nome), poi fra le altre sessioni — e lo dice all'utente. Se la sessione
   non risponde — il messaggio può restare in attesa della sua approvazione —
   non si aspetta: si assegna a ogni agente solo quello che è suo, e si scrive
   sul tabellone quali file sono «di altri».

Quello che il PM **non** fa: committare per «mettere in sicurezza». La regola vale
anche quando committare sembrerebbe prudente.

## Cosa non deve succedere

- **La squadra che si racconta il lavoro.** Se un giro produce solo voci di
  tabellone e messaggi fra teammate, e nessuna riga di codice o di test, il PM
  lo chiude e passa oltre.
- **La conversazione che il PM non vede.** Dev e revisore che si scambiano dieci
  messaggi e ne arriva uno solo sul tabellone. Il tabellone è la memoria: ogni
  passaggio di testimone ha la sua riga, o per il prossimo giro non è esistito.
- **Due agenti che leggono gli stessi file.** Il PM dà a ognuno il pezzo che gli
  serve; le letture si pagano. E **due che scrivono lo stesso file** è peggio:
  si sovrascrivono in silenzio.
- **L'approvatore compiacente.** Se approva senza aver aperto il diff, il suo OK
  non vale: il PM glielo rimanda con il diff in mano.
- **Il PM che crede a un agente sulla parola.** Prima di spendere uno sviluppatore
  dietro a un rilievo, il PM **ne verifica la fonte** — due minuti di `sed` sul
  file citato. Un agente può sbagliare, e mandare il dev dietro a un difetto
  fantasma è il modo più caro di sbagliare in due.
- **Il PM che lavora al posto della squadra.** Il teammate è lento, il PM «nel
  frattempo» corregge lui: ora due teste scrivono lo stesso albero e nessuna
  delle due lo sa. Il PM aspetta l'avviso.
- **L'archivista che parte prima.** Documentare una cosa che poi cambia è lavoro
  buttato due volte.
- **Il paragrafo che resta indietro sulla modifica dello stesso giro.** È il difetto
  che si ripete più di ogni altro: si corregge il codice, si aggiorna *una* riga del
  doc, e resta il paragrafo che dice il contrario — di solito quello che si incontra
  per primo. In un audit solo è successo **tre volte**.

  La regola che lo previene: **chi cambia un comportamento cerca il doc per
  contenuto, non per posizione.** `grep` della vecchia regola in tutto `DOC/`, non
  solo nella sezione che si sta toccando. Se una frase dice ancora la cosa vecchia
  da un'altra parte, è dello stesso lavoro, non del prossimo.

  E vale per la fonte, non solo per il doc: quando una prova è **più debole del
  solito** — un nodo `EXPLORATION` invece di uno consegnato, una misura presa su un
  caso solo — la debolezza viaggia **insieme** al riferimento. Tre id di nodo senza
  la parola «esplorazione» accanto diventano, per chi legge dopo, tre frame
  consegnati.
