import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Cấu hình phạm vi quyền truy cập
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

try:
    # Lấy biến môi trường GOOGLE_CREDS_JSON
    GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
    if not GOOGLE_CREDS_JSON:
        raise Exception("Biến môi trường GOOGLE_CREDS_JSON không tồn tại hoặc đang rỗng.")

    # Parse JSON string thành dict
    creds_dict = json.loads(GOOGLE_CREDS_JSON)

    # Tạo credentials từ dict
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    # Authorize với Google Sheets
    client = gspread.authorize(creds)
    print("✅ Kết nối thành công Google Sheets.")

    # ✅ TEST: Mở một Sheet cụ thể (đổi tên sheet theo thực tế)
    sheet = client.open("Tên_Sheet_Của_Bạn").sheet1
    print(f"📄 Đang mở Sheet: {sheet.title}")
    print("📌 Dòng đầu tiên trong sheet:", sheet.row_values(1))

except Exception as e:
    print("❌ Kết nối thất bại:", e)
