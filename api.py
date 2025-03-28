import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

def get_plans():
    response = requests.get(f"{BASE_URL}/plans/")
    return response.json()

def create_plan(data,file=None):
    response = requests.post(f"{BASE_URL}/plans/", data=data, files={"file": file})
    return response.json()

def update_plan(plan_id,data,file=None):
    response = requests.post(f"{BASE_URL}/plans/{plan_id}/file", data=data, files={"file": file})
    return response.json()

def delete_plan(plan_id):
    response = requests.delete(f"{BASE_URL}/plans/{plan_id}")
    return response.json()