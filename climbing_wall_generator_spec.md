# Specifica tecnica — Generatore parametrico di parete di arrampicata indoor

## 1. Obiettivo

Realizzare una pipeline Python parametrica in grado di generare automaticamente un modello 3D di una parete di arrampicata indoor composta da tre pannelli consecutivi con inclinazioni differenti.

Il modello sarà utilizzato come base per un'applicazione 3D demo, sviluppata successivamente con Three.js, nella quale sarà possibile posizionare, spostare e ruotare prese di arrampicata.

La parete iniziale NON deve contenere prese di arrampicata.

Deve invece contenere una griglia regolare di fori per il successivo posizionamento delle prese.

---

## 2. Tecnologia

### Linguaggio

Python 3.x.

### Libreria geometrica principale

Utilizzare:

- CadQuery
- OpenCascade, tramite CadQuery

CadQuery deve essere installabile tramite pip e non deve essere richiesto alcun software CAD esterno.

Installazione prevista:

```bash
pip install cadquery
```

Verifica prevista:

```bash
python -c "import cadquery as cq; print(cq.__version__)"
```

La pipeline deve essere completamente eseguibile da Python.

NON utilizzare:

- Blender
- bpy
- OpenSCAD
- FreeCAD
- altri software CAD esterni

---

## 3. Principio architetturale

La geometria deve essere generata inizialmente come solido CAD tramite CadQuery/OpenCascade.

Non costruire direttamente una mesh triangolare manualmente, salvo che sia necessario esclusivamente nella fase finale di esportazione.

Pipeline concettuale:

```text
Parametri
    |
    v
CadQuery / OpenCascade
    |
    +--> pannello 1
    +--> pannello 2
    +--> pannello 3
    +--> raccordo/diedro 1
    +--> raccordo/diedro 2
    |
    v
Unione dei solidi
    |
    v
Generazione griglia fori
    |
    v
Operazione booleana di sottrazione
    |
    v
Solido finale
    |
    +--> STEP
    +--> STL
    +--> OBJ
    +--> GLB/glTF, se supportato dalla pipeline
```

La geometria CAD deve essere considerata la fonte primaria del modello.

---

## 4. Dimensioni generali

La parete è composta da tre pannelli principali.

Ogni pannello ha:

- larghezza: 2.000 mm
- altezza: 20.000 mm
- spessore: 21 mm

Dimensioni complessive nominali:

- larghezza: 6.000 mm
- altezza massima: circa 20.000 mm

Le dimensioni devono essere espresse internamente in millimetri.

---

## 5. Pannelli

I tre pannelli sono disposti consecutivamente lungo la larghezza.

Ordine:

```text
PANNELLO 1 | PANNELLO 2 | PANNELLO 3
```

### Pannello 1

Inclinazione:

```text
80°
```

L'angolo è misurato rispetto al piano orizzontale/pavimento.

Quindi il pannello è inclinato di 10° rispetto alla verticale, con la parte superiore arretrata rispetto alla base.

### Pannello 2

Inclinazione:

```text
90°
```

Il pannello è perfettamente verticale.

### Pannello 3

Inclinazione:

```text
110°
```

Il pannello è strapiombante di 20° rispetto alla verticale.

---

## 6. Sistema di coordinate

Utilizzare il seguente sistema:

- X = larghezza della parete
- Y = profondità
- Z = altezza

La base della parete deve trovarsi a:

```text
Z = 0
```

La parete deve svilupparsi positivamente lungo Z.

Il fronte della parete deve essere orientato verso Y positivo.

L'origine del modello deve essere posizionata indicativamente:

```text
X = centro della parete
Y = piano di riferimento del fronte
Z = 0
```

La convenzione deve essere mantenuta coerente in tutti gli output.

---

## 7. Continuità tra i pannelli

I tre pannelli NON devono semplicemente essere tre solidi separati accostati.

