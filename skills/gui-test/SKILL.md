---
name: gui-test
description: Pilota il simulatore iOS con idb per provare davvero una schermata. Trova gli elementi per etichetta nell'albero di accessibilità, tocca, scorre, scrive e cattura, e legge quello che ha visto invece di darlo per fatto.
---

# Provare sul simulatore

Una schermata non è verificata finché non la si è guardata. Vale a ogni slice di
UI: senza cattura, non si dice che è a posto.

## idb è la strada principale

`idb` parla col simulatore attraverso `idb_companion`: **non muove il cursore del
Mac, non pretende la finestra davanti**, e funziona col simulatore dietro altre
finestre.

```sh
brew tap facebook/fb && brew install idb-companion
pip install fb-idb
```

Accanto a questa skill c'è `sim_drive.py`, che avvolge idb. Copialo in `tool/`
del progetto. Prende il simulatore da `SIM_UDID`, o in mancanza il primo avviato.

## La differenza vera: si cerca per etichetta

`idb ui describe-all` restituisce **l'albero di accessibilità**: etichetta,
ruolo, riquadro in punti logici, abilitato o no. Quindi un pulsante si trova per
nome, invece di ritagliare uno screenshot e rifare i conti sulla scala.

```python
import sim_drive as s
s.tap_label('Impostazioni')           # scorre in giù, poi dall'alto, poi tocca
s.labels()                            # tutto quello che c'è a schermo
s.describe_point(410, 94)             # cosa c'è in un punto, per i controlli senza etichetta
s.shot('/tmp/impostazioni.png')       # la cattura, da guardare
```

Cambia anche **cosa si può affermare**: `Button "Aiuto" a x=382` e nessun
`"Indietro"` è una verifica, non un'occhiata a uno screenshot. Usa l'albero per
le asserzioni e la cattura per l'aspetto.

## Le regole che costano tempo se le ignori

**L'albero contiene solo quello che è impaginato.** In una lista lunga la riga
che serve c'è ma con riquadro nullo finché non la porti a schermo: si scorre
finché il riquadro non è vero. `tap_label` lo fa da sé.

**Un albero letto mentre la lista si muove fa toccare la riga sbagliata.** Dopo un
lancio la lista decelera per un pezzo, e una pausa fissa non basta: `tree()`
rilegge finché due letture non coincidono, e solo allora restituisce. Se un tocco
non ha fatto quello che doveva, **il sospettato numero uno resta questo**. La
verifica è controllare dove sei finito, non fidarsi del valore di ritorno di
`tap_label`, che dice solo che ha toccato qualcosa.

**La durata dello swipe è il gesto, non la velocità.** ~0,1 s è un lancio e manda
la lista in fondo; 0,5 s è un trascinamento di circa quattro righe.

**Le webview sono opache.** Un login in webview espone solo il pulsante nativo
che lo chiude: dentro, l'albero non vede niente. Lì si torna a coordinate e
catture.

## Scrivere testo

**`idb ui text` va bene solo per lettere e cifre.** Manda codici tasto americani,
e un simulatore con un layout diverso li traduce in altro: con il layout
italiano `@` arriva come `”`.

`s.type_text('...')` spezza il testo: i tratti sicuri passano da `idb ui text`,
ogni altro carattere si tocca sulla tastiera a schermo, che ha il layout vero.
Poi **rilegge il campo e solleva un errore se il valore non coincide**. Le
etichette dei tasti che cambiano tastiera dipendono dalla lingua del simulatore:
si impostano con `SIM_KEY_SYMBOLS` e `SIM_KEY_LETTERS`.

Tocca prima il centro **visibile** del campo, non il centro del suo riquadro di
accessibilità: quel riquadro comprende anche l'etichetta, e il suo centro può
cadere sul bordo e lasciare il focus sul campo precedente.

## Prima della build

- **Spazza i file `._*`** se il repo sta su un volume ExFAT o di rete.
- **Controlla se il progetto ha modifiche locali obbligatorie** per girare su
  simulatore: stanno nella documentazione del progetto, di solito uno stash
  «DO NOT PUSH».
- Flavor e target stanno in `.vscode/launch.json` o nella doc del progetto.
- **Profile e release non girano sul simulatore iOS**: per misurare jank o tempi
  in AOT serve un dispositivo vero.

Se ti servono i log di `flutter run`, non usare `simctl terminate`/`launch` per
riavviare: staccano la sessione. Riavvia con `flutter run`.

## Lasciare le cose come le hai trovate

Se per provare hai cambiato uno stato vero (un consenso, un indirizzo, una
preferenza) **rimettilo com'era** e verificalo, anche su un account di prova. E
dillo nel report.

**Non disinstallare l'app** per essere sicuro della build: si porta via sessione e
dati. `flutter run` reinstalla sopra.

## Altro che idb sa fare

`set-location` (GPS finto), `send-notification` (push finte), `record` e `video`
(registrare la sessione), `focus` (portare avanti il simulatore quando serve),
`log`, `add-media`.
