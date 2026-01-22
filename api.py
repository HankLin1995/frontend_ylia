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

def upload_plan_document(plan_id, data, file):
    """上傳計畫PDF文件"""
    response = requests.post(f"{BASE_URL}/plans/{plan_id}/document", data=data, files={"file": file})
    return response.json()

def approve_plan_projects(plan_id, approval_date=None, project_ids=None):
    """批量核定計畫下的專案
    
    Args:
        plan_id: 計畫ID
        approval_date: 核定日期（可選）
        project_ids: 要核定的專案ID列表（可選，若為空則核定所有「提報」狀態的專案）
    """
    data = {}
    if approval_date:
        data["ApprovalDate"] = approval_date
    if project_ids:
        data["ProjectIDs"] = project_ids
    response = requests.patch(f"{BASE_URL}/plans/{plan_id}/projects/approve", json=data)
    return response.json()

def update_plan(plan_id, data, file=None):
    """上傳計畫文件並核定相關專案（組合操作）"""
    # 先上傳文件
    upload_response = upload_plan_document(plan_id, data, file)
    
    # 如果有核定日期或指定專案ID，則批量核定專案
    if "ApprovalDate" in data or "ProjectIDs" in data:
        approval_date = data.get("ApprovalDate")
        project_ids = data.get("ProjectIDs")
        approve_response = approve_plan_projects(plan_id, approval_date, project_ids)
        return {
            "upload": upload_response,
            "approve": approve_response
        }
    
    return upload_response

def get_plan_documents(plan_id):
    """獲取計畫的所有文件歷史記錄"""
    response = requests.get(f"{BASE_URL}/plans/{plan_id}/documents")
    return response.json()

def get_plan_document_file(plan_id, document_id):
    """獲取計畫文件的 PDF 檔案"""
    response = requests.get(f"{BASE_URL}/plans/{plan_id}/documents/{document_id}/file")
    if response.status_code == 200:
        return response.content
    return None

def delete_plan_document(plan_id, document_id):
    """刪除計畫文件並回滾相關專案狀態"""
    response = requests.delete(f"{BASE_URL}/plans/{plan_id}/documents/{document_id}")
    return response.json()

def delete_plan(plan_id):
    response = requests.delete(f"{BASE_URL}/plans/{plan_id}")
    return response.json()

#工程

def create_project(project_id, plan_id, project_name, approval_budget, current_status, workstation=None, td_code=None):
    data = {
        "ProjectID": project_id,
        "PlanID": plan_id,
        "ProjectName": project_name,
        "ApprovalBudget": approval_budget,
        "CurrentStatus": current_status
    }
    
    # 添加可選參數
    if workstation:
        data["Workstation"] = workstation
    if td_code:
        data["TD_CODE"] = td_code
    
    response = requests.post(f"{BASE_URL}/projects/", json=data)
    return response.json()

def get_projects():
    response = requests.get(f"{BASE_URL}/projects/all")
    return response.json()

def get_project(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    return response.json()

def get_projects_by_plan(plan_id):
    """獲取指定計畫下的所有專案"""
    response = requests.get(f"{BASE_URL}/projects/all")
    all_projects = response.json()
    return [p for p in all_projects if p.get("PlanID") == plan_id]

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

def update_project_channel(project_id,channel_name,data):
    response = requests.patch(f"{BASE_URL}/channels/project/{project_id}/channel/{channel_name}", json=data)
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

# 工程編號變更相關 API
def create_project_id_change(project_id, data, file=None):
    """創建工程編號變更記錄"""
    if file:
        files = {"file": file}
        data = {k: v for k, v in data.items() if k != "PDFPath"}
        response = requests.post(f"{BASE_URL}/projects/{project_id}/project-id-changes", data=data, files=files)
    else:
        data = {k: v for k, v in data.items() if k != "PDFPath"}
        response = requests.post(f"{BASE_URL}/projects/{project_id}/project-id-changes", json=data)
    return response.json()

def get_project_id_changes(project_id):
    """獲取指定專案的工程編號變更記錄"""
    response = requests.get(f"{BASE_URL}/projects/{project_id}/project-id-changes")
    return response.json()

def get_all_project_id_changes():
    """獲取所有工程編號變更記錄"""
    response = requests.get(f"{BASE_URL}/projects/project-id-changes/all")
    return response.json()

def delete_project_id_change(project_id, change_id):
    """刪除工程編號變更記錄"""
    response = requests.delete(f"{BASE_URL}/projects/{project_id}/project-id-changes/{change_id}")
    return response.json()

# 工程附件相關 API
def upload_project_attachment(project_id, file, description=None):
    """上傳工程附件"""
    files = {"file": file}
    data = {}
    if description:
        data["Description"] = description
    response = requests.post(f"{BASE_URL}/projects/{project_id}/attachments", data=data, files=files)
    return response.json()

def get_project_attachments(project_id):
    """獲取工程的所有附件"""
    response = requests.get(f"{BASE_URL}/projects/{project_id}/attachments")
    return response.json()

def download_project_attachment(project_id, attachment_id):
    """下載工程附件"""
    response = requests.get(f"{BASE_URL}/projects/{project_id}/attachments/{attachment_id}")
    if response.status_code == 200:
        return response.content
    return None

def delete_project_attachment(project_id, attachment_id):
    """刪除工程附件"""
    response = requests.delete(f"{BASE_URL}/projects/{project_id}/attachments/{attachment_id}")
    return response.json()

# 工程文件記錄相關 API
def create_project_document(project_id, data, file=None):
    """創建工程文件記錄"""
    files = {"file": file} if file else None
    response = requests.post(f"{BASE_URL}/projects/{project_id}/documents", data=data, files=files)
    return response.json()

def get_project_documents(project_id):
    """獲取工程的所有文件記錄"""
    response = requests.get(f"{BASE_URL}/projects/{project_id}/documents")
    return response.json()

def get_all_project_documents():
    """獲取所有工程文件記錄"""
    try:
        response = requests.get(f"{BASE_URL}/projects/documents/all")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []

def update_project_document(project_id, document_id, data, file=None):
    """更新工程文件記錄"""
    files = {"file": file} if file else None
    response = requests.patch(f"{BASE_URL}/projects/{project_id}/documents/{document_id}", data=data, files=files)
    return response.json()

def delete_project_document(project_id, document_id):
    """刪除工程文件記錄"""
    response = requests.delete(f"{BASE_URL}/projects/{project_id}/documents/{document_id}")
    return response.json()

def get_project_document_file(project_id, document_id):
    """獲取工程文件 PDF 檔案"""
    try:
        url = f"{BASE_URL}/projects/{project_id}/documents/{document_id}/file"
        print(f"Fetching PDF from: {url}")
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"PDF content length: {len(response.content)} bytes")
            return response.content
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching document file: {e}")
        import traceback
        traceback.print_exc()
        return None