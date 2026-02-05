import docker
import os
import logging
import Config.Config as config
from pathlib import Path

class Sandbox:

    def __init__(self, docker_host = config.DOCKER_HOST, language : str = 'c'):
        self.client = docker.DockerClient(base_url=docker_host)
        self.path = Path(__file__).resolve().parent
        self.prog_lan = language


    def build_image(self, image: str = 'sandbox:1'):
        
        if image not in self.client.images.list():
            try: 
                self.client.images.build(path=self.path, dockerfile=f"{self.path}/Dockerfile", tag=image)
            except docker.errors.BuildError as e:
                logging.error(f"Error al construir la imagen: {e}")
                return None
            except Exception as e:
                logging.error(f"Error al construir la imagen: {e}")
                return None
            
        return image
    

    def create_container(self, image: str = 'sandbox:1'):
        try:
            volumes = {
                f'{self.path.parent}/test': {
                    'bind': '/data',
                    'mode': 'rw'
                }
            }
            container = self.client.containers.run(image=image, name="sanbox_cont", volumes=volumes, command="sleep infinity", detach=True)
            logging.debug(f"Contenedor {container.id} iniciado exitosamente.")
        except Exception as e:
            logging.error(f"Error al iniciar el contenedor: {e}")
            return None
        
        return container
    

    def run_container(self, container):
        results = {}
        find_command = None
        file_extension = None

        if self.language == 'c':
            file_extension = "*.c"
        elif self.language == 'python':
            file_extension = "*.py"
        else:
            logging.error(f"Unsupported language: {self.language}")
            return None

        find_command = f"find /data -type f -name '{file_extension}'"
        logging.debug(f"Finding files with command: {find_command}")

        exit_code_find, output_find = container.exec_run(cmd=find_command, user='sandboxuser')


    def stop_container(self):
        pass