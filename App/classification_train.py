import time
from pathlib import Path
import logging
import torch
import Config.Config as config
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from PreEvaluation.FileLoader import FileLoader
from PreEvaluation.CodeClassifier import CodeClassifier
from PreEvaluation.CodeCleanner import CodeCleanner


def build_feature_vector(embeddings: list[dict], label: int):
    """Convierte la lista de embeddings en X (features) y y (label)"""
    X = []
    y = []
    for emb in embeddings:
        X.append([emb['euclidean'], emb['cosine']])
        y.append(label)
    return X, y


def embedding_n_grams(classifier: CodeClassifier, files: dict, ref: str):

    codes = {}
    for path, files_list in files.items():
        for file_code in files_list:
            codes.update({file_code : CodeCleanner.remove_comments(file_code)})

    classifier.fit_ngram_vocab(list(codes.values()))
    ref_embedding = classifier.get_ngram_embedding(code=ref)

    results = []
    for file_code, code in codes.items():
        file_embedding = classifier.get_ngram_embedding(code=code)
        euclidean = classifier.euclidean_distance(ref_embedding, file_embedding)
        # manhattan = classifier.manhattan_distance(ref_embedding, file_embedding)

        # print(f"Distancias {file_code}:\n\t1. Euclidea:\n\tn-grams: {euclidean}\n\t2. Manhattan\n\tn-grams: {manhattan}")
        
        cosine = classifier.cosine_similitude(ref_embedding, file_embedding)

        results.append({
            "filename": file_code,
            "euclidean": euclidean,
            #"manhattan": manhattan,
            "cosine": cosine,
        })

    return results


def embedding_tokenizer(classifier: CodeClassifier, files: dict, ref: str):

    ref_embedding = classifier.get_embedding(code=ref)

    results = []
    for path, files_list in files.items():
        for file_code in files_list:
            clean_code = CodeCleanner.remove_comments(file_code)
            file_embedding = classifier.get_embedding(code=clean_code)

            euclidean = classifier.euclidean_distance(ref_embedding, file_embedding)
            # manhattan = classifier.manhattan_distance(ref_embedding, file_embedding)

            # print(f"Distancias {file_code}:\n\t1. Euclidea:\n\tTokenizer: {euclidean}\n\t2. Manhattan\n\tTokenizer: {manhattan}")
            
            cosine = classifier.cosine_similitude(ref_embedding, file_embedding)

            results.append({
                "filename": file_code,
                "euclidean": euclidean,
                # "manhattan": manhattan,
                "cosine": cosine,
            })

    return results


def main():
     # === Datos ===
    bad_paths = {
        'binsearch': ['test/binsearch/1_binsearch.c'],
        'pruebas': ['test/pruebas/bad.c', 'test/pruebas/quijote.txt', 'test/pruebas/test.c']
    }

    good_paths = {
        'pruebas': ['test/pruebas/dynamic.c', 'test/pruebas/good.c']
    }

    ref = FileLoader.load_files(path="test/pruebas/good.c")
    classifier = CodeClassifier()

    # === Obtener distancias ===
    bad_embeddings = embedding_tokenizer(classifier=classifier, files=bad_paths, ref=ref)
    good_embeddings = embedding_tokenizer(classifier=classifier, files=good_paths, ref=ref)

    # === Etiquetar ===
    X_bad, y_bad = build_feature_vector(bad_embeddings, label=0)
    X_good, y_good = build_feature_vector(good_embeddings, label=1)

    X = np.array(X_bad + X_good)
    y = np.array(y_bad + y_good)

    # === Entrenar árbol ===
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    tree = DecisionTreeClassifier(max_depth=2, random_state=42)
    tree.fit(X_train, y_train)

    # === Evaluar ===
    y_pred = tree.predict(X_test)
    print(classification_report(y_test, y_pred))

    joblib.dump(tree, "decision_tree_pre_eval.pkl")
    print("Modelo guardado como decision_tree_pre_eval.pkl")
    
if __name__ == '__main__':
   #  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    main()