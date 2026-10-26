---
name: deliver
description: Trasforma un albero di lavoro sporco in commit disgiunti e leggibili, con messaggi in inglese. Non pusha mai se non gliel'hanno detto, e se gli si indica un orario committa e pusha davvero a quell'ora.
---

# Consegnare

## Le regole che non cambiano

- **Non pushare mai** se non lo dice l'utente. Il commit si propone, non si dà per
  concesso: l'autorizzazione di ieri non vale oggi.
- **Messaggi in inglese**, conventional commits.
- **Commenti nel codice in inglese**, anche dove il file accanto li ha in
  un'altra lingua.
- **Firme dell'AI nei commit: decide il team, una volta.** Se il team non le
  vuole (`Co-Authored-By`, «Generated with» in commit, PR e note di rilascio),
  rendilo meccanico invece di affidarlo alla memoria: disattiva l'attribuzione
  nelle impostazioni di Claude Code e metti un hook `commit-msg` che rifiuta il
  messaggio se la contiene.

```sh
# .git/hooks/commit-msg
grep -qiE 'co-authored-by:.*(claude|anthropic)|generated with' "$1" \
  && { echo "commit-msg: firma dell'AI nel messaggio"; exit 1; } || exit 0
```

## Prima di committare

1. **Spazza la spazzatura**: `find . -name '._*' -not -path './.git/*' -delete` sui
   volumi ExFAT o di rete, e controlla che non sia finita nell'indice.
2. **Escludi i file locali.** Alcuni progetti hanno modifiche che non vanno mai
   committate (scambi di framework per il simulatore, xcconfig locali). Stanno
   nella documentazione del progetto. Dopo il commit, **verifica che siano
   rimaste fuori**.
3. **Controlla la lingua dei commenti aggiunti**, meccanicamente e non a memoria.
   Esempio per chi lavora in italiano:

```sh
git diff | grep '^+' | grep -vE '^\+\+\+' | sed 's/^+//' | grep -E '^\s*(///|//)' \
  | grep -iE '\b(che|non|della|delle|una|perché|quindi|senza|già|questo|questa)\b'
```

   Se stampa qualcosa, l'hai scritto in italiano. Succede perché la conversazione
   è in italiano e si scrive nella lingua in cui si pensa: il controllo lo prende,
   la buona volontà no.

## Raggruppare

Con molti file modificati, un commit solo è illeggibile. Partiziona in gruppi
**disgiunti**, un tema per commit, e verifica prima di eseguire:

- ogni file modificato sta in esattamente un gruppo;
- nessun gruppo nomina file che non sono cambiati.

Un file toccato da due temi diversi va in un gruppo solo: scegli quello che
racconta il perché, e menziona l'altro nel corpo del messaggio.

## I commit a orario indicato

Se l'utente dice «committa alle 17:54», il commit e il push devono avvenire
**davvero a quell'ora**, non prima con la data riscritta.

Prepara i gruppi e i messaggi, programma l'esecuzione, e **non toccare i file di
quei gruppi** finché non è scattata: il comando aggiunge quello che trova in quel
momento, quindi un'altra modifica nel frattempo finirebbe dentro. Lavora su file
diversi nell'attesa, e verifica il log dopo.

**E non mettere niente in staging nell'attesa.** `git add <percorsi>` seguito da
`git commit -F <file>` committa **tutto l'indice**, non solo i percorsi aggiunti:
il lavoro fatto nel frattempo e messo in staging finirebbe dentro al commit
programmato con un messaggio che non lo riguarda. Prima di ogni orario, controlla
che `git diff --cached --name-only` non stampi niente.

**Verifica dopo, sui commit e non sullo stato di lavoro.** Che un file sia ancora
modificato non dimostra che non sia stato committato prima:
`git log --name-only --format=%h <base>..HEAD | grep '^ios/'` è la domanda giusta.

## Il messaggio

Dice **cosa cambia e perché**, non quali righe. Se la correzione nasce da una
misura, la misura sta nel corpo: è quella che rende il commit utile fra sei mesi.
