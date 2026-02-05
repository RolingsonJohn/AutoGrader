import time
from pathlib import Path
import logging
import torch
import Config.Config as config
import matplotlib.pyplot as plt
import pandas as pd
from PreEvaluation.FileLoader import FileLoader
from PreEvaluation.CodeClassifier import CodeClassifier
from PreEvaluation.CodeCleanner import CodeCleanner
import matplotlib.pyplot as plt

def plot_growth(results):
    sizes = [r["size"] for r in results]
    tok_times = [r["tokenizer_total"] for r in results]
    ng_times = [r["ngrams_total"] for r in results]

    plt.figure(figsize=(10, 6))
    plt.plot(sizes, tok_times, marker='o', label='Tokenizer')
    plt.plot(sizes, ng_times, marker='s', label='N-Grams')

    plt.xlabel("Número de archivos")
    plt.ylabel("Tiempo total (s)")
    plt.title("Coste computacional empírico de los embeddings")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("./plots/times.png")



def embedding_n_grams(classifier: CodeClassifier, files: dict, ref: str):
    start = time.time()

    codes = {}
    for path, files_list in files.items():
        for file_code in files_list:
            codes.update({file_code : CodeCleanner.remove_comments(file_code)})

    classifier.fit_ngram_vocab(list(codes.values()))
    ref_embedding = classifier.get_ngram_embedding(code=ref)

    end = time.time()
    time_init = end - start
    print(f"\tTiempo de embedding N-Grams = {time_init}")

    results = []
    for file_code, code in codes.items():
        file_embedding = classifier.get_ngram_embedding(code=code)
        euclidean = classifier.euclidean_distance(ref_embedding, file_embedding)
        manhattan = classifier.manhattan_distance(ref_embedding, file_embedding)

        # print(f"Distancias {file_code}:\n\t1. Euclidea:\n\tn-grams: {euclidean}\n\t2. Manhattan\n\tn-grams: {manhattan}")
        
        dot = classifier.dot_product_similitud(ref_embedding, file_embedding)
        cosine = classifier.cosine_similitude(ref_embedding, file_embedding)

        results.append({
            "filename": file_code,
            "euclidean": euclidean,
            "manhattan": manhattan,
            "dot_product": dot,
            "cosine": cosine,
        })

    end = time.time()
    time_cal = end - start
    print(f"\tTiempo de cálculo para n-grams {time_cal}")

    print(f"\tTiempo total n-grams = {time_cal + time_init}")

    return results, time_init, time_cal


def embedding_tokenizer(classifier: CodeClassifier, files: dict, ref: str):

    start = time.time()
    ref_embedding = classifier.get_embedding(code=ref)
    end = time.time()

    time_embedding = end - start
    print(f"\tTiempo de embedding del Tokenizer = {time_embedding}")

    start = time.time()
    results = []
    for path, files_list in files.items():
        for file_code in files_list:
            clean_code = CodeCleanner.remove_comments(file_code)
            file_embedding = classifier.get_embedding(code=clean_code)

            euclidean = classifier.euclidean_distance(ref_embedding, file_embedding)
            manhattan = classifier.manhattan_distance(ref_embedding, file_embedding)

            # print(f"Distancias {file_code}:\n\t1. Euclidea:\n\tTokenizer: {euclidean}\n\t2. Manhattan\n\tTokenizer: {manhattan}")
            
            dot = classifier.dot_product_similitud(ref_embedding, file_embedding)
            cosine = classifier.cosine_similitude(ref_embedding, file_embedding)

            results.append({
                "filename": file_code,
                "euclidean": euclidean,
                "manhattan": manhattan,
                "dot_product": dot,
                "cosine": cosine,
            })
    end = time.time()
    time_cal = end - start
    print(f"\tTiempo de cálculo para tokenizer {time_cal}")

    print(f"\tTiempo total tokenizer = {time_cal + time_embedding}")
    return results, time_embedding, time_cal

def run_timings(classifier, files_dict, ref, subset_size):
    files_flat = [file for files in files_dict.values() for file in files][:subset_size]

    files_subdict = {"subset": files_flat}
   
    # N-Grams
    start = time.time()
    _, t_embed_ng, t_calc_ng = embedding_n_grams(classifier, files_subdict, ref)
    end = time.time()
    t_n = end - start
    
    print(f"Tiempo total n_grams = {t_n}")
    # Tokenizer
    start = time.time()
    _, t_embed_tok, t_calc_tok = embedding_tokenizer(classifier, files_subdict, ref)
    end = time.time()
    t_t = end - start

    print(f"Tiempo total tokenizer = {t_t}")

    return {
        "size": subset_size,
        "tokenizer_total": t_t,
        "ngrams_total": t_n
    }


def collect_results_from_subsets(classifier, ref_path="test/pruebas/ref.py"):
    subset_dirs = [f"subsets/s{i}" for i in range(1, 9)]
    results = []

    ref = FileLoader.load_files(ref_path)

    for subset_path in subset_dirs:
        files_dict = FileLoader.load_files_from_dir(subset_path)

        # Adaptar a formato esperado por `run_timings` (dict con listas de código por "path")
        files_dict_formatted = {subset_path: list(files_dict.values())}

        result = run_timings(classifier, files_dict_formatted, ref, subset_size=len(files_dict))
        results.append(result)

    return results

def main():
    files = FileLoader.files_extraction("pruebas.zip", "test")
    ref = FileLoader.load_files(path="test/pruebas/ref.py")
    classifier = CodeClassifier()
   
    times = collect_results_from_subsets(classifier=classifier)
    plot_growth(times)


    results, time_t, time_t_cal = embedding_tokenizer(classifier=classifier, files=files, ref=ref)
    print(f"\t{time_t + time_t_cal}") 
    # Convertimos a DataFrame para facilitar el análisis
    df = pd.DataFrame(results)

    # Scatter plot: por ejemplo cosine vs euclidean
    plt.figure(figsize=(10, 6))
    plt.scatter(df['cosine'], df['euclidean'], c='blue', alpha=0.6)
    for i, row in df.iterrows():
        plt.text(row['cosine'], row['euclidean'], row['filename'], fontsize=8)
    plt.xlabel("Cosine Similarity")
    plt.ylabel("Euclidean Distance")
    plt.title("Similitud entre códigos")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("./plots/scatter1.png")


    results, time_n_grams, time_n_cal = embedding_n_grams(classifier=classifier, files=files, ref=ref)
    print(f"\t{time_n_grams + time_n_cal}")

    df = pd.DataFrame(results)
    # Scatter plot: por ejemplo cosine vs euclidean
    plt.figure(figsize=(10, 6))
    plt.scatter(df['cosine'], df['euclidean'], c='blue', alpha=0.6)
    for i, row in df.iterrows():
        plt.text(row['cosine'], row['euclidean'], row['filename'], fontsize=8)
    plt.xlabel("Cosine Similarity")
    plt.ylabel("Euclidean Distance")
    plt.title("Similitud entre códigos")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("./plots/scatter2.png")
    
    # plot_embedding_times(time_tokenizer_embed=time_t, time_tokenizer_calc=time_t_cal,
    #     time_ngrams_embed=time_n_grams, time_ngrams_calc=time_n_cal
    # )

if __name__ == '__main__':
   #  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    main()