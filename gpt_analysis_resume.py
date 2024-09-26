import openai
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv 

# 加載 .env 檔案中的環境變數
load_dotenv()

# 初始化 OpenAI API 客戶端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 定義要分析的 txt 檔案所在目錄
resume_directory = "./resumes/"

# GPT 交互函數（使用最新的 client.chat.completions.create）
def gpt_evaluation(resume_text):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": "你是一個幫助進行候選人評估的智能助手，請根據指定的標準評估簡歷。"},
                {
                    "role": "user",
                    "content": f"根據以下篩選標準，請針對簡歷進行篩選和評分，只提供第五項表格化關鍵欄位的資訊：\n篩選標準：\n1. 基本信息檢查\n2. 根據應徵職位進行分類\n3. 評分標準 (教育程度、工作經驗、技能匹配與語言能力、性別及年齡條件、空窗期及工作穩定度)\n4. 綜合評分\n5. 關鍵欄位表格化呈現排序（候選人、年齡、學歷、工作經驗、技能與特點、工作穩定度、綜合評分、GPT觀點）\n\n以下是簡歷內容：{resume_text}"
                }
            ]
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating GPT response: {e}")
        return None

# 讀取所有 txt 檔案，並向 GPT 發送請求進行評分
def process_resumes():
    resume_files = [f for f in os.listdir(resume_directory) if f.endswith(".txt")]
    resume_data = []

    for resume_file in resume_files:
        with open(os.path.join(resume_directory, resume_file), "r", encoding="utf-8") as file:
            resume_text = file.read()

        print(f"處理文件: {resume_file}")
        gpt_response = gpt_evaluation(resume_text)
        
        if gpt_response:
            print(f"GPT 評分結果：\n{gpt_response}")
            # 根據 GPT 的回應，你可以將其儲存為 CSV 或其他格式
            resume_data.append({
                "filename": resume_file,
                "gpt_response": gpt_response
            })

    return resume_data

# 將 GPT 回應寫入 CSV 文件
def save_to_csv(resume_data):
    df = pd.DataFrame(resume_data)
    df.to_csv("gpt_resume_evaluation.csv", index=False, encoding="utf-8")
    print("已成功保存 GPT 評分結果至 gpt_resume_evaluation.csv")

# 主程式
if __name__ == "__main__":
    resume_data = process_resumes()
    if resume_data:
        save_to_csv(resume_data)
