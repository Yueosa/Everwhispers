import streamlit as st
import json
from datetime import datetime
import os
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
IMAGE_DIR = os.path.join(UPLOAD_DIR, "images")
VIDEO_DIR = os.path.join(UPLOAD_DIR, "videos")
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audios")
DATA_PATH = os.path.join(BASE_DIR, "messages.json")
ADMIN_PASSWORD = "Yosa-0516"

if not os.path.exists(DATA_PATH):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

for dir in [IMAGE_DIR, VIDEO_DIR, AUDIO_DIR]:
    os.makedirs(dir, exist_ok=True)

def load_messages():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        messages = json.load(f)
    
    for msg in messages:
        files = msg.get("files", {})
        for file_type in files:
            if files[file_type]:
                # 确保使用正确的子文件夹
                subdir = f"{file_type}s"  # images, videos, audios
                files[file_type] = os.path.join(UPLOAD_DIR, subdir, os.path.basename(files[file_type]))
    return messages

def save_messages(new_msg):
    messages = load_messages()
    messages.append(new_msg)
    
    for msg in messages:
        files = msg.get("files", {})
        for file_type in files:
            if files[file_type]:
                # 只保存文件名
                files[file_type] = os.path.basename(files[file_type])
                
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def del_messages(id):
    message_list = load_messages()
    message_list = [msg for msg in message_list if msg["id"] != id]
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(message_list, f, ensure_ascii=False, indent=4)

def name_list():
    name_list = load_messages()
    search_list = {msg["name"] for msg in name_list}
    return search_list

st.set_page_config(page_title="留言板系统", layout="wide")
st.title("📮 迷你留言板系统")

# 🔒 设置管理员登录状态
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# 用于存储删除操作的状态
if "delete_msg" not in st.session_state:
    st.session_state["delete_msg"] = None

# 侧边栏：管理员登录区域
with st.sidebar:
    st.subheader("管理员登录")
    admin_input = st.text_input("输入管理员密码：", type="password")

    if st.button("登录"):
        st.session_state["is_admin"] = admin_input == ADMIN_PASSWORD
        if st.session_state["is_admin"]:
            st.success("登录成功")
        else:
            st.error("密码错误")

    if st.session_state["is_admin"]:
        st.info("管理员模式：开启 ✅")
    else:
        st.warning("管理员模式：关闭 ❌")

st.markdown("---")

tab1, tab2 = st.tabs(["留言", "更多"])

with tab1:
    # ✅ 留言区
    with st.expander("编写留言"):
        image_file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], key="image")
        video_file = st.file_uploader("上传视频", type=["mp4", "webm"], key="video")
        audio_file = st.file_uploader("上传音频", type=["mp3", "wav"], key="audio")
        
        if image_file:
            st.image(image_file, width=150, caption="图片预览")
        if video_file:
            st.video(video_file)
        if audio_file:
            st.audio(audio_file)

        # 留言表单
        with st.form("message_form"):
            name = st.text_input("你的名字: ")
            message = st.text_area("你想说的话:  ")

            # 提交按钮
            submit = st.form_submit_button("📬 提交留言")

            if submit:
                if name.strip() and message.strip():
                    message_id = str(uuid.uuid4())
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    files = {"image": None, "video": None, "audio": None}

                    # 文件保存
                    if image_file:
                        image_path = os.path.join(IMAGE_DIR, f"{message_id}_{image_file.name}")
                        with open(image_path, "wb") as f:
                            f.write(image_file.getbuffer())
                        files["image"] = os.path.relpath(image_path, UPLOAD_DIR)

                    if video_file:
                        video_path = os.path.join(VIDEO_DIR, f"{message_id}_{video_file.name}")
                        with open(video_path, "wb") as f:
                            f.write(video_file.getbuffer())
                        files["video"] = os.path.relpath(video_path, UPLOAD_DIR)

                    if audio_file:
                        audio_path = os.path.join(AUDIO_DIR, f"{message_id}_{audio_file.name}")
                        with open(audio_path, "wb") as f:
                            f.write(audio_file.getbuffer())
                        files["audio"] = os.path.relpath(audio_path, UPLOAD_DIR)

                    # 保存留言
                    save_messages({
                        "id": message_id,
                        "name": name,
                        "message": message,
                        "timestamp": timestamp,
                        "files": files
                    })
                    st.success("留言已提交~我喜欢你!")
                else:
                    st.warning("请填写完整的内容再提交哦~")


    st.markdown("---")
    st.subheader("📜 历史留言")

    # ✅ 显示删除成功信息
    if st.session_state["delete_msg"]:
        st.success(st.session_state["delete_msg"])
        st.session_state["delete_msg"] = None

    # ✅ 展示历史留言
    for msg in reversed(load_messages()):
        col_text, col_btn = st.columns([9, 1])

        with col_text:
            st.markdown(
                f"""
                <div style='
                    background-color: #f0f2f6;
                    padding: 10px;
                    border-radius: 10px;
                    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
                    margin-bottom: 10px;
                '>
                <strong>{msg['name']}</strong> 说：{msg['message']}<br>
                <span style='font-size: 12px; color: gray;'>🕒 {msg['timestamp']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            files = msg.get("files", {"image": None, "video": None, "audio": None})

            # 图片展示
            if msg["files"]["image"]:
                image_path = os.path.join(UPLOAD_DIR, "images", os.path.basename(msg["files"]["image"]))
                st.image(image_path)

            # 视频展示
            if msg["files"]["video"]:
                video_path = os.path.join(UPLOAD_DIR, "videos", os.path.basename(msg["files"]["video"]))
                st.video(video_path)

            # 音频展示
            if msg["files"]["audio"]:
                audio_path = os.path.join(UPLOAD_DIR, "audios", os.path.basename(msg["files"]["audio"]))
                st.audio(audio_path)

        with col_btn:
            # 仅管理员可删除
            if st.session_state["is_admin"]:
                if st.button("🗑️", key=f"del_{msg['id']}"):
                    del_messages(msg['id'])
                    st.session_state["delete_msg"] = "留言已删除"
                    st.rerun()


with tab2:
    st.header("暂时没有东西哦")
