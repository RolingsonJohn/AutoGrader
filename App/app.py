import ollama
from pathlib import Path
import logging
import joblib
import Utils.utils as u
import Config.Config as config
from PreEvaluation.FileLoader import FileLoader
from PreEvaluation.CodeClassifier import CodeClassifier
from PreEvaluation.CodeCleanner import CodeCleanner
from Evaluation.Evaluator import Evaluator
from Evaluation.RubricGenerator import RubricGenerator
from PostEvaluation.MailSender import MailSender


def rag_population():
    pass

def listall():
    print(ollama.list())

def main():

    # --- Carga de datos ---
    clf_model = joblib.load(config.CLF_MODEL)
    files = FileLoader.files_extraction("pruebas.zip", "test")
    ref = FileLoader.load_files(path="test/pruebas/good.c")

    # --- Tratamiento ---
    tags = {"<PLANGUAGE>" : "c", "<FORMAT>" : "Json"}
    system_config = FileLoader.replace_tags(template=FileLoader.load_files(path=f"{Path(__file__).resolve().parent}/resources/system_template.dat"), tags=tags)
    prompt_template = FileLoader.replace_tags(template=FileLoader.load_files(path=f"{Path(__file__).resolve().parent}/resources/prompt_template.dat"), tags=tags)
    
    # --- Pre-Evaluation ---
    classifier = CodeClassifier(model=clf_model)
    rubric_gen = RubricGenerator(system_config=system_config)

    rubrics = rubric_gen.get_rubric(theme="Fibonnacci Sequence")
    ref_embedding = classifier.get_embedding(ref)

    print(rubrics)

    scripts = {}
    for path, files in files.items():
        for file in files:
            clean_code = CodeCleanner.remove_comments(file)
            emb = classifier.get_embedding(clean_code)
            features = [
                classifier.euclidean_distance(ref_embedding, emb),
                classifier.manhattan_distance(ref_embedding, emb),
                classifier.dot_product_similitud(ref_embedding, emb),
                classifier.cosine_similitude(ref_embedding, emb)
            ]

            prediction = classifier.classifier.predict([features])[0]
            if prediction == 1:
                scripts.update({file : clean_code})
    
    print(scripts.keys())
    # --- Evaluation ---
    print("COMIENZA LA EVALUACIÓN-----------------------")
    ev = Evaluator(codes=scripts, rubrics=rubrics, max_threads=config.MAX_THREADS, system_template=system_config, prompt_template=prompt_template)
    results = ev.launch_threads()

    print("---------------------\n\n\n")
    grades = [ev.get("grade") for ev in results]
    feedbacks = [ev.get("error_feedback") for ev in results]
    filenames = [ev.get("name") for ev in results]

    sender = MailSender(endpoint=config.ENDPOINT)
    attchs = []
    for i, (filename, grade, fb) in enumerate(zip(filenames, grades, feedbacks)):
        print(f"Script {filename}, grade = {grade}\nFeedback = {fb}\n\n---------------------")
        for topic, feedback in fb.items():
            print(topic, feedback)
            attchs.append(sender.create_attachment(feedback, f"{topic}.md"))

    # Post-Evaluation
    print("POST-EVALUATION--------------------------------------------")
    sender.authenticate()
    sender.send_email(subject="Corrección", body="Adjunto se encuentra un fichero con el feedback de su código", attch=attchs, to_email="j.a.rolingson@gmail.com")

if __name__ == '__main__':
   #  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    listall()
    #main()