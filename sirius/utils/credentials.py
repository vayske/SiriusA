"""
A braindead credentials manager
"""
import json
from os import getcwd
from .tools import create_json

credential_path = getcwd() + '/utils/credentials.json'

create_json(credential_path)

def get_credential(key: str):
    with open(credential_path, 'r') as file:
        credentials = json.load(file)
    value = credentials.get(key)
    if not value:
        value = input(f"'{key}' does not exist, enter value: ")
        credentials[key] = value
        with open(credential_path, 'w') as file:
            json.dump(credentials, file, ensure_ascii=False, sort_keys=True, indent=2)
    return value
