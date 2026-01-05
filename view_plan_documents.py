import streamlit as st
import pandas as pd
from api import get_plan_documents, get_plan, get_plans, get_plan_document_file, delete_plan_document
import json
from datetime import datetime

st.subheader("📄 核定計畫版本")

# Dialog 函數：顯示 PDF 文件
@st.dialog("📄 查看 PDF 文件", width="large")
def view_pdf_dialog(plan_id, document):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**版本：** {document.get('Version', '')}")
        st.write(f"**核定文號：** {document.get('ApprovalDoc', '無')}")
        st.write(f"**上傳時間：** {document.get('UploadTime', '')[:19] if document.get('UploadTime') else ''}")
    
    with col2:
        # 刪除按鈕
        if st.button("🗑️ 刪除此文件", type="secondary", use_container_width=True):
            if st.session_state.get("confirm_delete") != document["DocumentID"]:
                st.session_state.confirm_delete = document["DocumentID"]
                st.warning("⚠️ 請再次點擊確認刪除")
            else:
                with st.spinner("刪除中..."):
                    result = delete_plan_document(plan_id, document["DocumentID"])
                    
                    # 顯示回滾資訊
                    if result.get("rollback_info"):
                        rollback = result["rollback_info"]
                        if rollback.get("reverted_projects"):
                            st.success(f"✅ 已回滾 {len(rollback['reverted_projects'])} 個專案狀態至「提報」")
                            st.info(f"回滾的專案：{', '.join(rollback['reverted_projects'])}")
                        if rollback.get("cleared_dates"):
                            st.info(f"已清除 {len(rollback['cleared_dates'])} 個專案的核定日期")
                    
                    st.success("✅ 文件已刪除")
                    st.session_state.pop("confirm_delete", None)
                    st.cache_data.clear()
                    st.rerun()
    
    # 顯示核定的專案
    if document.get("ApprovedProjectIDs"):
        st.write("**本次核定的專案：**")
        try:
            project_ids = json.loads(document["ApprovedProjectIDs"])
            st.write(", ".join(project_ids))
        except:
            st.write(document["ApprovedProjectIDs"])
    
    st.divider()
    
    # 獲取並顯示 PDF
    with st.spinner("載入 PDF 文件中..."):
        pdf_content = get_plan_document_file(plan_id, document["DocumentID"])
        
        if pdf_content:
            st.pdf(pdf_content, height=800)
        else:
            st.error("❌ 無法載入 PDF 文件")

# 選擇計畫ID - 只顯示有文件版本的計畫
plans = get_plans()
# 篩選出有文件的計畫
plans_with_documents = []
for plan in plans:
    try:
        documents = get_plan_documents(plan["PlanID"])
        if documents and len(documents) > 0:
            plans_with_documents.append(plan)
    except:
        continue

if not plans_with_documents:
    st.warning("⚠️ 目前沒有任何計畫上傳過文件版本")
    st.stop()

plan_options = {plan["PlanID"]: f"{plan['PlanID']} - {plan['PlanName']}" for plan in plans_with_documents}
selected_plan = st.selectbox("選擇所屬計畫", options=list(plan_options.keys()), format_func=lambda x: plan_options[x])

if selected_plan:
    plan_id = selected_plan
    plan = get_plan(plan_id)
    
    try:
        documents = get_plan_documents(plan_id)
        
        if documents:
            st.toast(f"✅ 找到 {len(documents)} 筆文件記錄")
            
            # 轉換為 DataFrame
            df_data = []
            for doc in documents:
                # 解析核定專案 ID
                approved_projects = ""
                if doc.get("ApprovedProjectIDs"):
                    try:
                        project_ids = json.loads(doc["ApprovedProjectIDs"])
                        approved_projects = ", ".join(project_ids)
                    except:
                        approved_projects = doc["ApprovedProjectIDs"]
                
                # 格式化上傳時間
                upload_time = doc.get("UploadTime", "")
                if upload_time:
                    try:
                        dt = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                        upload_time = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                df_data.append({
                    "版本": doc.get("Version", ""),
                    "核定文號": doc.get("ApprovalDoc", ""),
                    "上傳時間": upload_time,
                    "核定專案數": len(json.loads(doc.get("ApprovedProjectIDs", "[]"))) if doc.get("ApprovedProjectIDs") else 0,
                    "核定專案": approved_projects if approved_projects else "（無）"
                })
            
            df = pd.DataFrame(df_data)
            
            # # 顯示表格
            # st.dataframe(
            #     df,
            #     hide_index=True,
            #     use_container_width=True,
            #     column_config={
            #         "版本": st.column_config.NumberColumn("版本", width="small"),
            #         "核定文號": st.column_config.TextColumn("核定文號", width="medium"),
            #         "上傳時間": st.column_config.TextColumn("上傳時間", width="medium"),
            #         "核定專案數": st.column_config.NumberColumn("核定專案數", width="small"),
            #         "核定專案": st.column_config.TextColumn("核定專案", width="large")
            #     }
            # )
            
            # 顯示文件列表，每個都有查看按鈕
            st.divider()
            st.caption("📊 點擊查看 PDF 文件")
            
            # 使用列來排列按鈕
            cols_per_row = 3
            for idx in range(0, len(documents), cols_per_row):
                cols = st.columns(cols_per_row)
                for col_idx, doc in enumerate(documents[idx:idx+cols_per_row]):
                    with cols[col_idx]:
                        # 顯示文件資訊卡片
                        st.markdown(f"""
                        **版本 {doc.get('Version', '')}**  
                        📝 {doc.get('ApprovalDoc', '無文號')}  
                        🕒 {doc.get('UploadTime', '')[:10] if doc.get('UploadTime') else ''}
                        """)
                        
                        # 查看按鈕
                        if st.button(
                            "📄 查看 PDF", 
                            key=f"view_pdf_{doc['DocumentID']}", 
                            use_container_width=True
                        ):
                            view_pdf_dialog(plan_id, doc)
        else:
            st.warning("⚠️ 該計畫尚無文件記錄")
    
    except Exception as e:
        st.error(f"❌ 載入文件歷史時發生錯誤：{str(e)}")
