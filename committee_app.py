# committee_app.py
import streamlit as st
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("SILICONFLOW_API_KEY"), base_url="https://api.siliconflow.cn/v1")

COMMITTEE = [
    {"name": "技术尽调官", "weight": 0.25,
     "instruction": """输出JSON：{"风险等级": "高/中/低", "待验证假设": ["假设1","假设2"], "投票": "通过/待定/拒绝", "置信度": "高/中/低", "理由简述": "..."}"""},
    {"name": "市场分析师", "weight": 0.25,
     "instruction": """输出JSON：{"市场吸引力": 1-5, "关键不确定因素": "...", "投票": "通过/待定/拒绝", "置信度": "高/中/低", "理由简述": "..."}"""},
    {"name": "合规顾问", "weight": 0.35,
     "instruction": """输出JSON：{"主要风险点": "...", "应对措施": "...", "投票": "通过/待定/拒绝", "置信度": "高/中/低", "理由简述": "..."}"""},
    {"name": "财务风控官", "weight": 0.15,
     "instruction": """输出JSON：{"关键假设": "...", "财务风险": "...", "投票": "通过/待定/拒绝", "置信度": "高/中/低", "理由简述": "..."}"""}
]

def call_llm(prompt):
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content

st.title("投资委员会评审系统 (V5)")
name = st.text_input("项目名称")
desc = st.text_area("项目描述")
if st.button("开始评审") and name and desc:
    results = {}
    weighted_sum = 0.0
    total_weight = 0.0
    for m in COMMITTEE:
        prompt = f"{m['instruction']}\n\n项目名称：{name}\n项目描述：{desc}"
        with st.spinner(f"正在咨询 {m['name']} ..."):
            raw = call_llm(prompt)
            try:
                data = json.loads(raw.strip())
            except:
                data = {"投票": "待定", "理由简述": "解析失败"}
        results[m['name']] = data
        vote = data.get("投票", "待定")
        score = 2 if vote == "通过" else (1 if vote == "待定" else 0)
        weighted_sum += score * m["weight"]
        total_weight += m["weight"]
        st.write(f"**{m['name']}**：投票 {vote}，置信度 {data.get('置信度','-')}，理由 {data.get('理由简述','')}")
    avg = weighted_sum / total_weight
    if avg >= 1.45:
        final = "通过"
    else:
        final = "待定"
    st.success(f"最终结论：{final} (加权得分 {avg:.2f})")