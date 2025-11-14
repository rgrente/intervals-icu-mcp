# Training Plans - Examples d'utilisation

Ce guide montre comment créer des plans d'entraînement, y ajouter des workouts, et récupérer leurs détails via le serveur MCP Intervals.icu.

## Récupérer les plans avec leurs workouts

La fonction `get_workout_library` retourne maintenant automatiquement tous les détails des workouts (champ `children`) pour chaque plan/dossier:

```json
{
    "data": {
        "folders": [
            {
                "id": 12345,
                "name": "Marathon Training Plan",
                "description": "12-week marathon training plan",
                "num_workouts": 2,
                "start_date": "2024-01-01",
                "duration_weeks": 12,
                "workouts": [
                    {
                        "id": 1001,
                        "name": "Easy Run",
                        "description": "30min Z2 HR",
                        "type": "Run",
                        "duration_seconds": 1800,
                        "training_load": 30,
                        "indoor": false,
                        "color": "blue"
                    },
                    {
                        "id": 1002,
                        "name": "Long Run",
                        "description": "90min easy pace",
                        "type": "Run",
                        "duration_seconds": 5400,
                        "training_load": 75,
                        "indoor": false,
                        "color": "green"
                    }
                ],
                "workouts_count": 2
            }
        ],
        "summary": {
            "total_folders": 1,
            "training_plans": 1,
            "regular_folders": 0,
            "total_workouts": 2
        }
    }
}
```

## Créer un plan d'entraînement

### Plan de base

```python
create_training_plan(
    name="Marathon Training Plan",
    plan_type="PLAN",
    description="12-week marathon training plan",
    start_date="2024-01-01",
    visibility="PRIVATE"
)
```

**Note importante sur les dates**: Si vous ne spécifiez pas de `start_date` pour un plan (`plan_type="PLAN"`), la date de début sera automatiquement définie au prochain lundi. Cela garantit que les plans commencent toujours en début de semaine.

Exemple sans date spécifiée:
```python
create_training_plan(
    name="Marathon Training Plan",
    plan_type="PLAN",
    description="12-week marathon training plan",
    # start_date est automatiquement défini au prochain lundi
    visibility="PRIVATE"
)
```

### Simple dossier de workouts

```python
create_training_plan(
    name="My Workouts",
    plan_type="FOLDER",
    visibility="PRIVATE"
)
```

## Format des descriptions de workouts

⚠️ **IMPORTANT**: Les descriptions de workouts doivent suivre le format Markdown d'Intervals.icu pour être correctement interprétées.

### Règles de formatage

**Important pour le running/trail**:
- **IMPORTANT**: Impossible de mixer pace et HR dans la même séance. Choisir un seul mode pour toute la séance.
- **Pour les séances intensives VMA/intervalles sur terrain plat**: Utiliser le **pace** pour TOUTE la séance (warmup, main set, cooldown)
  * Warmup: `Press lap 15m 60-75% pace` (durée typique: 15m)
  * Main Set: Pace (ex: `100-105% pace`)
  * Cooldown: Pace (ex: `10m 60-70% pace`, durée typique: 10m)
- **Pour toutes les autres séances** (footing, tempo, longue sortie, côtes/trail): Utiliser les **zones HR** pour TOUTE la séance
  * Warmup: `Press lap 15m Z1-Z2 HR` (durée typique: 15m)
  * Main Set: Zones HR (ex: `Z2 HR`, `Z3 HR`, `Z4 HR`)
  * Cooldown: Zones HR (ex: `10m Z1-Z2 HR`, durée typique: 10m)
- JAMAIS de ramp pour le warmup ou cooldown en running/trail.

