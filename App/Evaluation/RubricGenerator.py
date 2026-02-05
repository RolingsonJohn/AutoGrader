import os
import re
import json
import ollama
from pathlib import Path
import App.Config.Config as config
from pydantic import BaseModel
from App.Evaluation.LLMClient import LLMClient
from typing import List

class Dimension(BaseModel):
	criteria: List[str]
	weight: float


class RubricFormat(BaseModel):
    Functionality: Dimension
    Quality: Dimension
    Efficiency: Dimension
    Logic: Dimension
    Resources: Dimension


class RubricGenerator:

    def __init__(self, system_config: str = ""):
        self.client = LLMClient(exe_mode=config.EXE_METHOD, system_context=system_config)
        self.rubric_path = f"{Path(__file__).parent.parent}/resources/rubrics.json"


    def get_rubric(self, theme: str) -> dict:
        
        if os.path.exists(f"{Path(__file__).parent.parent}/resources/rubrics.json"):
            rubrics = self.load_rubrics()
        else:
            rubrics = self.generate_rubrics(theme= theme)

        return rubrics
    

    def load_rubrics(self) -> dict:

        with open(self.rubric_path, 'r', encoding='utf-8') as file:
            rubric = json.load(file)
        return rubric


    def generate_rubrics(self, theme: str) -> dict:

        prompt = """
# Instruction
You are an expert code evaluator, evaluating code submissions for c programs by your students. Your task is to generate a **detailed evaluation rubric** for the programs that solve the **<THEME>** problem.
This rubric must rate the code on the following dimensions:

1. **Functionality**: Correctness of the algorithm and achievement of the objective.
2. **Quality**: Readability, style, best practices, modularity, and maintainability.
3. **Efficiency**: Proper use of runtime, algorithms and data structures.
4. **Resources**: Proper management of memory, files, input/output, etc.

Each dimension should contain:
- **Clear description of the criteria** to be evaluated.
- **Key points or subcriteria** (ideally 2 to 4 per dimension).
- **Evaluation range** (from 0.0 to 10.0 in total, with weights distributed by criterion).
- A **JSON return format**, structured and ready to be read by a machine.
"""
        prompt = re.sub("<THEME>", theme, prompt)
        response = self.client.chat(structure=RubricFormat, prompt=prompt) 

        print(response)
        with open(self.rubric_path, 'w', encoding='utf-8') as file:
            json.dump(response, file, ensure_ascii=False, indent=4)

        return response
