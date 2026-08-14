# Documentazione script - Climbing Wall Generator

Questo progetto implementa un generatore parametrico 3D in Python basato su CadQuery, che crea una parete di arrampicata indoor composta da 3 pannelli con inclinazioni diverse, raccordi continui tra pannelli e griglia di fori passanti.

## Cosa genera lo script

Lo script principale `generate_wall.py` crea una parete unica e continua con:

- 3 pannelli principali in sequenza lungo X;
- inclinazioni nominali 80 deg, 90 deg, 110 deg;
- spessore reale 21 mm;
- 2 zone di raccordo (diedri) tra i pannelli;
- fori passanti diametro 11 mm con passo 200 x 200 mm;
- orientamento dei fori normale alla superficie locale (anche sui raccordi);
- pavimento generico di riferimento da 50 m2 con parete centrata;
- esportazione STEP/STL e OBJ tramite conversione da STL.

## Architettura dei file

- `config.py`: tutti i parametri geometrici e di export centralizzati.
- `geometry.py`: layout parete e costruzione del solido CAD continuo.
- `holes.py`: generazione griglia fori, classificazione per zona, booleane di taglio in batch.
- `validation.py`: validazioni su configurazione, geometria, griglia e output.
- `export.py`: esportazione STEP/STL + conversione STL -> OBJ via trimesh.
- `materials.py`: definizione materiale logico `Wall` colore bianco.
- `generate_wall.py`: orchestrazione pipeline, logging step-by-step, report finale.
- `tests/`: test automatici per parametri e regole geometriche base.

## Come funziona la pipeline

1. Validazione configurazione nominale.
2. Costruzione geometria parete (pannelli + raccordi) con loft di sezioni YZ lungo X.
3. Generazione della griglia fori su tutta la superficie utile.
4. Creazione cilindri di taglio orientati con la normale locale.
5. Boolean cut in batch tramite compound di tutti i cutter.
6. Creazione pavimento e unione con la parete.
7. Orientamento globale del modello con asse Y come altezza.
8. Validazione del solido finale e coerenza griglia.
9. Export file in `output/`.
10. Report finale con conteggio fori per pannello/raccordo e tempo totale.

## Setup ambiente virtuale (venv)

Nella directory del progetto:

```bash
python -m venv .venv
```

Attivazione su Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

Installazione dipendenze:

```bash
pip install -r requirements.txt
```

## Esecuzione

Con venv attivo:

```bash
python generate_wall.py
```

Output minimi attesi:

- `output/wall.step`
- `output/wall.stl`

Output opzionali:

- `output/wall.obj` generato da conversione `output/wall.stl` tramite `trimesh`.
- `output/wall.glb` non generato direttamente in questa versione (richiede conversione mesh esterna affidabile).

## Test automatici

Con venv attivo:

```bash
pytest
```

I test verificano:

- valori nominali di configurazione;
- presenza di 3 pannelli e relativi angoli;
- coerenza della funzione angolo nei tratti piani;
- passo orizzontale/verticale della griglia fori.

## Parametri che puoi modificare

In `config.py`:

- `panel_width`, `panel_height`, `panel_thickness`
- `panel_angles_deg`
- `hole_diameter`, `hole_spacing_x`, `hole_spacing_z`, `hole_margin`
- `joint_width`, `joint_slices`
- `floor_area_m2`, `floor_thickness`, `floor_side_margin`
- `stl_tolerance`, `stl_angular_tolerance`
- `output_dir` e nomi file export

La logica resta invariata: basta cambiare i parametri.

## Note operative

- Unita' interne: millimetri.
- Sistema assi: X larghezza, Y profondita', Z altezza.
- Origine nominale alla base della parete, centrata in X.
- Priorita': correttezza geometrica e continuita' del solido rispetto alla sola velocita'.
