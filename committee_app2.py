import streamlit as st
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("SILICONFLOW_API_KEY"), base_url="https://api.siliconflow.cn/v1")

COMMITTEE = [
    {"name": "技术尽调官", "weight": 0.25,
     "instruction": """你是一位技术尽调专家。请严格按照以下JSON格式输出，不要包含任何其他文本、注释或解释：
{
  "风险等级": "高/中/低",
  "待验证假设": ["假设1", "假设2"],
  "投票": "通过/待定/拒绝",
  "置信度": "高/中/低",
  "理由简述": "不超过20字"
}
项目描述："""},
    {"name": "市场分析师", "weight": 0.25,
     "instruction": """你是一位市场分析师。请严格按照以下JSON格式输出：
{
  "市场吸引力": 1-5,
  "关键不确定因素": "字符串",
  "投票": "通过/待定/拒绝",
  "置信度": "高/中/低",
  "理由简述": "不超过20字"
}
项目描述："""},
    {"name": "合规顾问", "weight": 0.35,
     "instruction": """你是一位合规专家。请严格按照以下JSON格式输出：
{
  "主要风险点": "无或描述",
  "应对措施": "无或措施",
  "投票": "通过/待定/拒绝",
  "置信度": "高/中/低",
  "理由简述": "不超过20字"
}
项目描述："""},
    {"name": "财务风控官", "weight": 0.15,
     "instruction": """你是一位财务风控专家。请严格按照以下JSON格式输出：
{
  "关键假设": "描述",
  "财务风险": "描述",
  "投票": "通过/待定/拒绝",
  "置信度": "高/中/低",
  "理由简述": "不超过20字"
}
项目描述："""}
]

def call_llm(prompt):
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw = response.choices[0].message.content
    # 提取第一个JSON对象
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return match.group(0)
    else:
        return "{}"

st.title("投资委员会评审系统 (V5)")
name = st.text_input("项目名称")
desc = st.text_area("项目描述")
if st.button("开始评审") and name and desc:
    results = {}
    weighted_sum = 0.0
    total_weight = 0.0
    for m in COMMITTEE:
        prompt = f"{m['instruction']}{desc}"
        with st.spinner(f"咨询 {m['name']} ..."):
            raw_json = call_llm(prompt)
            try:
                data = json.loads(raw_json)
            except:
                data = {"投票": "待定", "理由简述": "解析失败"}
        results[m['name']] = data
        vote = data.get("投票", "待定")
        score = 2 if vote == "通过" else (1 if vote == "待定" else 0)
        weighted_sum += score * m["weight"]
        total_weight += m["weight"]
        st.write(f"**{m['name']}**：投票 {vote}，置信度 {data.get('置信度','-')}，理由 {data.get('理由简述','')}")
    if total_weight > 0:
        avg = weighted_sum / total_weight
    else:
        avg = 1.0
    if avg >= 1.45:
        final = "通过"
    else:
        final = "待定"
    st.success(f"最终结论：{final} (加权得分 {avg:.2f})")