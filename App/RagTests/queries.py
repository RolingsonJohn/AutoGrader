import chromadb

def consultar_chromadb(consulta, nombre_coleccion="pdf_chunks", k=5):
    # Conectar con ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")  # Ajusta la ruta según tu configuración
    
    # Obtener la colección
    coleccion = client.get_collection(nombre_coleccion)
    
    # Realizar la consulta
    resultados = coleccion.query(
        query_texts=[consulta],
        n_results=k  # Número de resultados a obtener
    )
    
    return resultados

if __name__ == "__main__":
    consulta = input("Introduce tu consulta: ")
    resultados = consultar_chromadb(consulta)
    
    print("Resultados obtenidos:")
    for i, documento in enumerate(resultados["documents"], 1):
        print(f"{i}. {documento}\n")