1. **En-têtes de section** (Warmup/Main Set/Cooldown) sur une ligne séparée
2. **Étapes** commencent par `- `, suivies de:
   - Durée (ex: `5m`, `30s`, `1m30`)
   - Intensité cible:
     - **Cyclisme**: % de FTP (ex: `85%`, `95-105%`)
     - **Course**: Zones HR pour la plupart des séances (ex: `Z2 HR`, `Z3 HR`, `Z4 HR`). Pace pour TOUTE la séance VMA/intervalles intensifs sur plat (ex: `60-75% pace` warmup, `100-105% pace` main set, `60-70% pace` cooldown)
     - **Zones génériques**: ex: `Z2`, `Z3 HR`, `Z2 Pace`
   - Optionnel: cadence (ex: `90rpm`)
   - Optionnel: rampe (ex: `ramp 60-80%`)
3. **Répétitions**: utiliser `Nx` sur sa propre ligne, avant le bloc
4. **Laisser des lignes vides** entre les sections et les répétitions

### Exemples de format Markdown

#### Cyclisme
```
Warmup
- 10m ramp 55-75% FTP 90rpm

Main Set 3x
- 5m 90% FTP 95rpm
- 3m 65% FTP 85rpm

Cooldown
- 10m ramp 75-55% FTP 85rpm
```

#### Course - Footing facile (basé sur HR)
```
Warmup
- Press lap 15m Z1-Z2 HR

Main Set
- 30m Z2 HR

Cooldown
- 10m Z1-Z2 HR
```

#### Course - Tempo (basé sur HR)
```
Warmup
- Press lap 15m Z1-Z2 HR

Main Set
- 30m Z3-Z4 HR

Cooldown
- 10m Z1-Z2 HR
```

#### Course - VMA sur terrain plat (pace pour toute la séance)
```
Warmup
- Press lap 15m 60-75% pace

Main Set 6x
- 3m 100-105% pace
- 2m 70% pace

Cooldown
- 10m 60-70% pace
```

#### Trail/Côtes (basé sur HR)
```
Warmup
- Press lap 15m Z1-Z2 HR

Main Set 5x
- 5m Z4 HR
- 3m Z2 HR

Cooldown
- 10m Z1-Z2 HR
```

## Ajouter des workouts à un plan

### Exemple simple - Workouts de course à pied

```python
add_workouts_to_plan(
    folder_id=12345,
    workouts='''[
        {
            "name": "Easy Run",
            "description": "Warmup\\n- 10m ramp 60-80% pace\\n\\nMain Set\\n- 20m Z2 HR\\n\\nCooldown\\n- 5m cooldown at Z1 pace",
            "type": "Run",
            "moving_time": 2100,
            "day": 1,
            "indoor": false,
            "color": "blue",
            "icu_training_load": 30,
            "targets": ["HR"]
        },
        {
            "name": "Long Run",
            "description": "Warmup\\n- 15m ramp 60-75% pace\\n\\nMain Set\\n- 60m 80-85% pace\\n\\nCooldown\\n- 15m cooldown at Z1-Z2 pace",
            "type": "Run",
            "moving_time": 5400,
            "day": 7,
            "indoor": false,
            "color": "green",
            "icu_training_load": 75
        }
    ]'''
)
```

### Exemple avec workouts structurés - Vélo avec zones de puissance

```python
add_workouts_to_plan(
    folder_id=12345,
    workouts='''[
        {
            "name": "Threshold Intervals",
            "description": "Warmup\\n- 10m ramp 55-75% FTP 90rpm\\n\\nMain Set 4x\\n- 8m 95-105% FTP 95rpm\\n- 2m 55% FTP 85rpm\\n\\nCooldown\\n- 10m ramp 75-55% FTP 85rpm",
            "type": "Ride",
            "moving_time": 3600,
            "day": 3,
            "indoor": true,
            "color": "red",
            "icu_training_load": 85,
            "targets": ["POWER"]
        }
    ]'''
)
```

### Exemple complet - Plan de semaine d'entraînement

