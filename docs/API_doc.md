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
  - `file` (file, 選填): PDF 文件，最大 50MB

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
- **描述**: 更新特定計畫的信息，包括基本資料和相關文件。
- **請求格式**: `multipart/form-data`
- **參數**:
  - `plan_id` (string, 必填): 計畫編號（URL 參數）
  - `PlanID` (string, 必填): 計畫編號
  - `PlanName` (string, 必填): 計畫名稱
  - `Year` (integer, 必填): 年度
  - `FundingSource` (string, 必填): 經費來源
  - `ApprovalDoc` (string, 選填): 核定公文
  - `file` (file, 選填): PDF 文件，僅接受 PDF 格式

- **成功回應** (200):
  ```json
  {
    "PlanID": "TP-2025-001",
    "PlanName": "更新後的計畫",
    "Year": 2026,
    "FundingSource": "地方自籌",
    "ApprovalDoc": "府水防字第1130000000號",
    "PDFPath": "uploads/TP-2025-001_document.pdf",
    "CreateTime": "2025-03-28T10:52:57+08:00"
  }
  ```

- **錯誤回應**:
  - `400`: 請求格式錯誤或檔案類型不符
  - `404`: 計畫不存在

#### 1.5 刪除計畫

- **URL**: `/plans/{plan_id}`
- **方法**: `DELETE`
- **描述**: 刪除特定計畫及其相關文件。
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

工程屬於特定計畫，代表具體的工程項目。

#### 2.1 創建工程

- **URL**: `/projects/`
- **方法**: `POST`
- **描述**: 創建新的工程。
- **請求體** (JSON):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "PlanID": "TP-2025-001",
    "ProjectName": "台北市防洪工程第一期",
    "Workstation": "第一工作站",
    "CurrentStatus": "規劃中"
  }
  ```

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "PlanID": "TP-2025-001",
    "ProjectName": "台北市防洪工程第一期",
    "Workstation": "第一工作站",
    "CurrentStatus": "規劃中",
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `400`: 工程 ID 已存在
  - `404`: 計畫不存在

#### 2.2 獲取工程列表

- **URL**: `/projects/`
- **方法**: `GET`
- **描述**: 獲取所有工程的列表，可以通過計畫 ID 進行篩選。
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
      "Workstation": "第一工作站",
      "CurrentStatus": "規劃中",
      "CreateTime": "2025-03-27T08:48:29.002710"
    }
  ]
  ```

#### 2.3 獲取特定工程

- **URL**: `/projects/{project_id}`
- **方法**: `GET`
- **描述**: 通過工程 ID 獲取特定工程的詳細信息。
- **參數**:
  - `project_id` (string, 必填): 工程編號

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "PlanID": "TP-2025-001",
    "ProjectName": "台北市防洪工程第一期",
    "Workstation": "第一工作站",
    "CurrentStatus": "規劃中",
    "CreateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 工程不存在

#### 2.4 更新工程

- **URL**: `/projects/{project_id}`
- **方法**: `PUT`
- **描述**: 更新特定工程的信息。
- **參數**:
  - `project_id` (string, 必填): 工程編號
  - 請求體 (JSON):
    ```json
    {
      "ProjectID": "PRJ-2025-001",
      "PlanID": "TP-2025-001",
      "ProjectName": "更新後的工程",
      "Workstation": "第二工作站",
      "CurrentStatus": "施工中"
    }
    ```

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "PlanID": "TP-2025-001",
    "ProjectName": "更新後的工程",
    "Workstation": "第二工作站",
    "CurrentStatus": "施工中",
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

### 3. 工程日期總表 (Project Date Summary)

工程日期總表記錄了工程各階段的重要日期。

#### 3.1 創建工程日期總表

- **URL**: `/projects/{project_id}/dates`
- **方法**: `POST`
- **描述**: 為特定工程創建日期總表。
- **參數**:
  - `project_id` (string, 必填): 工程編號
  - 請求體 (JSON):
    ```json
    {
      "ProjectID": "PRJ-2025-001",
      "ComplaintDate": "2025-03-27T08:48:29.002710",
      "SubmissionDate": "2025-03-28T08:48:29.002710",
      "SurveyDate": "2025-03-29T08:48:29.002710",
      "ApprovalDate": "2025-03-30T08:48:29.002710",
      "DraftCompletionDate": "2025-03-31T08:48:29.002710",
      "BudgetApprovalDate": "2025-04-01T08:48:29.002710",
      "TenderDate": "2025-04-02T08:48:29.002710"
    }
    ```

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "ComplaintDate": "2025-03-27T08:48:29.002710",
    "SubmissionDate": "2025-03-28T08:48:29.002710",
    "SurveyDate": "2025-03-29T08:48:29.002710",
    "ApprovalDate": "2025-03-30T08:48:29.002710",
    "DraftCompletionDate": "2025-03-31T08:48:29.002710",
    "BudgetApprovalDate": "2025-04-01T08:48:29.002710",
    "TenderDate": "2025-04-02T08:48:29.002710",
    "UpdateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `400`: 日期總表已存在
  - `404`: 工程不存在

