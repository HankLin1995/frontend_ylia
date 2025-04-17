import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

#計畫

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

def delete_project(project_id):
    response = requests.delete(f"{BASE_URL}/projects/{project_id}")
    return response.json()

# 水路

def create_channel(data):
    response = requests.post(f"{BASE_URL}/channels/", json=data)
    return response.json()

def get_channels():
    response = requests.get(f"{BASE_URL}/channels/")
    return response.json()

def get_channel(channel_id):
    response = requests.get(f"{BASE_URL}/channels/{channel_id}")
    return response.json()

def get_project_channels(project_id):
    response = requests.get(f"{BASE_URL}/channels/project/{project_id}")
    return response.json()

def update_channel(channel_id,data):
    response = requests.patch(f"{BASE_URL}/channels/{channel_id}", json=data)
    return response.json()

def delete_channel(channel_id):
    response = requests.delete(f"{BASE_URL}/channels/{channel_id}")
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

def update_project_date_and_status(project_id, new_status, new_date):
    project_dates = get_project_dates(project_id)
    # st.write(project_dates)
    if "detail" in project_dates:
        # st.warning("查無相關日程內容", icon="⚠️")
        return "查無相關日程內容"
    else:
        # st.write(project_dates)
        # 根據狀態來選擇對應的日期欄位
        date_column = None
        
        if new_status == "撤案":
            date_column = "WithdrawDate"  # 或你可以選擇 WithdrawDate
        elif new_status == "核定":
            date_column = "ApprovalDate"
        elif new_status == "初稿":
            date_column = "DraftCompletionDate"
        elif new_status == "預算書":
            date_column = "BudgetApprovalDate"
        elif new_status == "招標":
            date_column = "TenderDate"
        elif new_status == "決標":
            date_column = "AwardDate"
        else:
            st.warning("未知狀態，無法更新日期", icon="⚠️")
            return "未知狀態，無法更新日期"

        # 更新選擇的日期欄位
        if date_column:
            # 準備更新資料
            data = {
                "ProjectID": project_id,
                date_column: new_date,
            }

            result = update_project_dates(project_id, data)
            # st.write(result)
            print(result)

            data2={
                "CurrentStatus": new_status
            }

            # 更新狀態
            result2 = update_project(project_id, data2)
            # st.write(result2)
            print(result2)