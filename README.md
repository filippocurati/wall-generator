# Climbing Wall Generator

Generatore parametrico in Python/CadQuery per una parete indoor a 3 pannelli con raccordi continui, griglia fori passanti e pavimento di riferimento.

## Requisiti

- Python 3.10+
- pip aggiornato

## Installazione

1. Crea il virtual environment nella directory del progetto:

```bash
python -m venv .venv
```

2. Attiva il virtual environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

3. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

## Esecuzione

```bash
python generate_wall.py
```

Lo script stampa le fasi di avanzamento, valida la geometria e salva gli output in `output/`.

## Output

Output garantiti:

- `output/wall.step`
- `output/wall.stl`

Output opzionali:

- `output/wall.obj` (generato tramite conversione mesh STL -> OBJ con `trimesh`)
- `output/wall.glb` (non generato direttamente: non esiste un export GLB nativo affidabile in CadQuery)

## Configurazione

I parametri principali sono in `config.py`:

- dimensioni pannelli (`panel_width`, `panel_height`, `panel_thickness`)
- inclinazioni (`panel_angles_deg`)
- fori (`hole_diameter`, `hole_spacing_x`, `hole_spacing_z`)
- raccordi (`joint_width`, `joint_slices`)
- pavimento (`floor_area_m2`, `floor_thickness`, margini laterali)
- discretizzazione STL (`stl_tolerance`, `stl_angular_tolerance`)
- directory e nomi file output

Valori nominali correnti:

- pannelli larghi 4.000 mm ciascuno
- pannelli spessore 40 mm
- pavimento area 50 m2 con pannelli centrati
- orientamento export con asse Y come asse verticale

## Test

Esegui:

```bash
pytest
```

I test coprono valori nominali di configurazione, angoli pannelli e regolarita' della griglia fori.

## Troubleshooting

- **CadQuery non installabile**: aggiorna `pip`, usa un Python supportato (3.10+), reinstalla nel venv.
- **Boolean cut lenta**: e' normale con migliaia di fori; il generatore usa un compound unico per ridurre il numero di operazioni.
- **OBJ non esportato**: verifica installazione `trimesh` nel venv (`pip show trimesh`) e presenza di `output/wall.stl`.
- **Tempi lunghi o memoria alta**: riduci temporaneamente `joint_slices`, aumenta `stl_tolerance` o usa passo fori maggiore per debug.
