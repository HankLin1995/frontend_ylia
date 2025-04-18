from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException

from dotenv import load_dotenv
import os

load_dotenv()

AD_SERVER_NAME = os.getenv("AD_SERVER_NAME")
AD_DOMAIN=os.getenv("AD_DOMAIN")
AD_ADMIN_USER=os.getenv("AD_ADMIN_USER")
AD_ADMIN_PASSWORD=os.getenv("AD_ADMIN_PASSWORD")
BASE_DN=os.getenv("BASE_DN")

def check_ad_credentials(username, password):
    # 設定值（從你的 C# 註解轉換過來）
    user_upn = f"{username}@{AD_DOMAIN}"

    try:
        print(f"🔐 嘗試用 {user_upn} 登入 AD 伺服器 {AD_SERVER_NAME} ...")

        server = Server(AD_SERVER_NAME, get_info=ALL)
        conn = Connection(server, user=user_upn, password=password, authentication='SIMPLE', auto_bind=True)

        print("✅ 登入成功！")
        conn.unbind()
        return True

    except LDAPException as e:
        print(f"❌ LDAP 驗證錯誤: {e}")
        return False
    except Exception as ex:
        print(f"❌ 其他錯誤: {ex}")
        return False

def get_user_info_one(s_type, s_data):

    try:
        print(f"🔍 查詢條件: ({s_type} = {s_data})")

        # 建立連線
        server = Server(AD_SERVER_NAME, get_info=ALL)
        conn = Connection(server, user=AD_ADMIN_USER, password=AD_ADMIN_PASSWORD,authentication='SIMPLE', auto_bind=True)

        # 建立搜尋 Filter
        search_filter = f"(&(objectCategory=user)({s_type}={s_data}))"

        # 執行搜尋
        conn.search(
            search_base=BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=[
                'displayName',
                'description',
                'userPrincipalName',
                'sAMAccountName',
                'distinguishedName'
            ]
        )

        if not conn.entries:
            print("❌ 查無此人")
            return None

        entry = conn.entries[0]

        # 回傳模擬 C# DataTable 的字典
        result = {
            'USR_NAME': entry.displayName.value or '',
            'TITLE': entry.description.value or '',
            'EMAIL': entry.userPrincipalName.value or '',
            'DP_STR': entry.distinguishedName.value or ''
        }

        conn.unbind()
        return result

    except LDAPException as e:
        print(f"❌ LDAP 錯誤: {e}")
        return None
    except Exception as ex:
        print(f"❌ 其他錯誤: {ex}")
        return None

def parse_dn(dn):
    # 分割 DN，取得各個層次的資訊
    parts = dn.split(',')
    
    user_name = None
    ou_list = []
    dc_list = []
    
    for part in parts:
        if part.startswith('CN='):
            user_name = part.replace('CN=', '')
        elif part.startswith('OU='):
            ou_list.append(part.replace('OU=', ''))
        elif part.startswith('DC='):
            dc_list.append(part.replace('DC=', ''))
    
    # 返回解析結果
    return {
        'user_name': user_name,
        'organization_units': ou_list,
        'domain_components': dc_list
    }


def white_list(ou_list):
    accept_ou = ["010", "020", "030", "051", "052", "053", "054", "1C0", "1CH", "2D0", "2DD", "3E0", "3EC", "4F0", "4FD", "5G0", "5G4"]
    edit_ou =["051"]

    # 統一轉成 list 處理
    if isinstance(ou_list, str):
        ou_list = [ou_list]

    # 先檢查是否為編輯者
    for ou in ou_list:
        if ou.strip() in edit_ou:
            return "EDITOR"

    # 再檢查是否為接受者
    for ou in ou_list:
        if ou.strip() in accept_ou:
            return "VIEWER"

    # 其他都不是
    return "NONE"
# if __name__ == "__main__":
   
#     # 測試用戶名和密碼
#     test_username = "zong-han01273"
#     test_password = "d+55*****"
#     # 驗證用戶名和密碼
#     if check_ad_credentials(test_username, test_password):
#         print("✅ 驗證成功！")

#         user_info = get_user_info_one("sAMAccountName", "zong-han01273")

#         if user_info:
#             parse_dn_result = parse_dn(user_info['DP_STR'])
#             print(parse_dn_result['organization_units'][1])
#         else:
#             print("❌ 沒有找到該使用者")
#     else:
#         print("❌ 驗證失敗！")