Devono formare una parete strutturalmente continua.

Tra:

```text
Pannello 1 → Pannello 2
```

e:

```text
Pannello 2 → Pannello 3
```

devono essere create superfici/volumi di raccordo che costituiscano i due diedri interni.

I raccordi devono:

- collegare completamente i pannelli;
- avere lo stesso spessore nominale dei pannelli;
- essere parte integrante del modello;
- non lasciare spazi vuoti;
- non lasciare superfici aperte;
- essere inclusi nel solido finale.

La forma del raccordo deve essere geometricamente coerente con i due pannelli che collega.

---

## 8. Diedri

Il modello deve contenere due diedri:

### Diedro 1

Tra pannello 1 (80°) e pannello 2 (90°).

Differenza angolare:

```text
10°
```

### Diedro 2

Tra pannello 2 (90°) e pannello 3 (110°).

Differenza angolare:

```text
20°
```

Il raccordo non deve essere interpretato come una semplice linea di contatto.

Deve essere creato un elemento geometrico continuo che riempia la zona di transizione tra i pannelli.

La soluzione geometrica esatta del raccordo può essere scelta dall'agente, purché rispetti:

1. continuità della superficie;
2. continuità del volume;
3. stesso spessore nominale;
4. assenza di buchi;
5. possibilità di applicare la griglia di fori anche sulla superficie del raccordo.

È preferibile utilizzare una transizione geometrica semplice e robusta piuttosto che una superficie esteticamente complessa.

---

## 9. Spessore

Tutti i pannelli devono avere:

```text
21 mm
```

di spessore.

Anche le parti utilizzate per i raccordi devono essere coerenti con lo spessore della parete.

Il modello finale deve rappresentare un elemento fisico con spessore reale, non una semplice superficie infinitamente sottile.

---

## 10. Fori

La parete deve essere completamente predisposta per l'installazione delle prese di arrampicata.

Devono essere creati fori cilindrici passanti.

Diametro:

```text
11 mm
```

I fori devono attraversare completamente il materiale.

Non devono essere semplici depressioni superficiali.

---

## 11. Griglia dei fori

La distribuzione deve essere regolare.

Passo:

```text
200 mm × 200 mm
```

quindi:

- 200 mm orizzontalmente;
- 200 mm verticalmente.

La griglia deve coprire tutta la superficie utile della parete.

Devono essere forate:

- superficie del pannello 1;
- superficie del pannello 2;
- superficie del pannello 3;
- superfici dei due raccordi/diedri.

---

## 12. Orientamento dei fori

Ogni foro deve essere orientato ortogonalmente alla superficie locale sulla quale viene posizionato.

Pertanto:

- sui pannelli piani il foro è normale al pannello;
- sul pannello verticale il foro è normale al pannello;
- sul pannello strapiombante il foro è normale al pannello;
- sui raccordi il foro deve seguire la normale alla superficie locale.

L'obiettivo è simulare una reale griglia di punti di fissaggio sulla superficie della parete.

---

## 13. Continuità della griglia

La distribuzione dei fori deve essere il più possibile coerente tra pannelli e raccordi.

Non è accettabile avere una griglia regolare sui pannelli ma una zona dei raccordi completamente priva di fori.

La posizione dei fori sui raccordi deve essere calcolata in funzione della superficie del raccordo.

Se la geometria del raccordo rende impossibile mantenere una griglia cartesiana perfettamente uniforme, utilizzare una parametrizzazione coerente con la superficie.

La priorità è:

1. copertura completa;
2. regolarità;
3. orientamento corretto dei fori;
4. continuità visiva della disposizione.

---

## 14. Operazioni booleane

La generazione dei fori deve essere implementata in maniera efficiente.

NON eseguire necessariamente una sequenza di migliaia di operazioni:

```python
wall = wall.cut(hole1)
wall = wall.cut(hole2)
wall = wall.cut(hole3)
...
```

