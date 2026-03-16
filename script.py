import zipfile
import os
from collections import defaultdict

# --- CONFIG ---
zip_path = "SmartHomeSPL_V3.zip"   # chemin vers ton fichier
extract_dir = "SmartHomeSPL_V3"    # dossier d'extraction

# --- Extraction ---
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# --- Analyse ---
total_loc = 0
file_metrics = []
feature_metrics = defaultdict(lambda: {"files": set(), "loc": 0, "markers": 0})

for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith((".py", ".yaml", ".yml")):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            # LOC totales du fichier
            loc = sum(1 for l in lines if l.strip())
            total_loc += loc
            file_metrics.append((path, loc))

            # Analyse des annotations
            for i, line in enumerate(lines):
                line_strip = line.strip()
                if line_strip.startswith("#if["):
                    feature = line_strip.replace("#if[", "").replace("]", "")
                    feature_metrics[feature]["files"].add(path)
                    feature_metrics[feature]["markers"] += 1
                elif "#endif" in line_strip:
                    continue
                else:
                    # Ajouter LOC aux features actives
                    for feat in feature_metrics:
                        if f"#if[{feat}]" in "".join(lines[max(0, i-3):i+1]): 
                            feature_metrics[feat]["loc"] += 1

# Résultats globaux
print(f"Nombre de fichiers analysés: {len(file_metrics)}")
print(f"Total LOC: {total_loc}")

# Résultats par feature
for feat, data in feature_metrics.items():
    print(f"- {feat}: LOC={data['loc']}, Fichiers impactés={len(data['files'])}, Markers={data['markers']}")