```python
add_workouts_to_plan(
    folder_id=12345,
    workouts='''[
        {
            "name": "Recovery Run",
            "description": "Main Set\\n- 30m Z1-Z2 HR",
            "type": "Run",
            "moving_time": 1800,
            "day": 1,
            "icu_training_load": 25,
            "targets": ["HR"]
        },
        {
            "name": "Intervals",
            "description": "Warmup\\n- 15m ramp 60-80% pace\\n\\nMain Set 6x\\n- 3m 100-105% pace\\n- 2m 70% pace\\n\\nCooldown\\n- 10m cooldown at Z1 pace",
            "type": "Run",
            "moving_time": 3600,
            "day": 2,
            "icu_training_load": 65,
            "targets": ["PACE"]
        },
        {
            "name": "Easy Run",
            "description": "Warmup\\n- 10m ramp 60-75% pace\\n\\nMain Set\\n- 25m Z2 HR\\n\\nCooldown\\n- 10m cooldown at Z1 pace",
            "type": "Run",
            "moving_time": 2700,
            "day": 3,
            "icu_training_load": 40,
            "targets": ["HR"]
        },
        {
            "name": "Tempo Run",
            "description": "Warmup\\n- 15m ramp 60-80% pace\\n\\nMain Set\\n- 20m 95-100% pace\\n\\nCooldown\\n- 15m cooldown at Z1-Z2 pace",
            "type": "Run",
            "moving_time": 3000,
            "day": 4,
            "icu_training_load": 55,
            "targets": ["PACE"]
        },
        {
            "name": "Rest Day",
            "description": "Complete rest or light cross-training",
            "type": "Workout",
            "moving_time": 0,
            "day": 5,
            "icu_training_load": 0
        },
        {
            "name": "Easy Run",
            "description": "Main Set\\n- 40m Z2 HR",
            "type": "Run",
            "moving_time": 2400,
            "day": 6,
            "icu_training_load": 35,
            "targets": ["HR"]
        },
        {
            "name": "Long Run",
            "description": "Warmup\\n- 15m ramp 60-75% pace\\n\\nMain Set\\n- 90m 75-80% pace\\n\\nCooldown\\n- 15m cooldown at Z1-Z2 pace",
            "type": "Run",
            "moving_time": 7200,
            "day": 7,
            "icu_training_load": 95,
            "targets": ["HR"]
        }
    ]'''
)
```

## Champs requis pour chaque workout

- `name`: Nom du workout (requis)
- `type`: Type d'activité - "Run", "Ride", "Swim", etc. (requis)
- `moving_time`: Durée en secondes (requis)
- `day`: Jour dans le plan (requis, commence à 1)

## Champs optionnels

- `description`: Description du workout
- `indoor`: true/false (défaut: false)
- `color`: Couleur pour l'affichage ("blue", "green", "red", etc.)
- `icu_training_load`: Charge d'entraînement estimée
- `targets`: Array de cibles - ["HR"], ["POWER"], ["PACE"], ou ["AUTO"]
- `workout_doc`: Structure détaillée du workout avec steps
- `sub_type`: "NONE", "WARMUP", "COOLDOWN", "RACE", "COMMUTE"

## Structure de workout_doc (workouts structurés)

Le champ `workout_doc` permet de créer des workouts avec des segments spécifiques et des zones cibles:

```json
{
    "duration": 3600,
    "steps": [
        {
            "duration": 600,
            "power": {"value": 2, "units": "power_zone"}
        },
        {
            "duration": 1200,
            "hr": {"value": 4, "units": "hr_zone"}
        },
        {
            "duration": 300,
            "pace": {"value": 5, "units": "pace_zone"}
        }
    ]
}
```

### Unités disponibles

- **Power**: `"power_zone"` (zones 1-7), `"watts"`, `"ftp_percent"`
- **Heart Rate**: `"hr_zone"` (zones 1-7), `"bpm"`, `"lthr_percent"`, `"max_hr_percent"`
- **Pace**: `"pace_zone"` (zones 1-7), `"min_per_km"`, `"threshold_pace_percent"`

## Réponse

Les deux outils retournent des réponses JSON avec:

```json
{
    "data": {
        "workouts": [...],
        "summary": {
            "count": 2,
            "total_duration_seconds": 5400,
            "total_training_load": 115
        }
    },
    "analysis": {
        "workouts_created": 2,
        "total_duration_seconds": 5400,
        "total_training_load": 115,
        "folder_id": 12345
    }
}
```
