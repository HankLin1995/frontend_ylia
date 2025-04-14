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

def get_project(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    return response.json()

def update_project(project_id,data):
    response = requests.patch(f"{BASE_URL}/projects/{project_id}", json=data)
    return response.json()

#刪除工程
def delete_project(project_id):
    response = requests.delete(f"{BASE_URL}/projects/{project_id}")
    return response.json()

#工作站
def create_workstation(division,station):
    data={
        "Division": division,
        "Name": station
    }
    response = requests.post(f"{BASE_URL}/workstations/", json=data)
    return response.json()

def get_workstations():
    response = requests.get(f"{BASE_URL}/workstations/")
    return response.json()

def create_project_dates(project_id,data):
    response = requests.post(f"{BASE_URL}/projects/{project_id}/dates", json=data)
    return response.json()

def get_project_dates(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}/dates")
    return response.json()

def update_project_dates(project_id,data):
    response = requests.put(f"{BASE_URL}/projects/{project_id}/dates", json=data)
    return response.json()

def get_all_project_dates():
    response = requests.get(f"{BASE_URL}/projects/dates/all")
    return response.json()

#變更紀錄
def create_change_record(project_id, data, file=None):
    if file:
        files = {"file": file}
        # 從 data 中移除 PDFPath，因為它是由後端處理的
        data = {k: v for k, v in data.items() if k != "PDFPath"}
        response = requests.post(f"{BASE_URL}/projects/{project_id}/changes", data=data, files=files)
    else:
        # 從 data 中移除 PDFPath，因為它是由後端處理的
        data = {k: v for k, v in data.items() if k != "PDFPath"}
        response = requests.post(f"{BASE_URL}/projects/{project_id}/changes", json=data)
    return response.json()

def get_project_changes(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}/changes")
    return response.json()

def update_change_record(project_id, change_id, data, file=None):
    files = {"file": file} if file else None
    response = requests.patch(f"{BASE_URL}/projects/{project_id}/changes/{change_id}", data=data)
    return response.json()

def delete_change_record(project_id, change_id):
    response = requests.delete(f"{BASE_URL}/projects/{project_id}/changes/{change_id}")
    return response.json()

def get_all_changes():
    response = requests.get(f"{BASE_URL}/projects/changes/all")
    return response.json()