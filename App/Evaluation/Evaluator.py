from pydantic import BaseModel
from App.Evaluation.LLMClient import LLMClient
from threading import Lock, get_ident
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from ollama import Client
import App.Config.Config as config
import os
import re
import time

mutex = Lock()

class StudentsInfo(BaseModel):
    name: str
    grade: float
    error_feedback: str

class Evaluator:

    def __init__(self, codes: dict = {}, rubrics: dict = {}, max_threads: int = 3, 
                 system_template:str = "", prompt_template: str = "", language: str = "c"):
        """
        """
        self.client = LLMClient(exe_mode=config.EXE_METHOD, system_context=system_template)
        self.codes = codes
        self.structure = StudentsInfo
        self.results = []
        self.rubrics = rubrics
        self.max_threads = max_threads
        self.language = language
        self.format = "Json"
        self.system_template = system_template
        self.prompt_template = prompt_template


    def replace_tags(self, code: str, prompt_template: str, system_template: str) -> tuple[str, str]:
        prompt = prompt_template
        system = system_template
        tags = {"<PLANGUAGE>": self.language, "<FORMAT>": self.format, "<CODE>": code}

        for tag, value in tags.items():
            prompt = re.sub(tag, value, prompt)
            system = re.sub(tag, value, system)

        return (prompt, system)


    def zero_shot_prompt(self, filename: str, code: str) -> dict:
        
        # prompt, system_config = self.replace_tags(code, self.prompt_template, self.system_template)
        prompt = re.sub("<CODE>", code, self.prompt_template)
        data = prompt
        for key, rubric in self.rubrics.items():
            criterios = rubric.get("criteria")
            criteria = f'## Criteria {key}\n'
            for criterio in criterios:
                criteria += f'- {criterio}\n'
            
            criteria += f'### Weight = {rubric.get("weight")}'
            data = re.sub("<RUBRIC>", criteria, data)
            data += '\n<RUBRIC>'
        data = re.sub("<RUBRIC>", "", data)

        print(f"Hilo Evaluando: {get_ident()}\nPrompt = \n{data}\n\n")

        with mutex:
            response = self.client.chat(structure=StudentsInfo, prompt=data)
        # response = self.client.chat(
        #     model= self.model,
        #     messages=[
        #         {'role' : 'system', 'content' : system_config},
        #         {'role' : 'user', 'content': data}
        #     ],
        #     format=StudentsInfo.model_json_schema(),
        #     options={'temperature': 0},
        # )

        # response = StudentsInfo.model_validate_json(response.message.content).model_dump()
        response.update({"name" : filename})
        return response


    def cot_prompt(self, filename: str, code: str)-> dict:
        
        #prompt, system_config = self.replace_tags(code, self.prompt_template, self.system_template)
        prompt = re.sub("<CODE>", code, self.prompt_template)
        feedbacks = {}
        grades = []

        for key, rubric in self.rubrics.items():
            criterios = rubric.get("criteria")
            criteria = f'## Criteria {key}\n'
            for criterio in criterios:
                criteria += f'- {criterio}\n'
            
            criteria += f'### Weight = [0.0 - {rubric.get("weight")}]'
            data = re.sub("<RUBRIC>", criteria, prompt)
            
            with mutex:
               response = self.client.chat(structure=StudentsInfo, prompt=data)
               if config.EXE_METHOD == 'google':
                time.sleep(5)
            # with mutex:
            #     response = self.client.chat(
            #         model= config.OLLAMA_MODEL,
            #         messages=[
            #             {'role' : 'system', 'content' : system_config},
            #             {'role' : 'user', 'content': data}
            #         ],
            #         format=StudentsInfo.model_json_schema(),
            #         options={'temperature': 0},
            #     )

            # response = StudentsInfo.model_validate_json(response.message.content).model_dump()
            feedback = response.get("error_feedback")
            grades.append(response.get("grade"))

            feedbacks.update({key : feedback})
            prompt += f"\n# Feedback for {key}\n{feedback}"
            prompt += f"\n## Grade for {key} = {response.get("grade")}/{rubric.get("weight")}"

            print(f"Hilo Evaluando: {get_ident()}\nPrompt = \n{data}\n\n")
        print(f"Fichero {filename}, notas = {grades}")
        #final_grade = sum(grades) / len(grades) if grades else 0.0
        final_grade = sum(grades)

        response.update({"name" : filename})
        response.update({"grade" : final_grade})
        response.update({"error_feedback" : feedbacks})

        return response
    
    def launch_threads(self) -> list[dict]:
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.cot_prompt, filename, code): (filename, code) for filename, code in self.codes.items()}
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
        return self.results
