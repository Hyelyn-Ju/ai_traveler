import openai
import streamlit as st
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase_client = init_connection()

st.title("🗺️ 확신의 J가 짜주는 여행계획")
st.image("./data/sky.png")
openai.api_key = st.secrets.OPENAI_TOKEN

def generate_prompt(place, days, style, mbti, n):
    prompt = f"""
여행을 하기 위한 여행 계획을 {n}개 짜주세요.
여행 기간과 여행 컨샙에 맞는 여행일정을 짜주세요.
반드시 모든 식당과 관광지는 해당 여행지에 확실히 존재하는 유명한 곳으로만 추천해 주세요.
반드시 여행지가 지구에 있는 장소가 아닌 곳이 아니라면 "아직 우주로의 여행은 준비되지 않았습니다...🚀"만을 출력하고 다른 내용을 출력하지 말아주세요.
지구에 있는 장소가 여행지로 입력 되었을때는 위 내용자체를 절대 언급하지 말아주세요.
만약 mbti가 입력된다면 해당 mbti에 맞는 여행 일정을 짜주세요.
만약 mbti가 입력되었다면 해당 mbti의 여행 스타일에 대해서 문장 맨 위에 한줄정도 알려주세요.
여행일정은 2-3시간 간견으로 짜주세요.
컨셉이 맛집탐방일 경우 식당까지 추천하며 간단한 식당의 정보를 맨 하단에 남겨주세요.
컨셉이 관광명소일 경우에만 관광지에 대한 설명을 해주세요.

---
여행지 정보: {place},
여행 기간 정보: {days},
여행 컨셉:{style}
mbti:{mbti}
---
"""
    return prompt.strip()

def request_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system", "content": "당신은 전문 여행가입니다."},
            {"role":"user", "content":prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

def write_prompt_result(prompt, result):
    response = supabase_client.table("prompt_results").insert(
        {
            "prompt":prompt,
            "result":result,
            "mbti":mbti
        }
    ).execute()
    print(response)



with st.form("my_form"):
    place = st.text_input("여행지를 알려주세요.(필수)", placeholder="강릉")
    days = st.text_input("여행 기간을 알려주세요.(필수)", placeholder="2박3일")
    style = st.selectbox(
        "여행 컨샙을 선택해주세요.",
        ["맛집 탐방", "관광명소", "휴식"]
    )
    mbti = st.text_input("mbti를 알려주세요.", placeholder="isfj")
    submitted = st.form_submit_button("Submit")
    if submitted:
        if not place:
            st.error("여행지를 입력해주세요.")
        if not days:
            st.error("여행 기간을 입력해주세요.")
        else:
            prompt = generate_prompt(place, days, style, mbti,n=1)
            with st.spinner("확신의 J가 일정을 짜고 있습니다..."):
                generated_text = request_chat_completion(prompt)
                response = request_chat_completion(prompt)
                write_prompt_result(prompt, response)
                st.text_area(
                    label="확신의 J가 짜드린 여행일정 결과",
                    value=generated_text,
                    placeholder="아직 여행일정이 완성되지 않았습니다.",
                    height=600
                )