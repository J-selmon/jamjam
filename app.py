import streamlit as st
import json
from datetime import datetime
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px
from streamlit_echarts import st_echarts
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="웹심 챌린지",
    page_icon="🎯",
    layout="wide"
)

# 초기 데이터 설정
if 'challenges' not in st.session_state:
    st.session_state.challenges = [
        {
            "id": 1,
            "title": "첫 번째 웹페이지 만들기",
            "description": "HTML과 CSS를 사용하여 간단한 개인 웹페이지를 만들어보세요.",
            "difficulty": "초급",
            "category": "웹 기초",
            "duration": "1주일",
            "points": 100
        },
        {
            "id": 2,
            "title": "투두리스트 만들기",
            "description": "JavaScript를 사용하여 할 일 목록을 관리하는 앱을 만들어보세요.",
            "difficulty": "중급",
            "category": "JavaScript",
            "duration": "2주일",
            "points": 200
        },
        {
            "id": 3,
            "title": "날씨 앱 만들기",
            "description": "API를 활용하여 실시간 날씨 정보를 보여주는 앱을 만들어보세요.",
            "difficulty": "고급",
            "category": "API 통합",
            "duration": "3주일",
            "points": 300
        }
    ]

# 세션 상태 초기화
if 'participations' not in st.session_state:
    st.session_state.participations = []
if 'total_points' not in st.session_state:
    st.session_state.total_points = 0
if 'user' not in st.session_state:
    st.session_state.user = None
if 'comments' not in st.session_state:
    st.session_state.comments = {}

# CSS 스타일
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .challenge-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .badge {
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        background-color: #f0f0f0;
    }
    .points {
        color: #1f77b4;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 사이드바 - 로그인/회원가입
with st.sidebar:
    if st.session_state.user is None:
        st.subheader("로그인")
        login_username = st.text_input("사용자 이름", key="login_username")
        login_password = st.text_input("비밀번호", type="password", key="login_password")
        if st.button("로그인"):
            # 실제 구현에서는 데이터베이스 연동 필요
            st.session_state.user = {"name": login_username, "points": 0}
            st.success(f"환영합니다, {login_username}님!")
            st.rerun()
    else:
        st.write(f"안녕하세요, {st.session_state.user['name']}님!")
        st.write(f"현재 포인트: {st.session_state.total_points}")
        if st.button("로그아웃"):
            st.session_state.user = None
            st.rerun()

# 메인 페이지
st.title("웹심 챌린지 🎯")
st.markdown("웹 개발 실력을 향상시키는 재미있는 방법")

# 네비게이션
selected = option_menu(
    menu_title=None,
    options=["챌린지", "내 참여현황", "추천하기"],
    icons=["trophy", "person", "star"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

if selected == "챌린지":
    # 필터 섹션
    col1, col2, col3 = st.columns(3)
    with col1:
        difficulty_filter = st.selectbox(
            "난이도 필터",
            ["전체", "초급", "중급", "고급"]
        )
    
    # 챌린지 목록 표시
    challenges_to_show = st.session_state.challenges
    if difficulty_filter != "전체":
        challenges_to_show = [c for c in challenges_to_show if c["difficulty"] == difficulty_filter]
    
    for challenge in challenges_to_show:
        with st.container():
            st.markdown(f"""
            <div class="challenge-card">
                <h3>{challenge['title']}</h3>
                <span class="badge">{challenge['difficulty']}</span>
                <p>{challenge['description']}</p>
                <p>🏷️ {challenge['category']} • ⏱️ {challenge['duration']} • 
                   <span class="points">🏆 {challenge['points']}점</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            # 참여 버튼
            challenge_id = challenge['id']
            if challenge_id not in [p['challengeId'] for p in st.session_state.participations]:
                if st.button("참여하기", key=f"join_{challenge_id}"):
                    if st.session_state.user is None:
                        st.warning("로그인이 필요합니다.")
                    else:
                        participation = {
                            "challengeId": challenge_id,
                            "title": challenge['title'],
                            "category": challenge['category'],
                            "points": challenge['points'],
                            "participationDate": datetime.now().isoformat()
                        }
                        st.session_state.participations.append(participation)
                        st.session_state.total_points += challenge['points']
                        st.success(f"{challenge['title']} 챌린지에 참여하셨습니다!")
                        st.rerun()
            else:
                if st.button("참여 취소", key=f"cancel_{challenge_id}"):
                    st.session_state.participations = [p for p in st.session_state.participations if p['challengeId'] != challenge_id]
                    st.session_state.total_points -= challenge['points']
                    st.success("챌린지 참여가 취소되었습니다.")
                    st.rerun()
            
            # 댓글 섹션
            with st.expander("댓글"):
                if challenge_id not in st.session_state.comments:
                    st.session_state.comments[challenge_id] = []
                
                # 댓글 입력
                new_comment = st.text_input("댓글을 입력하세요", key=f"comment_{challenge_id}")
                if st.button("댓글 작성", key=f"submit_comment_{challenge_id}"):
                    if st.session_state.user is None:
                        st.warning("로그인이 필요합니다.")
                    else:
                        st.session_state.comments[challenge_id].append({
                            "user": st.session_state.user['name'],
                            "text": new_comment,
                            "date": datetime.now().isoformat()
                        })
                        st.success("댓글이 작성되었습니다.")
                
                # 댓글 표시
                for comment in st.session_state.comments[challenge_id]:
                    st.markdown(f"""
                    **{comment['user']}**: {comment['text']}  
                    _{datetime.fromisoformat(comment['date']).strftime('%Y-%m-%d %H:%M')}\_
                    """)

elif selected == "내 참여현황":
    if st.session_state.user is None:
        st.warning("로그인이 필요합니다.")
    else:
        st.subheader("나의 챌린지 현황")
        
        # 참여 현황 차트
        if st.session_state.participations:
            df = pd.DataFrame(st.session_state.participations)
            fig = px.pie(df, names='category', title='카테고리별 참여 현황')
            st.plotly_chart(fig)
            
            # 참여 목록
            st.subheader("참여 중인 챌린지")
            for p in st.session_state.participations:
                st.markdown(f"""
                * **{p['title']}**
                  * 카테고리: {p['category']}
                  * 획득 포인트: {p['points']}
                  * 참여일: {datetime.fromisoformat(p['participationDate']).strftime('%Y-%m-%d')}
                """)
        else:
            st.info("아직 참여한 챌린지가 없습니다.")

elif selected == "추천하기":
    if st.session_state.user is None:
        st.warning("로그인이 필요합니다.")
    else:
        st.subheader("새로운 챌린지 추천하기")
        
        title = st.text_input("챌린지 제목")
        description = st.text_area("챌린지 설명")
        difficulty = st.selectbox("난이도", ["초급", "중급", "고급"])
        duration = st.selectbox("소요 기간", ["1주일", "2주일", "3주일", "4주일"])
        
        if st.button("추천하기"):
            new_challenge = {
                "id": len(st.session_state.challenges) + 1,
                "title": title,
                "description": description,
                "difficulty": difficulty,
                "category": "추천",
                "duration": duration,
                "points": random.choice([100, 200, 300])
            }
            st.session_state.challenges.append(new_challenge)
            st.success("새로운 챌린지가 추천되었습니다!")
            st.rerun()

# 푸터
st.markdown("---")
st.markdown("© 2024 웹심 챌린지. All rights reserved.")