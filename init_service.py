import os

from dotenv import load_dotenv

def init_env_vars(env_name: str):
    dotenv_path = os.path.join(os.path.dirname(__file__), env_name)
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)
    else:
        raise EnvironmentError('Could not find .env file')