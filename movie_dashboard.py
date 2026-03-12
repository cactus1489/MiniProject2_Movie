import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from collections import Counter
import re

# ── Korean font setup for matplotlib (Windows Malgun Gothic) ──
matplotlib.rc('font', family='Malgun Gothic')
matplotlib.rcParams['axes.unicode_minus'] = False

# Page config
st.set_page_config(page_title="왕과 사는 남자 - 관람평 대시보드", layout="wide")

# Styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        color: #1e1e1e;
        font-family: 'Pretendard', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("movie_reviews_detailed_full.csv", encoding="utf-8-sig")
    # Clean rating to numeric
    df['별점'] = pd.to_numeric(df['별점'], errors='coerce')
    df = df.dropna(subset=['별점', '리뷰내용'])
    return df

def get_keywords(text_series, top_n=20):
    text = " ".join(text_series.astype(str))
    # Simple Korean-friendly word split (nouns/names)
    words = re.findall(r'[가-힣]{2,}', text)
    # Filter common stopwords (very basic)
    stopwords = {'진짜', '너무', '정말', '보고', '영화', '보고왔는데', '보고왔어요', '봤는데', '봤어요'}
    filtered_words = [w for w in words if w not in stopwords]
    return Counter(filtered_words).most_common(top_n)

def main():
    st.title("🎬 '왕과 사는 남자' 관람평 인사이트 대시보드")
    
    try:
        df = load_data()
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return

    # Sidebar
    st.sidebar.header("🔍 필터 및 검색")
    search_query = st.sidebar.text_input("리뷰 내용 검색", "")
    min_rating = st.sidebar.slider("최소 별점", 1, 10, 1)
    
    # Filtering
    filtered_df = df[df['별점'] >= min_rating]
    if search_query:
        filtered_df = filtered_df[filtered_df['리뷰내용'].str.contains(search_query, case=False, na=False)]

    # --- Metrics Section ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("평균 평점", f"{df['별점'].mean():.2f} / 10")
    with col2:
        st.metric("총 리뷰 수", f"{len(df)}건")
    with col3:
        st.metric("총 공감수", f"{int(df['공감수'].sum()):,}회")
    with col4:
        st.metric("최고 평점 비율", f"{(len(df[df['별점']==10])/len(df)*100):.1f}%")

    st.divider()

    # --- Dash Section ---
    tab1, tab2, tab3 = st.tabs(["📊 시각화 분석", "💡 핵심 인사이트", "📝 리뷰 상세 보기"])

    with tab1:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("별점 분포")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.countplot(data=df, x='별점', palette="viridis", ax=ax)
            ax.set_title("Audience Rating Distribution")
            st.pyplot(fig)
            
        with c2:
            st.subheader("주요 언급 키워드 TOP 15")
            keywords = get_keywords(df['리뷰내용'], 15)
            kw_df = pd.DataFrame(keywords, columns=['word', 'count'])
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(data=kw_df, x='count', y='word', palette="magma", ax=ax)
            ax.set_title("Most Frequent Keywords")
            st.pyplot(fig)

    with tab2:
        st.subheader("🔍 리뷰 데이터 기반 핵심 인사이트")
        
        col_ins1, col_ins2 = st.columns(2)
        
        with col_ins1:
            st.info("""
            **✅ 긍정 포인트 (Top Strengths)**
            1. **배우들의 연기 차력쇼:** 특히 **박지훈(단종 역)**의 눈빛 연기에 대한 찬사가 압도적입니다. "단종 그 자체", "눈빛이 개연성" 등의 표현이 반복됩니다.
            2. **유해진의 폭넓은 연기:** 특유의 코믹함부터 묵직한 감정 연기까지 극의 중심을 잘 잡았다는 평이 많습니다.
            3. **장항준 감독의 재발견:** "감독의 인생작", "연출이 따뜻하다"는 반응이 주를 이룹니다.
            4. **높은 감정적 몰입:** 후반부 '오열', '눈물' 키워드가 매우 높게 나타나며 관객들의 감정선을 성공적으로 건드렸음을 알 수 있습니다.
            """)
            
        with col_ins2:
            st.warning("""
            **⚠️ 아쉬운 포인트 (Areas for Improvement)**
            1. **호랑이 CG의 이질감:** "연출에서 호랑이만 아쉽다", "CG가 몰입을 방해한다"는 구체적인 지적이 반복적으로 등장합니다.
            2. **빠른 전개와 개연성:** 일부 관객들은 후반부 전개가 다소 빨라 서사가 뚝뚝 끊기는 느낌을 받았다고 회고합니다.
            3. **신파적 요소에 대한 호불호:** 대다수는 감동적이라 평했으나, 일부 낮은 평점 리뷰어들은 "억지 눈물", "유치한 연출"이라는 반응을 보였습니다.
            """)
            
        st.success("""
        **📌 종합 결론:** 
        전통 사극의 묵직함보다는 **배우들의 압도적인 캐릭터 소화력**과 **감성적인 연출**이 천만 흥행의 주역입니다. 
        특히 박지훈은 이번 영화를 통해 '아이돌 출신' 꼬리표를 완전히 떼고 영화계의 기대주로 우뚝 섰음을 데이터로 확인할 수 있습니다.
        """)

    with tab3:
        st.subheader(f"리뷰 리스트 (검색 결과: {len(filtered_df)}건)")
        st.dataframe(filtered_df[['별점', '리뷰내용', '작성자', '작성일', '공감수']].sort_values(by='공감수', ascending=False), 
                     use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
