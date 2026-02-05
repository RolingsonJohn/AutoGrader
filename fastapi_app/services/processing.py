from pathlib import Path
from services.System import System
import logging

logger = logging.getLogger(__name__)


def process_files(
        theme: str,
        prog_lang: str,
        model_name: str,
        agent: str,
        api_key: str,
        token: str,
        zip_path: Path,
        rubric_path: Path):

    system = System(
        theme=theme,
        prog_lang=prog_lang,
        llm_model=model_name,
        agent=agent,
        api_key=api_key,
        token=token,
        zip_path=zip_path,
        rubric_path=rubric_path,
    )
    try:
        # Extract data first to get clf_model, files, and ref
        logger.info(f"Extracting data from {zip_path}")
        clf_model, files, ref = system.data_extraction()
        logger.info(f"Extracted {len(files)} files from archive")

        # Now call preevaluation with required arguments
        logger.info("Starting pre-evaluation (classification)")
        scripts = system.preevaluation(clf_model, files, ref)
        logger.info(
            f"Pre-evaluation complete. Classified scripts: {len(scripts)}")

        if not scripts:
            logger.warning(
                "No scripts passed classification. Aborting evaluation.")
            return None

        logger.info("Starting evaluation")
        results = system.evaluation(scripts)
        logger.info(f"Evaluation complete. Results: {len(results)}")
    except Exception as e:
        logger.error(
            f"Error en la evaluación de los ficheros: {str(e)}", exc_info=True)         
        print(f"Error en la evaluación de los ficheros {e}")
        return None

    try:
        logger.info("Starting post-evaluation (sending feedback)")
        system.postevaluation(results, to_email="j.a.rolingson@gmail.com")
        logger.info("Post-evaluation complete")
    except Exception as e:
        logger.error(
            f"Error en la emisión del feedback a estudiantes: {str(e)}", exc_info=True)         
        print(f"Error en la emisión del feedback a estudiantes {e}")

    return results


def upload_examples():
    pass
