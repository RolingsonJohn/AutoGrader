import pdfplumber
from transformers import AutoTokenizer, AutoModel
import torch
import chromadb
import numpy as np

def pdf_to_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

pdf_text = pdf_to_text("tema.pdf")

# 2️⃣ Cargar el modelo y tokenizer de embeddings
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 3️⃣ Función para dividir el texto en chunks usando el tokenizer
def chunk_text(text, max_tokens=128):
    tokens = tokenizer.encode(text, truncation=False)  # Tokenizar todo el texto sin truncar
    chunks = [tokens[i : i + max_tokens] for i in range(0, len(tokens), max_tokens)]  # Crear chunks
    return [tokenizer.decode(chunk) for chunk in chunks]  # Decodificar cada chunk a texto

chunks = chunk_text(pdf_text, max_tokens=128)  

# 4️⃣ Función para obtener embeddings
def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()  # Extraemos solo el CLS token

# Generar embeddings para cada fragmento
vectors = [get_embedding(chunk) for chunk in chunks]

# 5️⃣ Guardar en una base de datos vectorial (ChromaDB)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_chunks")

for i, chunk in enumerate(chunks):
    collection.add(
        ids=[str(i)],
        documents=[chunk],
        embeddings=[vectors[i].tolist()]
    )

print("✅ Embeddings generados y almacenados en ChromaDB")