Preferire, quando possibile:

- aggregazione dei cilindri di taglio;
- batch boolean operations;
- suddivisione per pannello;
- suddivisione per superficie;
- altre strategie equivalenti che riducano il numero di operazioni booleane.

La pipeline deve comunque privilegiare la correttezza geometrica rispetto alla velocità.

---

## 15. Numero indicativo di fori

Il numero esatto deve essere determinato automaticamente dal generatore in funzione delle dimensioni e del passo.

Come riferimento, una superficie piana 6 m × 20 m con passo 200 mm contiene circa:

```text
30 × 100 = 3.000
```

posizioni.

Il numero effettivo sarà differente a causa delle inclinazioni e della geometria dei raccordi.

Il codice NON deve utilizzare un numero di fori hard-coded.

---

## 16. Materiale

La parete deve essere bianca.

Non sono necessarie texture nella prima versione.

Creare un materiale denominato:

```text
Wall
```

Colore:

```text
RGB = 255, 255, 255
```

oppure equivalente colore RGB normalizzato:

```text
1.0, 1.0, 1.0
```

Non utilizzare:

- texture diffuse;
- normal map;
- bump map;
- displacement map.

---

## 17. UV

Le UV non sono necessarie per la prima versione se l'output principale è un modello CAD/STL.

Se viene prodotto un formato mesh destinato a Three.js, le UV possono essere generate dove supportato.

La pipeline deve comunque essere strutturata in modo da poter aggiungere texture in futuro senza dover riscrivere la logica geometrica.

---

## 18. Output

La pipeline deve produrre almeno:

```text
output/
    wall.step
    wall.stl
```

### wall.step

Rappresenta il modello CAD parametrico finale.

Deve essere il formato principale per verificare la correttezza geometrica.

### wall.stl

Rappresenta la versione triangolata del modello.

Deve essere utilizzabile per visualizzazione e verifica della mesh.

---

## 19. OBJ

Se CadQuery e le librerie disponibili consentono un'esportazione OBJ affidabile, produrre anche:

```text
output/
    wall.obj
```

L'OBJ deve rappresentare l'intera parete come un unico modello.

Se l'esportazione OBJ diretta da CadQuery non è sufficientemente affidabile, NON implementare una soluzione fragile esclusivamente per soddisfare questo requisito.

In tal caso documentare chiaramente l'alternativa utilizzata.

---

## 20. GLB / glTF

Poiché il modello verrà successivamente utilizzato con Three.js, valutare anche la generazione di:

```text
output/
    wall.glb
```

Il GLB deve essere considerato un output opzionale ma fortemente consigliato.

La pipeline può utilizzare una fase di conversione dalla geometria CadQuery alla mesh triangolare necessaria per il formato glTF/GLB.

Il GLB deve essere ottimizzato per la visualizzazione realtime.

---

## 21. Struttura del progetto

Organizzare il progetto indicativamente in questo modo:

```text
climbing-wall-generator/
│
├── README.md
├── requirements.txt
├── config.py
├── generate_wall.py
├── geometry.py
├── panels.py
├── joints.py
├── holes.py
├── materials.py
├── export.py
├── validation.py
├── utils.py
└── output/
```

La struttura può essere semplificata se l'agente ritiene che alcuni moduli siano inutili, ma deve essere mantenuta una separazione logica tra:

- configurazione;
- geometria;
- foratura;
- validazione;
- esportazione.

---

## 22. Configurazione parametrica

Tutti i parametri geometrici principali devono essere centralizzati.

Esempio:

```python
PANEL_WIDTH = 2000.0       # mm
PANEL_HEIGHT = 20000.0     # mm
PANEL_THICKNESS = 21.0     # mm

PANEL_ANGLES = [
    80.0,
    90.0,
    110.0
]

HOLE_DIAMETER = 11.0       # mm
HOLE_SPACING_X = 200.0     # mm
HOLE_SPACING_Z = 200.0     # mm
```

