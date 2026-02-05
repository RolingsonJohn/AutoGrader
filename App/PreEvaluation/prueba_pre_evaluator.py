import re
import math
from sentence_transformers import SentenceTransformer, util


def remove_comments(path: str):
    
    with open(path, 'r', encoding='utf-8') as archivo:
        code = archivo.read()

    extension = path.split('.')[-1]

    match extension:
        case 'c' | 'java':
            code = re.sub(r'(//.*)', '', code)
            code = re.sub(r'(/\*.*\*/)(.*?)', '', code, flags=re.DOTALL)
        case 'py':
            code = re.sub(r'(#.*)', '', code)
            code = re.sub(r'("""|\'\'\')(.*?)', '', code, flags=re.DOTALL)
        case _:
            code = re.sub(r'(#.*|//.*)', '', code)
            code = re.sub(r'("""|\'\'\'|/\*.*\*/)(.*?)', '', code, flags=re.DOTALL)
            
    return code


def embedding_cosine_similitude(texto: str, referencia: str) -> float:
    """
        Calcula la similitud de coseno entre dos textos usando embeddings.
    """
    modelo_embedding = SentenceTransformer("all-MiniLM-L6-v2")

    emb1 = modelo_embedding.encode(texto, convert_to_tensor=True)
    emb2 = modelo_embedding.encode(referencia, convert_to_tensor=True)
    return util.pytorch_cos_sim(emb1, emb2).item()

def entropy_calculus(code: str)-> float:
    if not code:
        return 0
    freq = {char: code.count(char) / len(code) for char in set(code)}
    return -sum(prob * math.log2(prob) for prob in freq.values())