#### 3.2 獲取工程日期總表

- **URL**: `/projects/{project_id}/dates`
- **方法**: `GET`
- **描述**: 獲取特定工程的日期總表。
- **參數**:
  - `project_id` (string, 必填): 工程編號

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "ComplaintDate": "2025-03-27T08:48:29.002710",
    "SubmissionDate": "2025-03-28T08:48:29.002710",
    "SurveyDate": "2025-03-29T08:48:29.002710",
    "ApprovalDate": "2025-03-30T08:48:29.002710",
    "DraftCompletionDate": "2025-03-31T08:48:29.002710",
    "BudgetApprovalDate": "2025-04-01T08:48:29.002710",
    "TenderDate": "2025-04-02T08:48:29.002710",
    "UpdateTime": "2025-03-27T08:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 日期總表不存在

#### 3.3 更新工程日期總表

- **URL**: `/projects/{project_id}/dates`
- **方法**: `PUT`
- **描述**: 更新特定工程的日期總表。
- **參數**:
  - `project_id` (string, 必填): 工程編號
  - 請求體 (JSON):
    ```json
    {
      "ComplaintDate": "2025-04-05T08:48:29.002710",
      "SubmissionDate": "2025-04-06T08:48:29.002710"
    }
    ```

- **成功回應** (200):
  ```json
  {
    "ProjectID": "PRJ-2025-001",
    "ComplaintDate": "2025-04-05T08:48:29.002710",
    "SubmissionDate": "2025-04-06T08:48:29.002710",
    "SurveyDate": "2025-03-29T08:48:29.002710",
    "ApprovalDate": "2025-03-30T08:48:29.002710",
    "DraftCompletionDate": "2025-03-31T08:48:29.002710",
    "BudgetApprovalDate": "2025-04-01T08:48:29.002710",
    "TenderDate": "2025-04-02T08:48:29.002710",
    "UpdateTime": "2025-03-27T09:48:29.002710"
  }
  ```

- **錯誤回應**:
  - `404`: 日期總表不存在

#### 3.4 刪除工程日期總表

- **URL**: `/projects/{project_id}/dates`
- **方法**: `DELETE`
- **描述**: 刪除特定工程的日期總表。
- **參數**:
  - `project_id` (string, 必填): 工程編號

- **成功回應** (200):
  ```json
  {
    "message": "Date summary deleted successfully"
  }
  ```

- **錯誤回應**:
  - `404`: 日期總表不存在

### 4. 審查 (Reviews)

審查記錄了工程的各種審查資訊和金額明細。

#### 4.1 創建審查

- **URL**: `/reviews/`
- **方法**: `POST`
- **描述**: 創建新的審查記錄，包含金額明細。
- **請求體** (JSON):
  ```json
  {
    "ID": "REV-2025-001",
    "ProjectID": "PRJ-2025-001",
    "ReviewStage": "初步設計",
    "Reviewer": "王工程師",
    "ReviewTime": "2025-03-27T08:48:29.002710",
    "amount_details": [
      {
        "ID": "AMT-2025-001",
        "ReviewID": "REV-2025-001",
        "Name": "工程費",
        "Amount": 1000000
      },
      {
        "ID": "AMT-2025-002",
        "ReviewID": "REV-2025-001",
        "Name": "設計費",
        "Amount": 200000
      }
    ]
  }
  ```

- **成功回應** (200):
  ```json
  {
    "ID": "REV-2025-001",
    "ProjectID": "PRJ-2025-001",
    "ReviewStage": "初步設計",
    "Reviewer": "王工程師",
    "ReviewTime": "2025-03-27T08:48:29.002710",
    "amount_details": [
      {
        "ID": "AMT-2025-001",
        "ReviewID": "REV-2025-001",
        "Name": "工程費",
        "Amount": 1000000
      },
      {
        "ID": "AMT-2025-002",
        "ReviewID": "REV-2025-001",
        "Name": "設計費",
        "Amount": 200000
      }
    ]
  }
  ```

- **錯誤回應**:
  - `400`: 審查 ID 已存在
  - `404`: 工程不存在

#### 4.2 獲取審查列表

- **URL**: `/reviews/`
- **方法**: `GET`
- **描述**: 獲取所有審查的列表，可以通過工程 ID 進行篩選。
- **參數**:
  - `skip` (integer, 選填, 預設: 0): 跳過的記錄數
  - `limit` (integer, 選填, 預設: 100): 返回的最大記錄數
  - `project_id` (string, 選填): 工程編號，用於篩選特定工程下的審查

- **成功回應** (200):
  ```json
  [
    {
      "ID": "REV-2025-001",
      "ProjectID": "PRJ-2025-001",
      "ReviewStage": "初步設計",
      "Reviewer": "王工程師",
      "ReviewTime": "2025-03-27T08:48:29.002710",
      "amount_details": [
        {
          "ID": "AMT-2025-001",
          "ReviewID": "REV-2025-001",
          "Name": "工程費",
          "Amount": 1000000
        },
        {
          "ID": "AMT-2025-002",
          "ReviewID": "REV-2025-001",
          "Name": "設計費",
          "Amount": 200000
        }
      ]
    }
  ]
  ```

