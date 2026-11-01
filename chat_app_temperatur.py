import streamlit as st
from groq import Groq
import os

st.title("简单AI聊天")

# 可选模型
models = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-safeguard-20b"
]

# 初始化
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "你是一个友好的助手，回答要简洁易懂。"

if "model" not in st.session_state:
    st.session_state.model = models[0]

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "messages" not in st.session_state:
    st.session_state.messages = []

def format_chat():
    lines = []
    for msg in st.session_state.messages:
        role = "用户" if msg["role"] == "user" else "AI"
        lines.append(f"{role}：{msg['content']}")
    return "\n\n".join(lines)

# 侧边栏
with st.sidebar:
    st.header("操作")
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()
    
    # 模型选择
    st.session_state.model = st.selectbox(
        "选择模型",
        models,
        index=models.index(st.session_state.model)
    )
    
    # 温度调节
    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1
    )
    
    # 可编辑系统提示词
    st.session_state.system_prompt = st.text_area(
        "系统提示词",
        value=st.session_state.system_prompt,
        height=100
    )
    
    if st.session_state.messages:
        chat_text = format_chat()
        st.download_button(
            label="导出对话",
            data=chat_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )
    
    uploaded_file = st.file_uploader("上传文本文件", type=["txt"])
    file_content = ""
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        st.write("已上传文件，内容预览：")
        st.text(file_content[:300])

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

def generate_reply(messages):
    client = Groq(api_key=os.getenv("API_KEY"))
    stream = client.chat.completions.create(
        model=st.session_state.model,
        messages=messages,
        temperature=st.session_state.temperature,
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# 接收用户输入
if prompt := st.chat_input("说点什么..."):
    user_message = prompt
    if file_content:
        user_message = f"文件内容：\n{file_content}\n\n用户问题：{prompt}"
    
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.write(prompt)
    
    messages = [
        {"role": "system", "content": st.session_state.system_prompt}
    ] + st.session_state.messages
    
    with st.chat_message("assistant"):
        reply = st.write_stream(generate_reply(messages))
    
    st.session_state.messages.append({"role": "assistant", "content": reply})