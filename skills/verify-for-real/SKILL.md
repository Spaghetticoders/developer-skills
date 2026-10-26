---
name: verify-for-real
description: I riti che trovano i difetti veri. Rompere la correzione per vedere il test fallire, iniettare il guasto invece di dedurlo, contare invece di stimare. Da usare prima di dire che qualcosa è corretto o verificato.
---

# Verificare davvero

Non automatizza niente. È la differenza fra «ho corretto» e «ho verificato», e
nella pratica smentisce più deduzioni di quante ne confermi.

## 1. Rompi la correzione e guarda il test fallire

Un test che passa anche sul codice rotto non vale niente. Per ogni correzione:
`cp` del file, rimetti il comportamento vecchio, lancia i test, **vedili fallire**,
ripristina. Trenta secondi.

Succede davvero che un test passi per il motivo sbagliato: la fixture non aveva
il campo che il filtro richiede, quindi contava zero elementi e l'asserzione era
vera per caso.

## 2. Inietta il guasto, non dedurlo

Quando la conclusione è «se la rete cade succede X», non fermarti al codice:
sostituisci la risposta con un errore, ricostruisci, e guarda.

Costa una build e cambia la conclusione. Un caso reale: dal codice si deduceva
«resta il profilo vecchio»; iniettando l'errore si è visto che **non partivano
affatto** tre caricamenti a valle, e che il pull-to-refresh non recuperava. Cioè
che da quello stato non si usciva senza chiudere l'app.

**Il contatore che fa fallire solo il primo tentativo** (`static int _n; if (++_n == 1) return Error(...)`)
mostra anche il recupero, e serve per le schermate da far vedere.

Tolta la sonda, verifica che non sia rimasto niente: `grep` sul marcatore.

## 3. Conta, non stimare

«Mi sembra che parta due o tre volte» non è una misura. Contali.

Attenzione al doppio conteggio: i logger di rete stampano **richiesta e risposta**,
quindi due righe per chiamata. Un caso reale: sembravano 2-3 catene di chiamate,
contate per endpoint era **una**, e la correzione che stava per essere scritta
non serviva.

## 4. Incrocia con una fonte esterna

Una schermata coerente con sé stessa non prova niente. Confrontala con qualcosa
che sta fuori dall'app: il plist del simulatore, il log di rete, il nodo Figma,
la risposta del backend. Le discrepanze lì sono i difetti veri.

## 5. Enumera gli stati, non correggere il sintomo

Se sbagli lo stesso confine due volte, stai correggendo il caso che hai appena
visto. Apri il file degli stati e coprili tutti: la domanda giusta non è «questo
caso è coperto?» ma «quali sono tutti i casi?».
