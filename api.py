import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

def get_plans():
    response = requests.get(f"{BASE_URL}/plans/")
    return response.json()

def get_plan(plan_id):
    response = requests.get(f"{BASE_URL}/plans/{plan_id}")
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

#工程

def create_project(project_id,plan_id,project_name,approval_budget,current_status):
    data={
        "ProjectID": project_id,
        "PlanID": plan_id,
        "ProjectName": project_name,
        "ApprovalBudget": approval_budget,
        "CurrentStatus": current_status
    }
    response = requests.post(f"{BASE_URL}/projects/", json=data)
    return response.json()

def get_projects():
    response = requests.get(f"{BASE_URL}/projects/all")
    return response.json()