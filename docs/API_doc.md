# 工程管理系統 API 文件

## 概述

本文檔提供工程管理系統 API 的詳細說明。API 基於 FastAPI 框架開發，提供計畫、工程、工程日期和審查相關的操作。

**API 基本資訊**:
- 標題: Backend API
- 描述: Backend API for engineering project management
- 版本: 1.0.0
- 基礎 URL: `/`

## 認證

API 目前支援 CORS，允許來自所有來源的請求。

## 資源

### 1. 計畫 (Plans)

計畫是整個系統的基礎單位，每個計畫可以包含多個工程。

#### 1.1 創建計畫

- **URL**: `/plans/`
- **方法**: `POST`
- **描述**: 創建新的計畫，可以選擇上傳相關的 PDF 文件。
- **請求格式**: `multipart/form-data`
- **參數**:
  - `PlanID` (string, 必填): 計畫編號
  - `PlanName` (string, 必填): 計畫名稱
  - `Year` (integer, 必填): 年度
  - `FundingSource` (string, 必填): 經費來源
  - `ApprovalDoc` (string, 必填): 核定公文
  - `file` (file, 選填): PDF 文件，最大 10MB

- **成功回應** (200):
  ```json
  {
    "PlanID": "TP-2025-001",
    "PlanName": "台北市防洪工程",
    "Year": 2025,
    "FundingSource": "中央補助",
    "ApprovalDoc": "府水防字第1120000000號",
    "PDFPath": "/app/app/files/台北市防洪工程_approval.pdf",
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `400`: 檔案類型錯誤或檔案過大
  - `404`: 計畫不存在

#### 1.2 獲取計畫列表

- **URL**: `/plans/`
- **方法**: `GET`
- **描述**: 獲取所有計畫的列表。
- **參數**:
  - `skip` (integer, 選填, 預設: 0): 跳過的記錄數
  - `limit` (integer, 選填, 預設: 100): 返回的最大記錄數

- **成功回應** (200):
  ```json
  [
    {
      "PlanID": "TP-2025-001",
      "PlanName": "台北市防洪工程",
      "Year": 2025,
      "FundingSource": "中央補助",
      "ApprovalDoc": "府水防字第1120000000號",
      "PDFPath": "/app/app/files/台北市防洪工程_approval.pdf",
      "CreateTime": "2025-03-27T08:48:29.002710"
    }
  ]
  ```

#### 1.3 獲取特定計畫

- **URL**: `/plans/{plan_id}`
- **方法**: `GET`
- **描述**: 通過計畫 ID 獲取特定計畫的詳細信息。
- **參數**:
  - `plan_id` (string, 必填): 計畫編號

- **成功回應** (200):
  ```json
  {
    "PlanID": "TP-2025-001",
    "PlanName": "台北市防洪工程",
    "Year": 2025,
    "FundingSource": "中央補助",
    "ApprovalDoc": "府水防字第1120000000號",
    "PDFPath": "/app/app/files/台北市防洪工程_approval.pdf",
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 計畫不存在

#### 1.4 更新計畫

- **URL**: `/plans/{plan_id}`
- **方法**: `PUT`
- **描述**: 更新特定計畫的資訊。
- **請求格式**: `application/json`
- **參數**:
  - `plan_id` (string, 必填): 計畫編號
  - Request Body:
    ```json
    {
      "PlanID": "TP-2025-001",
      "PlanName": "更新後的計畫名稱",
      "Year": 2025,
      "FundingSource": "中央補助",
      "ApprovalDoc": "府水防字第1120000000號"
    }
    ```

- **成功回應** (200):
  ```json
  {
    "PlanID": "TP-2025-001",
    "PlanName": "更新後的計畫名稱",
    "Year": 2025,
    "FundingSource": "中央補助",
    "ApprovalDoc": "府水防字第1120000000號",
    "PDFPath": "/app/app/files/台北市防洪工程_approval.pdf",
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 計畫不存在

#### 1.5 更新計畫檔案

- **URL**: `/plans/{plan_id}/file`
- **方法**: `POST`
- **描述**: 更新特定計畫的 PDF 檔案。
- **請求格式**: `multipart/form-data`
- **參數**:
  - `plan_id` (string, 必填): 計畫編號
  - `ApprovalDoc` (string, 必填): 核定公文
  - `file` (file, 必填): PDF 文件，最大 10MB

- **成功回應** (200):
  ```json
  {
    "PlanID": "TP-2025-001",
    "PlanName": "台北市防洪工程",
    "Year": 2025,
    "FundingSource": "中央補助",
    "ApprovalDoc": "府水防字第1120000000號",
    "PDFPath": "/app/app/files/台北市防洪工程_approval_new.pdf",
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `400`: 檔案類型錯誤或檔案過大
  - `404`: 計畫不存在

#### 1.6 刪除計畫

- **URL**: `/plans/{plan_id}`
- **方法**: `DELETE`
- **描述**: 刪除特定計畫及其相關檔案。
- **參數**:
  - `plan_id` (string, 必填): 計畫編號

- **成功回應** (200):
  ```json
  {
    "message": "Plan deleted successfully"
  }
  ```

- **錯誤回應**:
  - `404`: 計畫不存在

### 2. 工程 (Projects)

工程是計畫下的具體執行項目。

#### 2.1 創建工程

- **URL**: `/projects/`
- **方法**: `POST`
- **描述**: 創建新的工程。
- **請求格式**: `application/json`
- **參數**:
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "PlanID": "TP-2025-001",
    "ProjectName": "台北市防洪工程第一期",
    "Workstation": "WS001",
    "CurrentStatus": "規劃中",
    "ApprovalBudget": 1000000
  }
  ```

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "PlanID": "TP-2025-001",
    "ProjectName": "台北市防洪工程第一期",
    "Workstation": "WS001",
    "CurrentStatus": "規劃中",
    "ApprovalBudget": 1000000,
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `400`: 工程編號已存在
  - `404`: 計畫不存在

#### 2.2 獲取工程列表

- **URL**: `/projects/`
- **方法**: `GET`
- **描述**: 獲取工程列表。
- **參數**:
  - `skip` (integer, 選填, 預設: 0): 跳過的記錄數
  - `limit` (integer, 選填, 預設: 100): 返回的最大記錄數
  - `plan_id` (string, 選填): 計畫編號，用於篩選特定計畫下的工程

- **成功回應** (200):
  ```json
  [
    {
      "ProjectID": "PRJ-2025-001",
      "PlanID": "TP-2025-001",
      "ProjectName": "台北市防洪工程第一期",
      "Workstation": "WS001",
      "CurrentStatus": "規劃中",
      "ApprovalBudget": 1000000,
      "CreateTime": "2025-03-27T08:48:29.002710"
    }
  ]
  ```

#### 2.3 獲取特定工程

- **URL**: `/projects/{project_id}`
- **方法**: `GET`
- **描述**: 獲取特定工程的詳細信息。
- **參數**:
  - `project_id` (string, 必填): 工程編號

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "PlanID": "TP-2025-001",
    "ProjectName": "台北市防洪工程第一期",
    "Workstation": "WS001",
    "CurrentStatus": "規劃中",
    "ApprovalBudget": 1000000,
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 工程不存在

#### 2.4 更新工程

- **URL**: `/projects/{project_id}`
- **方法**: `PUT`
- **描述**: 更新特定工程的資訊。
- **請求格式**: `application/json`
- **參數**:
  - `project_id` (string, 必填): 工程編號
  - Request Body:
    ```json
    {
      "ProjectID": "PRJ-2025-001",
      "PlanID": "TP-2025-001",
      "ProjectName": "更新後的工程名稱",
      "Workstation": "WS001",
      "CurrentStatus": "施工中",
      "ApprovalBudget": 1500000
    }
    ```

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "PlanID": "TP-2025-001",
    "ProjectName": "更新後的工程名稱",
    "Workstation": "WS001",
    "CurrentStatus": "施工中",
    "ApprovalBudget": 1500000,
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 工程不存在或計畫不存在

#### 2.5 刪除工程

- **URL**: `/projects/{project_id}`
- **方法**: `DELETE`
- **描述**: 刪除特定工程。
- **參數**:
  - `project_id` (string, 必填): 工程編號

- **成功回應** (200):
  ```json
  {
    "message": "Project deleted successfully"
  }
  ```

- **錯誤回應**:
  - `404`: 工程不存在

### 3. 工程日期 (Project Dates)

工程日期記錄了工程的各個重要時間點。

#### 3.1 創建工程日期

- **URL**: `/projects/{project_id}/dates`
- **方法**: `POST`
- **描述**: 為特定工程創建日期記錄。
- **請求格式**: `application/json`
- **參數**:
  - `project_id` (string, 必填): 工程編號
  - Request Body:
    ```json
    {
      "ProjectID": "PRJ-2025-001",
      "ComplaintDate": "2025-01-01T00:00:00",
      "SubmissionDate": "2025-02-01T00:00:00",
      "SurveyDate": "2025-03-01T00:00:00",
      "ApprovalDate": "2025-04-01T00:00:00",
      "DraftCompletionDate": "2025-05-01T00:00:00",
      "BudgetApprovalDate": "2025-06-01T00:00:00",
      "TenderDate": "2025-07-01T00:00:00"
    }
    ```

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "ComplaintDate": "2025-01-01T00:00:00",
    "SubmissionDate": "2025-02-01T00:00:00",
    "SurveyDate": "2025-03-01T00:00:00",
    "ApprovalDate": "2025-04-01T00:00:00",
    "DraftCompletionDate": "2025-05-01T00:00:00",
    "BudgetApprovalDate": "2025-06-01T00:00:00",
    "TenderDate": "2025-07-01T00:00:00",
    "UpdateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `400`: 日期記錄已存在
  - `404`: 工程不存在

#### 3.2 獲取工程日期

- **URL**: `/projects/{project_id}/dates`
- **方法**: `GET`
- **描述**: 獲取特定工程的日期記錄。
- **參數**:
  - `project_id` (string, 必填): 工程編號

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "ComplaintDate": "2025-01-01T00:00:00",
    "SubmissionDate": "2025-02-01T00:00:00",
    "SurveyDate": "2025-03-01T00:00:00",
    "ApprovalDate": "2025-04-01T00:00:00",
    "DraftCompletionDate": "2025-05-01T00:00:00",
    "BudgetApprovalDate": "2025-06-01T00:00:00",
    "TenderDate": "2025-07-01T00:00:00",
    "UpdateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 日期記錄不存在

#### 3.3 更新工程日期

- **URL**: `/projects/{project_id}/dates`
- **方法**: `PUT`
- **描述**: 更新特定工程的日期記錄。
- **請求格式**: `application/json`
- **參數**:
  - `project_id` (string, 必填): 工程編號
  - Request Body:
    ```json
    {
      "ComplaintDate": "2025-01-15T00:00:00",
      "SubmissionDate": "2025-02-15T00:00:00",
      "SurveyDate": "2025-03-15T00:00:00",
      "ApprovalDate": "2025-04-15T00:00:00",
      "DraftCompletionDate": "2025-05-15T00:00:00",
      "BudgetApprovalDate": "2025-06-15T00:00:00",
      "TenderDate": "2025-07-15T00:00:00"
    }
    ```

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "ComplaintDate": "2025-01-15T00:00:00",
    "SubmissionDate": "2025-02-15T00:00:00",
    "SurveyDate": "2025-03-15T00:00:00",
    "ApprovalDate": "2025-04-15T00:00:00",
    "DraftCompletionDate": "2025-05-15T00:00:00",
    "BudgetApprovalDate": "2025-06-15T00:00:00",
    "TenderDate": "2025-07-15T00:00:00",
    "UpdateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 日期記錄不存在

#### 3.4 刪除工程日期

- **URL**: `/projects/{project_id}/dates`
- **方法**: `DELETE`
- **描述**: 刪除特定工程的日期記錄。
- **參數**:
  - `project_id` (string, 必填): 工程編號

- **成功回應** (200):
  ```json
  {
    "message": "Date summary deleted successfully"
  }
  ```

- **錯誤回應**:
  - `404`: 日期記錄不存在

### 4. 工作站 (Workstations)

工作站用於管理工程的執行單位。

#### 4.1 創建工作站

- **URL**: `/workstations/`
- **方法**: `POST`
- **描述**: 創建新的工作站。
- **請求格式**: `application/json`
- **參數**:
  ```json
  {
    "ID": "WS001",
    "Name": "第一工作站",
    "Division": "台北分處"
  }
  ```

- **成功回應** (200):
  ```json
  {
    "ID": "WS001",
    "Name": "第一工作站",
    "Division": "台北分處"
  }
  ```

- **錯誤回應**:
  - `400`: 工作站編號已存在

#### 4.2 獲取工作站列表

- **URL**: `/workstations/`
- **方法**: `GET`
- **描述**: 獲取工作站列表。
- **參數**:
  - `skip` (integer, 選填, 預設: 0): 跳過的記錄數
  - `limit` (integer, 選填, 預設: 100): 返回的最大記錄數

- **成功回應** (200):
  ```json
  [
    {
      "ID": "WS001",
      "Name": "第一工作站",
      "Division": "台北分處"
    }
  ]
  ```

#### 4.3 獲取特定工作站

- **URL**: `/workstations/{workstation_id}`
- **方法**: `GET`
- **描述**: 獲取特定工作站的詳細信息。
- **參數**:
  - `workstation_id` (string, 必填): 工作站編號

- **成功回應** (200):
  ```json
  {
    "ID": "WS001",
    "Name": "第一工作站",
    "Division": "台北分處"
  }
  ```

- **錯誤回應**:
  - `404`: 工作站不存在

#### 4.4 更新工作站

- **URL**: `/workstations/{workstation_id}`
- **方法**: `PUT`
- **描述**: 更新特定工作站的資訊。
- **請求格式**: `application/json`
- **參數**:
  - `workstation_id` (string, 必填): 工作站編號
  - Request Body:
    ```json
    {
      "ID": "WS001",
      "Name": "更新後的工作站",
      "Division": "新北分處"
    }
    ```

- **成功回應** (200):
  ```json
  {
    "ID": "WS001",
    "Name": "更新後的工作站",
    "Division": "新北分處"
  }
  ```

- **錯誤回應**:
  - `404`: 工作站不存在

#### 4.5 刪除工作站

- **URL**: `/workstations/{workstation_id}`
- **方法**: `DELETE`
- **描述**: 刪除特定工作站。如果工作站正在被工程使用，則無法刪除。
- **參數**:
  - `workstation_id` (string, 必填): 工作站編號

- **成功回應** (200):
  ```json
  {
    "message": "Workstation deleted successfully"
  }
  ```

- **錯誤回應**:
  - `400`: 工作站正在被工程使用
  - `404`: 工作站不存在
