---
name: start-work
description: Avvia una lavorazione da una lista di ticket (Jira, Linear, ClickUp) o da una descrizione. Legge le card e i loro commenti, scrive un piano e si ferma ad aspettare il via libera. Poi esegue il protocollo completo (branch, sviluppo, test, gui-test, cicli di audit, report) senza committare finché non glielo si dice.
---

# Avviare una lavorazione

Si invoca con una lista di ticket, o con una descrizione a parole. Tutto il resto
di questo file è il protocollo: vale anche quando l'utente non lo ripete.

## 1. Capire, prima di pianificare

- **Leggi ogni card e i suoi commenti.** I commenti contengono correzioni di rotta
  che la descrizione non ha: richieste di fix, decisioni prese a voce, nodi Figma.
  Una card letta senza commenti è una card letta a metà.
- **Guarda se è già fatto.** Prima di stimare, controlla il codice: capita che una
  card descriva qualcosa che un altro ha già chiuso. Verificarlo costa un grep e
  cambia il piano.
- I fatti del progetto (ramo base, tracker, simulatore, flavor, file Figma)
  stanno nella documentazione del progetto: `AGENTS.md`, `CLAUDE.md`, la memoria
  di progetto. Leggili, non chiederli. Chiedi solo quello che davvero non c'è.

## 2. Il piano, e poi ci si ferma

Un piano corto: cosa cambia, dove, cosa si rompe, cosa resta da decidere.
**Poi ci si ferma e si aspetta il via libera.** Non toccare il codice prima.

Se durante la lettura emerge una domanda che cambierebbe il piano, falla adesso,
non a metà lavorazione.

## 3. Esecuzione

Branch dal ramo base del progetto, con la convenzione che il repo usa già
(guarda gli ultimi rami: `git for-each-ref --sort=-committerdate refs/remotes`).

Poi, per ogni slice: sviluppo → test → **gui-test sul simulatore** → si itera
finché la schermata non è giusta. Vedi `gui-test` e `figma-check`.

**I casi che non si producono a comando si mockano.** Se una condizione richiede
dati che il backend non dà (un profilo vuoto, una cache scaduta, una rete
assente) si costruisce una pagina mock in un menu di sviluppo, accanto alle altre
del progetto. È anche il modo di far provare il caso a chi non sviluppa.

## 4. I cicli di audit

Audit 1, 2, ... N. Per *audit* si intende rileggere il diff **e** rilanciare test
e gui-test, non solo guardare il codice.

**Ci si ferma quando un giro intero produce solo rilievi cosmetici**: formattazione,
un numero stantio in un doc. È il segnale che la curva è scesa: i primi giri
trovano difetti veri, gli ultimi igiene. Poi un ultimo audit di sicurezza (cosa
finisce su disco, cosa nei log, cosa sopravvive al logout) e un ultimo giro di test.

Ogni correzione va verificata con `verify-for-real`: rompila e guarda il test
fallire prima di tenerla.

## 5. Quando il disegno sembra sbagliato

**Fermati e chiedi prima di implementare.** Non inventare copy né misure, e non
implementare in silenzio la versione che ti sembra giusta.

Ma non bloccare tutto: fai tutto quello che non dipende da quella risposta, tieni
in sospeso il solo pezzo incerto, e chiedi al momento giusto, non a fine turno.
Se l'utente decide di scostarsi dal Figma, **lo scostamento va scritto** (codice,
doc, test) o qualcuno lo "ripristinerà" rileggendo il nodo.

## 6. Chiusura

- **Niente commit e niente push** finché non lo dice l'utente. Vedi `deliver`.
- **Niente commenti sui ticket** se non lo chiede.
- Un report finale: cosa è stato fatto, quali difetti sono emersi e come sono
  stati misurati, cosa resta aperto e cosa aspetta una sua decisione.