Il codice principale non deve contenere valori geometrici hard-coded.

---

## 23. Parametri futuri

La struttura deve consentire facilmente di modificare:

- numero di pannelli;
- larghezza pannelli;
- altezza pannelli;
- spessore;
- inclinazione di ogni pannello;
- passo orizzontale dei fori;
- passo verticale dei fori;
- diametro dei fori;
- materiale;
- directory di output.

---

## 24. Validazione geometrica

La pipeline deve includere una fase di validazione automatica.

Devono essere effettuati almeno i seguenti controlli:

1. Il solido finale esiste.
2. Il solido finale non è nullo.
3. Il solido finale è valido secondo le funzionalità disponibili di OpenCascade/CadQuery.
4. I tre pannelli sono presenti.
5. I raccordi sono presenti.
6. La geometria è unita.
7. I fori sono effettivamente passanti.
8. L'output STEP viene creato.
9. L'output STL viene creato.
10. Gli eventuali output OBJ/GLB vengono creati correttamente.

Se una validazione fallisce, lo script deve terminare con un errore esplicito.

---

## 25. Verifica delle dimensioni

La pipeline deve verificare almeno indicativamente:

```text
larghezza pannelli ≈ 2000 mm
altezza pannelli ≈ 20000 mm
spessore ≈ 21 mm
```

e le inclinazioni:

```text
pannello 1 = 80°
pannello 2 = 90°
pannello 3 = 110°
```

Le tolleranze devono essere esplicite nel codice.

---

## 26. Verifica dei fori

Il generatore deve mantenere internamente una rappresentazione delle posizioni dei fori generate.

È consigliato registrare almeno:

```text
numero totale dei fori
numero fori pannello 1
numero fori pannello 2
numero fori pannello 3
numero fori raccordo 1
numero fori raccordo 2
```

Al termine deve essere stampato un riepilogo simile a:

```text
Wall generation completed.

Panels:
  Panel 1: 80°
  Panel 2: 90°
  Panel 3: 110°

Dimensions:
  Panel width: 2000 mm
  Panel height: 20000 mm
  Thickness: 21 mm

Holes:
  Diameter: 11 mm
  Spacing: 200 x 200 mm
  Total: XXXX

Output:
  wall.step
  wall.stl
  wall.obj
  wall.glb
```

Gli output non disponibili devono essere esplicitamente indicati.

---

## 27. Robustezza delle operazioni booleane

Le operazioni booleane devono essere progettate tenendo conto delle possibili problematiche numeriche di OpenCascade.

Evitare, quando possibile:

- facce coincidenti;
- solidi di taglio tangenti alla superficie senza attraversarla;
- geometrie degeneri;
- spessori infinitesimali;
- sovrapposizioni non necessarie.

I cilindri utilizzati per creare i fori devono attraversare completamente il materiale con un piccolo margine oltre lo spessore nominale.

Ad esempio:

```text
lunghezza cilindro > 21 mm
```

in modo da garantire una sottrazione completa.

---

## 28. Mesh STL

L'esportazione STL deve utilizzare una discretizzazione sufficientemente accurata.

Il diametro dei fori deve risultare visivamente circolare e non costituito da pochissimi segmenti.

Il livello di discretizzazione deve essere parametrico o comunque facilmente modificabile.

Non utilizzare una discretizzazione eccessivamente fine se causa inutilmente file enormi.

---

## 29. Performance

La parete contiene potenzialmente circa 3.000 fori.

La pipeline deve quindi evitare strutture inutilmente inefficienti.

È accettabile che la prima generazione richieda tempo significativo.

Non è invece accettabile una soluzione che esegua migliaia di operazioni booleane indipendenti se esiste una strategia equivalente significativamente più efficiente.

Il tempo di generazione deve essere riportato al termine dell'esecuzione.

---

## 30. Logging

