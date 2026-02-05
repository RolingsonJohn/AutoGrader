from services.System import System
from services.Config import Config

system = System(
    "Fibonacci Sequence",
    "c",
    Config.OLLAMA_MODEL,
    Config.EXE_METHOD,
    api_key="",
    token=None,
    zip_path=None,
    rubric_path=None)
system.sandbox_execution()
