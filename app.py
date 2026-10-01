import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Doosan E&C Financial Insight",
    page_icon="🏗️",
    layout="wide"
)

# -----------------------------
# 기본 스타일
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.8rem; padding-bottom: 2.5rem;}
h1, h2, h3 {letter-spacing: -0.03em;}
.doosan-card {
    border: 1px solid #e8e8e8;
    border-radius: 16px;
    padding: 18px 20px;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.doosan-note {
    border-left: 4px solid #2458d3;
    background: #f6f8ff;
    padding: 14px 16px;
    border-radius: 8px;
    margin: 8px 0 14px 0;
}
.small {color:#666; font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 공시자료 기반 데이터
# 단위: 억원 (별도 표시가 없는 경우)
# -----------------------------

# 1) 공사 종류별 매출실적
# 2024 사업보고서: 제49기(2024), 제48기(2023), 제47기(2022)
sales_mix = pd.DataFrame({
    "연도": ["2022"]*4 + ["2023"]*4 + ["2024"]*4 + ["2025"]*4,
    "공사종류": ["국내건축", "국내토목", "해외건축", "기타"] * 4,
    "매출액_억원": [
        9498, 2178, 133, 98,
        14915, 1978, 142, 141,
        18965, 2699, 6, 84,
        14539.54, 3165.28, 128.30, 69.32
    ]
})

sales_mix["연도총매출_억원"] = sales_mix.groupby("연도")["매출액_억원"].transform("sum")
sales_mix["비중"] = sales_mix["매출액_억원"] / sales_mix["연도총매출_억원"] * 100
sales_2025 = sales_mix[sales_mix["연도"] == "2025"].copy()

# 2025 수익 주석 기준: 국내 건축 1,453,953.764백만원,
# 아시아 건축 12,830.187백만원, 토목 316,527.996백만원, 기타 6,932.122백만원
# 위 sales_mix에서는 건축을 국내/해외로 나누어 표시

# 2) 공사도급계약 변동
# 사업보고서 수익 주석 기준, 단위 억원
contract_flow = pd.DataFrame({
    "연도": ["2024", "2025"],
    "기초잔액_억원": [91368.98, 98625.35],
    "증감액_억원": [28242.89, 20918.53],
    "공사매출_억원": [20986.53, 17166.17],
    "기말잔액_억원": [98625.35, 102377.71]
})

contract_segment = pd.DataFrame({
    "연도": ["2024", "2024", "2025", "2025"],
    "구분": ["건축", "토목", "건축", "토목"],
    "증감액_억원": [20979.23, 7263.67, 16985.04, 3933.49],
    "공사매출_억원": [18294.30, 2692.23, 14082.74, 3083.43],
    "기말잔액_억원": [78128.50, 20496.85, 81030.80, 21346.91]
})

# 3) 매출 → 청구 → 회수
# 연결재무제표 주석의 고객과의 계약 잔액 기준
cash_conversion = pd.DataFrame({
    "연도": ["2023", "2024", "2025"],
    "매출채권_억원": [2014.68, 2075.21, 5403.14],
    "계약자산_억원": [1460.75, 3498.23, 2460.29],
    "계약부채_억원": [4310.30, 3935.88, 4250.29]
})

cash_conversion["청구전+회수전_억원"] = (
    cash_conversion["계약자산_억원"] + cash_conversion["매출채권_억원"]
)

# 2025 상·하반기 흐름 참고
half_2025 = pd.DataFrame({
    "시점": ["2024년말", "2025년 6월말", "2025년말"],
    "매출채권_억원": [2075.21, 4457.06, 5403.14],
    "계약자산_억원": [3498.23, 1798.26, 2460.29]
})

# 2025년말 주요 계약 일부
projects_2025 = pd.DataFrame({
    "프로젝트": [
        "우암2구역 주택재개발",
        "율하이엘 지역주택조합",
        "운천주공 주택재건축",
        "구미중앙숲 지역주택조합",
        "강화2 지역주택조합",
        "여의 주택재개발",
        "대야구역 재개발",
        "송림3지구 주택재개발",
        "원동남산지구 주택재개발"
    ],
    "수주총액_억원": [
        7175.71, 4489.94, 4356.11, 3958.75, 3127.28,
        2957.61, 2928.03, 2828.41, 2648.17
    ],
    "진행률_%": [100.00, 100.00, 4.09, 1.74, 10.65, 100.00, 6.55, 94.45, 93.79],
    "미청구공사_억원": [0, 0, 95.62, 0, 0, 0, 0, 740.05, 425.98],
    "공사미수금_억원": [1628.66, 108.00, 0, 0, 0, 225.18, 0, 0, 0]
})

# -----------------------------
# 공통 상단
# -----------------------------
st.title("Doosan E&C Financial Insight")
st.caption(
    "두산건설의 매출구조 → 공사도급계약 → 계약잔액을 연결해 "
    "사업계획과 자금관리 관점에서 살펴보는 재무분석 대시보드"
)

total_2025 = sales_2025["매출액_억원"].sum()
building_2025 = sales_2025[
    sales_2025["공사종류"].isin(["국내건축", "해외건축"])
]["매출액_억원"].sum()
building_share_2025 = building_2025 / total_2025 * 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("2025 매출", f"{total_2025:,.0f}억원")
m2.metric("2025 건축 매출 비중", f"{building_share_2025:.1f}%")
m3.metric("2025 공사도급 기말잔액", f"{contract_flow.iloc[-1]['기말잔액_억원']:,.0f}억원")
m4.metric(
    "기말잔액 ÷ 공사매출",
    f"{contract_flow.iloc[-1]['기말잔액_억원']/contract_flow.iloc[-1]['공사매출_억원']:.1f}배"
)

st.markdown("""
<div class="doosan-note">
<b>분석 방향</b><br>
① 두산건설은 어떤 공사에서 매출을 만드는가
→ ② 공사도급계약의 증감과 매출 인식 이후 얼마의 계약잔액이 남는가
→ ③ 매출 인식 후 청구 전 단계의 계약자산과 청구 후 회수 전 단계의 매출채권은 어떻게 변하는가
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "① 매출구조",
    "② 공사도급계약 → 매출",
    "③ 매출 → 청구 → 회수"
])

# -----------------------------
# TAB 1. 매출구조
# -----------------------------
with tab1:
    st.subheader("① 공사 종류별 매출구조")
    st.write(
        "최근 연간 공시를 기준으로 국내건축·국내토목·해외건축·기타의 "
        "매출 구성과 변화 방향을 확인합니다."
    )

    c1, c2 = st.columns([1, 1.15])

    with c1:
        fig = px.pie(
            sales_2025,
            names="공사종류",
            values="매출액_억원",
            hole=0.58
        )
        fig.update_traces(
            texttemplate="%{label}<br>%{percent:.1%}",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f}억원<extra></extra>"
        )
        fig.update_layout(
            title="2025 공사 종류별 매출 구성",
            legend_title_text="",
            margin=dict(t=60, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        df_show = sales_2025.copy()
        df_show["매출액"] = df_show["매출액_억원"].map(lambda x: f"{x:,.0f}억원")
        df_show["비중표시"] = df_show["비중"].map(lambda x: f"{x:.1f}%")
        st.dataframe(
            df_show[["공사종류", "매출액", "비중표시"]].rename(columns={"비중표시": "비중"}),
            hide_index=True,
            use_container_width=True
        )

        st.markdown(f"""
        <div class="doosan-card">
        <b>2025년 해석</b><br><br>
        2025년 매출은 약 <b>{total_2025:,.0f}억원</b>이며,
        국내·해외 건축을 합한 건축 매출 비중은 약 <b>{building_share_2025:.1f}%</b>입니다.<br><br>
        따라서 두산건설의 실적을 이해할 때는 건축부문의 매출 변화와
        확보된 공사계약이 이후 매출로 전환되는 흐름을 우선적으로 확인할 필요가 있습니다.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 최근 4개년 공사 종류별 매출")

    fig_mix = px.bar(
        sales_mix,
        x="연도",
        y="매출액_억원",
        color="공사종류",
        barmode="stack",
        text_auto=".3s",
        labels={"매출액_억원": "매출액(억원)", "연도": "", "공사종류": "공사종류"},
        title="2022~2025 공사 종류별 매출액"
    )
    st.plotly_chart(fig_mix, use_container_width=True)

    totals = sales_mix.groupby("연도", as_index=False)["매출액_억원"].sum()
    totals["증감률_%"] = totals["매출액_억원"].pct_change() * 100

    st.dataframe(
        totals.style.format({"매출액_억원": "{:,.0f}", "증감률_%": "{:+.1f}%"}),
        hide_index=True,
        use_container_width=True
    )

    rev_2024 = totals.loc[totals["연도"] == "2024", "매출액_억원"].iloc[0]
    rev_2025 = totals.loc[totals["연도"] == "2025", "매출액_억원"].iloc[0]
    change_25 = (rev_2025 / rev_2024 - 1) * 100

    st.markdown(f"""
    <div class="doosan-card">
    <b>매출구조에서 얻는 결론</b><br><br>
    ① 전체 매출은 2022년 약 <b>1.19조원</b>에서 2024년 약 <b>2.18조원</b>까지 확대됐습니다.<br><br>
    ② 2025년에는 약 <b>{rev_2025/10000:.2f}조원</b>으로 전년 대비 <b>{change_25:.1f}%</b> 감소했습니다.<br><br>
    ③ 2025년 감소는 특히 건축 매출 축소의 영향이 컸습니다. 따라서 단순히 전사 매출 감소만 보는 대신,
    다음 탭에서 공사도급계약의 신규 증감과 기말잔액을 함께 확인합니다.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# TAB 2. 공사도급계약 → 매출
# -----------------------------
with tab2:
    st.subheader("② 공사도급계약 → 매출 분석")
    st.write(
        "공사도급계약의 기초잔액에 신규계약·계약변경 등의 증감이 더해지고, "
        "공사매출로 인식된 뒤 얼마가 기말잔액으로 남는지 확인합니다."
    )

    a, b, c = st.columns(3)
    a.metric("2024 계약 증감액", f"{contract_flow.loc[0, '증감액_억원']:,.0f}억원")
    b.metric("2025 계약 증감액", f"{contract_flow.loc[1, '증감액_억원']:,.0f}억원",
             f"{(contract_flow.loc[1,'증감액_억원']/contract_flow.loc[0,'증감액_억원']-1)*100:.1f}%")
    c.metric("2025 기말 계약잔액", f"{contract_flow.loc[1, '기말잔액_억원']:,.0f}억원")

    fig_flow = go.Figure()
    fig_flow.add_trace(go.Bar(
        x=contract_flow["연도"],
        y=contract_flow["증감액_억원"],
        name="계약 증감액"
    ))
    fig_flow.add_trace(go.Bar(
        x=contract_flow["연도"],
        y=contract_flow["공사매출_억원"],
        name="공사매출"
    ))
    fig_flow.update_layout(
        barmode="group",
        title="공사도급계약 증감액과 공사매출",
        yaxis_title="억원",
        legend_title_text=""
    )
    st.plotly_chart(fig_flow, use_container_width=True)

    st.markdown("""
    <div class="doosan-note">
    <b>여기서 보는 핵심</b><br><br>
    2025년 계약 증감액은 전년보다 감소했고 공사매출도 줄었습니다.
    그럼에도 기말 계약잔액은 2024년 약 9.86조원에서 2025년 약 10.24조원으로 증가했습니다.
    즉 당해 매출 감소만으로 미래 사업기반까지 축소됐다고 해석하기보다는,
    신규·변경계약과 매출 인식 이후 남은 계약잔액을 함께 봐야 합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 건축과 토목으로 나누면?")

    fig_seg = px.bar(
        contract_segment,
        x="연도",
        y="증감액_억원",
        color="구분",
        barmode="stack",
        text_auto=".3s",
        labels={"증감액_억원": "계약 증감액(억원)", "연도": "", "구분": ""},
        title="건축·토목 공사도급계약 증감액"
    )
    st.plotly_chart(fig_seg, use_container_width=True)

    seg_pivot = contract_segment.pivot(
        index="구분", columns="연도", values="증감액_억원"
    ).reset_index()
    seg_pivot["증감_억원"] = seg_pivot["2025"] - seg_pivot["2024"]
    st.dataframe(
        seg_pivot.style.format({"2024": "{:,.0f}", "2025": "{:,.0f}", "증감_억원": "{:+,.0f}"}),
        hide_index=True,
        use_container_width=True
    )

    st.markdown("""
    <div class="doosan-card">
    <b>이 탭의 최종 결론</b><br><br>
    ① 2025년 공사도급계약 증감액은 약 <b>2.09조원</b>으로 2024년 약 2.82조원보다 감소했습니다.<br>
    ② 건축의 계약 증감액 감소폭이 토목보다 컸습니다.<br>
    ③ 같은 기간 공사매출도 약 <b>2.10조원 → 1.72조원</b>으로 감소했습니다.<br>
    ④ 그러나 기말 계약잔액은 약 <b>9.86조원 → 10.24조원</b>으로 증가했습니다.
    따라서 사업계획에서는 당기 매출뿐 아니라 계약 증감과 누적 계약잔액을 함께 관리할 필요가 있습니다.
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "주의: 공사도급계약의 '증감액'에는 신규수주뿐 아니라 계약변경 등에 따른 도급액 변동이 포함될 수 있으므로 "
        "이를 신규수주액과 동일하게 해석하지 않습니다."
    )

# -----------------------------
# TAB 3. 매출 → 청구 → 회수
# -----------------------------
with tab3:
    st.subheader("③ 매출 → 청구 → 회수 분석")
    st.write(
        "계약자산과 매출채권을 단순 잔액으로 보지 않고, "
        "매출이 현금으로 전환되는 과정의 어느 단계에 금액이 쌓이는지 확인합니다."
    )

    st.markdown("""
    <div class="doosan-note">
    <b>왜 이 두 계정을 보는가?</b><br><br>
    건설사업은 <b>공사진행 → 매출 인식 → 청구 → 현금 회수</b>의 과정을 거칩니다.<br>
    • <b>계약자산</b>: 재화나 용역을 이전해 대가를 받을 권리가 발생했지만 아직 청구하지 않은 금액<br>
    • <b>매출채권</b>: 청구 후 아직 현금으로 회수되지 않은 금액<br><br>
    따라서 두 계정을 함께 보면 청구 전 단계와 회수 전 단계 중 어디에 잔액이 쌓이는지 확인할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    fig_cash = go.Figure()
    fig_cash.add_trace(go.Bar(
        x=cash_conversion["연도"],
        y=cash_conversion["계약자산_억원"],
        name="계약자산(청구 전)"
    ))
    fig_cash.add_trace(go.Bar(
        x=cash_conversion["연도"],
        y=cash_conversion["매출채권_억원"],
        name="매출채권(회수 전)"
    ))
    fig_cash.update_layout(
        barmode="group",
        title="계약자산·매출채권 추이",
        yaxis_title="억원",
        legend_title_text=""
    )
    st.plotly_chart(fig_cash, use_container_width=True)

    latest = cash_conversion.iloc[-1]
    prev = cash_conversion.iloc[-2]

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "2025 계약자산",
        f"{latest['계약자산_억원']:,.0f}억원",
        f"{(latest['계약자산_억원']/prev['계약자산_억원']-1)*100:.1f}%"
    )
    c2.metric(
        "2025 매출채권",
        f"{latest['매출채권_억원']:,.0f}억원",
        f"{(latest['매출채권_억원']/prev['매출채권_억원']-1)*100:.1f}%"
    )
    c3.metric(
        "청구 전+회수 전",
        f"{latest['청구전+회수전_억원']:,.0f}억원",
        f"{(latest['청구전+회수전_억원']/prev['청구전+회수전_억원']-1)*100:.1f}%"
    )

    st.markdown("""
    <div class="doosan-card">
    <b>1차 진단</b><br><br>
    2024→2025년 계약자산은 약 <b>3,498억원 → 2,460억원</b>으로 감소했습니다.
    반면 매출채권은 약 <b>2,075억원 → 5,403억원</b>으로 크게 증가했습니다.<br><br>
    즉 2025년에는 청구 전 단계에 쌓인 금액은 감소했지만,
    청구 이후 아직 회수되지 않은 매출채권이 크게 늘어난 것이 특징입니다.
    따라서 자금관리 관점에서는 계약자산 감소만으로 현금전환이 개선됐다고 판단하기보다
    매출채권의 회수 흐름을 함께 확인해야 합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 2025년 중간 흐름까지 보면?")

    fig_half = go.Figure()
    fig_half.add_trace(go.Line(
        x=half_2025["시점"],
        y=half_2025["계약자산_억원"],
        mode="lines+markers+text",
        text=half_2025["계약자산_억원"].map(lambda x: f"{x:,.0f}"),
        textposition="top center",
        name="계약자산"
    ))
    fig_half.add_trace(go.Line(
        x=half_2025["시점"],
        y=half_2025["매출채권_억원"],
        mode="lines+markers+text",
        text=half_2025["매출채권_억원"].map(lambda x: f"{x:,.0f}"),
        textposition="bottom center",
        name="매출채권"
    ))
    fig_half.update_layout(
        title="2024년말 → 2025년 6월말 → 2025년말",
        yaxis_title="억원",
        legend_title_text=""
    )
    st.plotly_chart(fig_half, use_container_width=True)

    st.write(
        "2025년 상반기부터 계약자산이 줄고 매출채권이 증가하는 이동이 확인됩니다. "
        "연말에는 계약자산이 상반기말보다 다시 증가했지만, 매출채권 증가폭이 더 크게 나타났습니다."
    )

    st.markdown("#### 2025년말 주요 계약에서는 어디에 잔액이 있나?")

    project_long = projects_2025.melt(
        id_vars=["프로젝트", "수주총액_억원", "진행률_%"],
        value_vars=["미청구공사_억원", "공사미수금_억원"],
        var_name="구분",
        value_name="잔액_억원"
    )
    project_long["구분"] = project_long["구분"].replace({
        "미청구공사_억원": "미청구공사",
        "공사미수금_억원": "공사미수금"
    })

    fig_projects = px.bar(
        project_long,
        x="잔액_억원",
        y="프로젝트",
        color="구분",
        barmode="group",
        orientation="h",
        labels={"잔액_억원": "잔액(억원)", "프로젝트": "", "구분": ""},
        title="2025년말 주요 계약의 미청구공사·공사미수금"
    )
    fig_projects.update_layout(height=560)
    st.plotly_chart(fig_projects, use_container_width=True)

    st.markdown("""
    <div class="doosan-card">
    <b>이 탭에서 얻는 최종 결론</b><br><br>
    ① 2025년 계약자산은 전년보다 감소했지만 매출채권은 크게 증가했습니다.<br>
    ② 따라서 2025년 현금전환 과정에서 눈에 띄는 변화는 <b>청구 전 잔액의 확대보다 청구 후 회수 전 잔액의 확대</b>입니다.<br>
    ③ 주요 계약을 보면 프로젝트별로 미청구공사와 공사미수금이 쌓이는 위치가 다르므로,
    전체 잔액 변화 이후 개별 현장의 진행률·청구조건·회수일정을 확인해야 합니다.<br>
    ④ 재무담당자는 사업계획 수립 시 매출계획뿐 아니라 계약자산과 매출채권의 변화를 함께 반영해
    실제 자금 유입 시점을 관리할 필요가 있습니다.
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "주요 계약 표는 계약금액이 전기 매출액의 5% 이상인 중요 계약 등 공시 대상 기준이며, "
        "회사 전체 계약자산·매출채권과 동일한 범위가 아닙니다."
    )

# -----------------------------
# 출처 / 유의사항
# -----------------------------
st.divider()

with st.expander("데이터 출처 및 해석 유의사항"):
    st.markdown("""
    **출처**
    - 두산건설 2024 사업보고서(2025.03.31 제출)
    - 두산건설 2025 반기보고서(2025.08.14 제출)
    - 두산건설 2025 사업보고서(2026.03.31 제출)
    - 사용자가 제공한 두산건설 공시자료를 기준으로 수치를 구조화했습니다.

    **주요 기준**
    - 2022~2024 공사 종류별 매출: 사업보고서 '매출 및 수주상황'
    - 2025 공사 종류별 매출: 재무제표 주석 '수익'
    - 공사도급계약 변동: 재무제표 주석의 기간에 걸쳐 이행되는 수행의무 관련 공사도급계약 변동
    - 계약자산·매출채권: 재무제표 주석 '계약 잔액'
    - 주요 프로젝트: 사업보고서 '수주계약 현황 등'

    **유의사항**
    - 공사도급계약 '증감액'은 신규수주뿐 아니라 계약변경 등에 따른 도급액 변동을 포함할 수 있습니다.
    - 계약자산은 아직 청구하지 않은 금액이며 청구 시 수취채권으로 대체됩니다.
    - 주요 계약별 미청구공사·공사미수금은 회사 전체 계정잔액과 동일하지 않습니다.
    - 공개자료만으로 개별 현장의 실제 청구조건과 회수예정일을 모두 확인할 수 없습니다.
    - 특정 계정의 증가만으로 부실 또는 회수위험을 단정하지 않습니다.
    """)

st.caption("Doosan E&C Financial Insight · 생성형 AI를 활용한 개인 재무분석 프로젝트")
