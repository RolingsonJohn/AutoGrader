from celery import Celery
import requests
from services.processing import process_files
from pathlib import Path

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",  # o la URL de tu instancia Redis
    backend="redis://localhost:6379/0"
)

celery_app.conf.task_routes = {
    "tasks.process_files_and_notify": {"queue": "evaluations"},
}


@celery_app.task(name="tasks.process_files_and_notify")
def process_files_and_notify(task_id: int, theme: str, prog_lang: str, model_name: str, agent: str, api_key: str, token: str, zip_path: Path, rubric_path: Path):
    print("Entro en procesamiento")
    
    result = None
    error_occurred = False
    error_message = ""
    
    try:
        result = process_files(theme, prog_lang, model_name, agent, api_key, token, zip_path, rubric_path)
        
        # Check if result is None or empty
        if result is None:
            error_occurred = True
            error_message = "Evaluation returned no results"
            print(f"Error: {error_message}")
    except Exception as e:
        error_occurred = True
        error_message = str(e)
        print(f"Error al procesar la evaluación: {error_message}")
    
    # Notify Django
    try:
        if error_occurred:
            # Send error notification
            error_payload = {"error": error_message}
            response = requests.post(
                f"http://localhost:8000/autograder/task/{task_id}/error/",
                json=error_payload,
                timeout=5
            )
            response.raise_for_status()
            print(f"Tarea {task_id} marcada como error: {response.status_code}")
        else:
            # Send success with results
            payload = {
                "task_id": task_id,
                "result": result
            }
            response = requests.post(
                f"http://localhost:8000/autograder/task/{task_id}/results/",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"Tarea {task_id} marcada como procesada: {response.status_code}")
    except Exception as notify_err:
        print(f"Error notificando a Django: {notify_err}")