Lo script deve produrre messaggi di avanzamento.

Esempio:

```text
[1/7] Creating panels...
[2/7] Creating joints...
[3/7] Unioning wall geometry...
[4/7] Generating hole grid...
[5/7] Applying boolean cuts...
[6/7] Validating geometry...
[7/7] Exporting files...
```

In caso di errore deve essere indicata chiaramente la fase che ha fallito.

---

## 31. README

Il progetto deve includere un README.md contenente:

### Requisiti

Versione Python supportata.

### Installazione

Esempio:

```bash
pip install -r requirements.txt
```

oppure:

```bash
pip install cadquery
```

### Esecuzione

Esempio:

```bash
python generate_wall.py
```

### Output

Spiegare i file generati.

### Configurazione

Spiegare come modificare:

- dimensioni;
- inclinazioni;
- fori;
- output.

### Troubleshooting

Indicare i principali problemi possibili relativi a:

- installazione CadQuery;
- operazioni booleane;
- esportazione;
- tempi di generazione.

---

## 32. Test

Implementare test automatici per le parti che possono essere verificate senza rendering.

I test devono verificare almeno:

- corretta lettura della configurazione;
- corretto numero di pannelli;
- corretta applicazione degli angoli;
- corrette dimensioni nominali;
- corretto passo della griglia;
- corretto diametro dei fori;
- generazione del solido;
- generazione dei file di output.

---

## 33. Criteri di accettazione finali

Il progetto è considerato completato quando:

1. È possibile installare tutte le dipendenze esclusivamente tramite pip.

2. Non è necessario installare Blender o altri programmi CAD.

3. `python generate_wall.py` genera automaticamente il modello.

4. La parete contiene tre pannelli principali.

5. I pannelli hanno dimensione 2.000 × 20.000 mm.

6. Lo spessore nominale è 21 mm.

7. Le inclinazioni sono:
   - 80°
   - 90°
   - 110°

8. I pannelli sono collegati mediante due raccordi/diedri.

9. Non sono presenti spazi vuoti tra i pannelli.

10. I raccordi fanno parte integrante del solido.

11. La superficie della parete è predisposta con fori su tutta la superficie.

12. Il passo nominale della griglia è 200 × 200 mm.

13. Il diametro dei fori è 11 mm.

14. I fori attraversano completamente lo spessore.

15. I fori sono orientati secondo la normale alla superficie locale.

16. La parete non contiene prese di arrampicata.

17. Il materiale è bianco.

18. Il modello principale è un unico solido continuo.

19. La geometria viene validata tramite OpenCascade.

20. Viene generato almeno `wall.step` e `wall.stl`.

21. Viene generato `wall.obj` se la pipeline CadQuery lo consente in maniera affidabile.

22. Viene generato `wall.glb` se la pipeline di conversione disponibile lo consente in maniera affidabile.

23. I parametri geometrici principali sono modificabili senza modificare la logica del generatore.

24. Il progetto contiene README e istruzioni complete di installazione ed esecuzione.

---

## 34. Priorità dei requisiti

In caso di conflitto tra requisiti, utilizzare il seguente ordine di priorità:

1. Correttezza geometrica.
2. Continuità del solido.
3. Correttezza dei fori.
4. Parametricità.
5. Validazione OpenCascade.
6. Compatibilità Three.js.
7. Performance.
8. Qualità estetica.

Non sacrificare la correttezza geometrica per ottenere una maggiore velocità di generazione.

---

## 35. Nota sul modello per la demo

Questo modello è destinato principalmente a una demo software.

Non deve essere considerato un progetto strutturale o costruttivo di una reale parete di arrampicata.

Le dimensioni e lo spessore sono utilizzati per ottenere un modello 3D realistico e coerente per la visualizzazione e per lo sviluppo dell'applicazione.

Non devono essere interpretati come specifiche ingegneristiche per la costruzione fisica di una parete.