#### 4.3 獲取特定審查

- **URL**: `/reviews/{review_id}`
- **方法**: `GET`
- **描述**: 通過審查 ID 獲取特定審查的詳細信息。
- **參數**:
  - `review_id` (string, 必填): 審查編號

- **成功回應** (200):
  ```json
  {
    "ID": "REV-2025-001",
    "ProjectID": "PRJ-2025-001",
    "ReviewStage": "初步設計",
    "Reviewer": "王工程師",
    "ReviewTime": "2025-03-27T08:48:29.002710",
    "amount_details": [
      {
        "ID": "AMT-2025-001",
        "ReviewID": "REV-2025-001",
        "Name": "工程費",
        "Amount": 1000000
      },
      {
        "ID": "AMT-2025-002",
        "ReviewID": "REV-2025-001",
        "Name": "設計費",
        "Amount": 200000
      }
    ]
  }
  ```

- **錯誤回應**:
  - `404`: 審查不存在

#### 4.4 更新審查

- **URL**: `/reviews/{review_id}`
- **方法**: `PUT`
- **描述**: 更新特定審查的信息，包括金額明細。
- **參數**:
  - `review_id` (string, 必填): 審查編號
  - 請求體 (JSON):
    ```json
    {
      "ID": "REV-2025-001",
      "ProjectID": "PRJ-2025-001",
      "ReviewStage": "細部設計",
      "Reviewer": "李工程師",
      "ReviewTime": "2025-03-28T08:48:29.002710",
      "amount_details": [
        {
          "ID": "AMT-2025-001",
          "ReviewID": "REV-2025-001",
          "Name": "工程費",
          "Amount": 1200000
        },
        {
          "ID": "AMT-2025-002",
          "ReviewID": "REV-2025-001",
          "Name": "設計費",
          "Amount": 250000
        }
      ]
    }
    ```

- **成功回應** (200):
  ```json
  {
    "ID": "REV-2025-001",
    "ProjectID": "PRJ-2025-001",
    "ReviewStage": "細部設計",
    "Reviewer": "李工程師",
    "ReviewTime": "2025-03-28T08:48:29.002710",
    "amount_details": [
      {
        "ID": "AMT-2025-001",
        "ReviewID": "REV-2025-001",
        "Name": "工程費",
        "Amount": 1200000
      },
      {
        "ID": "AMT-2025-002",
        "ReviewID": "REV-2025-001",
        "Name": "設計費",
        "Amount": 250000
      }
    ]
  }
  ```

- **錯誤回應**:
  - `404`: 審查不存在或工程不存在

#### 4.5 刪除審查

- **URL**: `/reviews/{review_id}`
- **方法**: `DELETE`
- **描述**: 刪除特定審查及其金額明細。
- **參數**:
  - `review_id` (string, 必填): 審查編號

- **成功回應** (200):
  ```json
  {
    "message": "Review deleted successfully"
  }
  ```

- **錯誤回應**:
  - `404`: 審查不存在

## 錯誤處理

API 使用標準的 HTTP 狀態碼來表示請求的結果：

- `200 OK`: 請求成功
- `400 Bad Request`: 請求參數錯誤或資源已存在
- `404 Not Found`: 請求的資源不存在
- `500 Internal Server Error`: 服務器內部錯誤

錯誤回應的格式如下：

```json
{
  "detail": "錯誤信息"
}
```

## 數據模型

### 計畫 (Plan)
- `PlanID`: 計畫編號 (主鍵)
- `Year`: 年度
- `PlanName`: 計畫名稱
- `FundingSource`: 經費來源
- `ApprovalDoc`: 核定公文
- `PDFPath`: 公文PDF儲存路徑
- `CreateTime`: 建立時間

### 工程 (Project)
- `ProjectID`: 工程編號 (主鍵)
- `PlanID`: 計畫編號 (外鍵)
- `ProjectName`: 工程名稱
- `Workstation`: 工作站
- `CurrentStatus`: 目前狀態
- `CreateTime`: 建立時間

### 工程日期總表 (ProjectDateSummary)
- `ProjectID`: 工程編號 (主鍵, 外鍵)
- `ComplaintDate`: 陳情日期
- `SubmissionDate`: 提報日期
- `SurveyDate`: 測設日期
- `ApprovalDate`: 核准日期
- `DraftCompletionDate`: 初稿完成日期
- `BudgetApprovalDate`: 預算書核准日期
- `TenderDate`: 招標日期
- `UpdateTime`: 更新時間

### 審查 (Review)
- `ID`: 審查ID (主鍵)
- `ProjectID`: 工程編號 (外鍵)
- `ReviewStage`: 審查階段
- `Reviewer`: 審查人員
- `ReviewTime`: 審查時間

### 審查金額明細 (ReviewAmountDetail)
- `ID`: 明細ID (主鍵)
- `ReviewID`: 審查ID (外鍵)
- `Name`: 名稱
- `Amount`: 金額
