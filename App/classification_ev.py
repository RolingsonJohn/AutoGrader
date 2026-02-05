import os
import time
import joblib
import numpy as np
from PreEvaluation.FileLoader import FileLoader
from PreEvaluation.CodeClassifier import CodeClassifier
from PreEvaluation.CodeCleanner import CodeCleanner
from sklearn.cluster import Birch
from collections import defaultdict

def evaluate_with_birch(path_subset: str, ref_code_path: str, n_clusters: int = 2):
    classifier = CodeClassifier()

    # Cargar código de referencia
    ref_code = FileLoader.load_files(ref_code_path)
    ref_embedding = classifier.get_embedding(code=ref_code)

    filenames = []
    features = []

    for filename in os.listdir(path_subset):

        full_path = os.path.join(path_subset, filename)
        clean_code = CodeCleanner.remove_comments(full_path)
        emb = classifier.get_embedding(code=clean_code)

        # Distancias como features
        feats = [
            classifier.euclidean_distance(ref_embedding, emb),
            classifier.manhattan_distance(ref_embedding, emb),
            classifier.dot_product_similitud(ref_embedding, emb),
            classifier.cosine_similitude(ref_embedding, emb)
        ]
        filenames.append(filename)
        features.append(feats)

    X = np.array(features)

    # Entrenar BIRCH
    birch = Birch(n_clusters=n_clusters, threshold=0.02)
    birch.fit(X)
    labels = birch.predict(X)

    # Agrupar por clúster
    clustered_files = defaultdict(list)
    for filename, label in zip(filenames, labels):
        clustered_files[label].append(filename)

    # Mostrar resultados
    print(f"\n📊 Resultados BIRCH (clústeres={n_clusters}):")
    for cluster_id, files in clustered_files.items():
        print(f"\n🧩 Clúster {cluster_id} ({len(files)} archivos):")
        print(files)  # Solo los 5 primeros para no saturar

    return clustered_files

def evaluate_on_subset(path_subset: str, ref_code_path: str, model_path: str = "decision_tree_pre_eval.pkl"):
    classifier = CodeClassifier()
    tree = joblib.load(model_path)
    
    # Cargar código de referencia
    ref_code = FileLoader.load_files(ref_code_path)
    ref_embedding = classifier.get_embedding(code=ref_code)

    accepted = []
    rejected = []

    for filename in os.listdir(path_subset):

        full_path = os.path.join(path_subset, filename)
        code = CodeCleanner.remove_comments(full_path)

        emb = classifier.get_embedding(code)
        features = [
            classifier.euclidean_distance(ref_embedding, emb),
            classifier.cosine_similitude(ref_embedding, emb)
        ]

        prediction = tree.predict([features])[0]
        if prediction == 1:
            accepted.append(filename)
        else:
            rejected.append(filename)

    print(f"✅ Códigos aceptados: {len(accepted)}")
    print(f"❌ Códigos rechazados: {len(rejected)}")
    print("\nEjemplos aceptados:", accepted)
    print("Ejemplos rechazados:", rejected)

    return accepted, rejected

# === Uso ===
start = time.time()
res_t_a, res_t_r = evaluate_on_subset("subsets/s8", "test/pruebas/ref.py")
end = time.time()

print(f"Tiempo de clasificación Árbol de decisión = {end - start}")

start = time.time()
res_b = evaluate_with_birch("subsets/s8", "test/pruebas/ref.py", n_clusters=2)
end = time.time()

print(f"Tiempo de clasificación BIRCH = {end - start}")

res_b_a = res_b.get(0)
print("Ficheros aceptados por Tree pero no por BIRCH: ", end="")
for file in res_t_a:
    if file not in res_b_a:
        print(f"{file} ", end="")

print("\n")