import streamlit as st
import pandas as pd
import time

from view_plans import get_plans_df
from api import get_plans,get_plan,create_project
            
st.subheader("計畫明細")

plan_id=st.selectbox("計畫編號",get_plans_df()["計畫編號"])

plan=get_plan(plan_id)

st.write(f"計畫名稱: {plan['PlanName']}")

# if plan["ApprovalDoc"]:
#     st.write(f"核定文號: {plan['ApprovalDoc']}")
#     current_status="核定"
# else:
#     current_status="提報"
#     st.write("核定文號: 待核定")


