---
name: figma-check
description: Scarica nodo e render dal Figma e li confronta con la schermata vera dell'app, misure comprese. Riconosce il token scaduto in una chiamata sola, e quando il disegno sembra sbagliato si ferma e chiede invece di decidere da solo.
---

# Confrontare con il Figma

## Accesso

Il token personale di Figma sta in una variabile d'ambiente (`FIGMA_TOKEN`), mai
nel repo. La file key sta nella documentazione del progetto. **Un progetto può
avere più file**: chiedere un nodo al file sbagliato risponde `null` senza
spiegare perché, ed è il primo posto dove si perde tempo.

```sh
curl -sH "X-Figma-Token: $FIGMA_TOKEN" "https://api.figma.com/v1/files/$KEY/nodes?ids=123:456"
curl -sH "X-Figma-Token: $FIGMA_TOKEN" "https://api.figma.com/v1/images/$KEY?ids=123:456&format=png&scale=2"
```

Gli id nelle URL usano `-`, nella API `:`. Il render torna un URL a scadenza
breve: scaricalo subito.

**Il token scade.** La firma è `{"status":403,"err":"Token expired"}` su
**qualsiasi** chiamata, `/v1/me` compresa: provala per prima e saprai in un colpo
se è il token o i permessi. Quando è scaduto, non cercare strade alternative:
chiedi all'utente un token nuovo.

## Trovare il nodo

Se hai solo il nome della schermata, scendi per livelli invece di indovinare:
`?depth=1` dà le pagine, `?depth=2` le sezioni, poi i frame dentro la sezione.

## Confrontare

Metti il render accanto alla cattura del simulatore (`gui-test`) e guarda **testi,
misure e ordine**, non l'impressione generale. Per i testi, leggi `characters` dal
nodo: è la fonte, non quello che si legge nel render.

**Attenzione ai testi troncati.** Se un titolo finisce con dei puntini, controlla
`textTruncation`, `maxLines` e la larghezza del riquadro: se non ci sono, i
puntini **li ha scritti il designer** e non è un'elisione. Succede.

## Quando il disegno sembra sbagliato

**Fermati e chiedi prima di implementare.** Non inventare copy né misure, e non
mettere in silenzio la versione che ti sembra giusta.

Non bloccare tutto il resto: implementa quello che non dipende da quella risposta,
tieni in sospeso il pezzo incerto, e chiedi al momento giusto.

Se l'utente decide di scostarsi dal nodo, **scrivilo dove qualcuno lo troverà**:
un commento nel codice con l'id del nodo e la misura, la doc, e un test che
fallisce se torna indietro. Altrimenti il prossimo che rilegge il Figma lo
"ripristina" in buona fede.
