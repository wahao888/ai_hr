import imaplib
import email
import re
import uuid
import os
from email.header import decode_header
from dotenv import load_dotenv 

# 加載 .env 檔案中的環境變數
load_dotenv()

# 設定 Gmail IMAP 伺服器和登入資訊
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "barrywang.gate@gmail.com"
PASSWORD = os.getenv("GMAIL_IMAP_PASSWORD")
FOLDER = "inbox"

# 連接到 Gmail
def connect_gmail():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.select(FOLDER)
    return mail

# 提取郵件標題中的姓名
def extract_name_from_subject(subject):
    # 先解碼郵件標題
    decoded_header = decode_header(subject)
    subject = ''.join([str(part[0], part[1] or 'utf-8') if isinstance(part[0], bytes) else part[0] for part in decoded_header])
    print(f"解碼後的郵件標題: {subject}")  # 顯示解碼後的標題

    # 提取右括號 "】" 後面的三個字，假設應徵者姓名是三個字
    match = re.search(r"】(.{3})", subject)
    if match:
        return match.group(1)
    return None

def extract_work_experience(body):
    match = re.search(r"總年資(.+)", body, re.DOTALL)
    if match:
        print(f"提取到的 '總年資' 部分: {match.group(1)[:100]}...")  # 顯示 '總年資' 部分的前 100 個字符
        return match.group(1).strip()
    print("未找到 '總年資'")
    return None



# 匹配姓名並替換為 "姓氏OO"
def anonymize_name(text, name):
    # 將應徵者名字替換為 "姓氏OO"
    surname = name[0]
    return text.replace(name, surname + "OO")

# 讀取郵件並處理內容
def process_emails():
    mail = connect_gmail()
    result, data = mail.search(None, 'ALL')
    email_ids = data[0].split()

    print(f"找到的郵件數量: {len(email_ids)}")  # 確認郵件總數
    
    processed_data = []

    for email_id in email_ids:
        # 讀取郵件資料
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # 提取郵件標題
        subject = msg["Subject"]
        print(f"處理郵件標題: {subject}")  # 確認是否獲取到郵件標題

        name = extract_name_from_subject(subject)
        if not name:
            print("未找到應徵者姓名，跳過郵件")
            continue
        
        # 生成唯一 UID
        uid = str(uuid.uuid4())

        # 提取郵件內容
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8")
                    print(f"找到郵件正文 (text/plain): {body[:100]}...")  # 顯示正文的前 100 個字符
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8")
            print(f"找到郵件正文 (non-multipart): {body[:100]}...")  # 顯示正文的前 100 個字符

        # 提取 "總年資" 開始的內容
        work_experience = extract_work_experience(body)
        if not work_experience:
            print("未找到 '總年資'，跳過郵件")
            continue
        
        print(f"提取到的總年資: {work_experience[:100]}...")  # 顯示總年資的前 100 個字符
        
        # 匹配姓名並進行替換
        anonymized_text = anonymize_name(work_experience, name)

        # 儲存到檔案
        file_name = f"{uid}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(anonymized_text)
        
        # 儲存處理結果
        processed_data.append({"UID": uid, "Name": name})

    return processed_data


# 將結果匯出成一個 CSV 文件
def save_to_csv(processed_data):
    if not processed_data:
        print("沒有資料可保存到 CSV")  # 檢查是否有數據
        return

    import pandas as pd
    df = pd.DataFrame(processed_data)
    print(f"寫入 CSV 的資料: {df.head()}")  # 查看前幾筆資料
    df.to_csv("processed_resumes.csv", index=False)


# 主程式執行
processed_data = process_emails()
save_to_csv(processed_data)
