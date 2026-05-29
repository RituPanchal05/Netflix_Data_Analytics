"""
Netflix EDA Streamlit Dashboard
================================
🔴 Recruiter-Ready | Interactive | Dark Theme

Setup:
    pip install streamlit pandas plotly wordcloud matplotlib pillow

Run:
    streamlit run netflix_dashboard.py

Data:
    Place your cleaned CSV as: data/netflix_cleaned.csv
    Expected columns: show_id, type, title, director, cast, country,
                      date_added, release_year, rating, duration, listed_in, description
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from collections import Counter

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Netflix Content Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Netflix Dark Theme CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark Netflix background */
    .stApp { background-color: #141414; color: #FFFFFF; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #E50914;
    }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1f1f1f, #2a2a2a);
        border: 1px solid #E50914;
        border-radius: 12px;
        padding: 16px !important;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.2);
    }
    div[data-testid="metric-container"] label { color: #b3b3b3 !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #E50914 !important; font-size: 2rem !important; font-weight: 800 !important;
    }
    
    /* Headers */
    h1 { color: #E50914 !important; font-weight: 900 !important; letter-spacing: -1px; }
    h2, h3 { color: #FFFFFF !important; font-weight: 700 !important; }
    
    /* Section divider */
    .section-title {
        border-left: 4px solid #E50914;
        padding-left: 12px;
        margin: 24px 0 16px 0;
        font-size: 1.3rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    
    /* Tabs */
    button[data-baseweb="tab"] { color: #b3b3b3 !important; font-weight: 600; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #E50914 !important;
        border-bottom: 2px solid #E50914 !important;
    }
    
    /* Dataframe */
    .stDataFrame { border: 1px solid #333; border-radius: 8px; }
    
    /* Selectbox and multiselect */
    div[data-baseweb="select"] > div { background-color: #2a2a2a !important; }
    
    /* Footer tag */
    .footer-tag {
        text-align: center;
        color: #555;
        font-size: 0.8rem;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid #222;
    }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark template ─────────────────────────────────────────────────────
NETFLIX_COLORS = ["#E50914", "#ff6b6b", "#ff9e9e", "#ffd3d3",
                  "#831010", "#b31317", "#cc1a1f", "#ff3333"]
PLOT_BG  = "#1a1a1a"
PAPER_BG = "#141414"
FONT_CLR = "#FFFFFF"
GRID_CLR = "#2a2a2a"

def make_layout(title="", height=400):
    return dict(
        title=dict(text=title, font=dict(color=FONT_CLR, size=15, family="Arial Black")),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_CLR, family="Arial"),
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
    )

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/netflix_cleaned.csv")
    except FileNotFoundError:
        try:
            df = pd.read_csv("data/netflix_titles.csv")
        except FileNotFoundError:
            # Demo data so the dashboard runs without files
            import numpy as np
            np.random.seed(42)
            n = 8807
            types    = np.random.choice(["Movie","TV Show"], n, p=[0.7, 0.3])
            years    = np.random.randint(2000, 2022, n)
            ratings  = np.random.choice(["TV-MA","TV-14","TV-PG","R","PG-13","PG","TV-G","G","NR"], n)
            countries= np.random.choice(["United States","India","United Kingdom","Japan","South Korea","France","Canada","Spain"], n, p=[0.35,0.15,0.1,0.08,0.07,0.07,0.1,0.08])
            genres   = ["Dramas","Comedies","Action & Adventure","Documentaries","Thrillers","International TV Shows","Children & Family","Romantic Movies","Horror Movies","Stand-Up Comedy"]
            months   = ["January","February","March","April","May","June","July","August","September","October","November","December"]
            df = pd.DataFrame({
                "show_id":    [f"s{i}" for i in range(n)],
                "type":       types,
                "title":      [f"Title {i}" for i in range(n)],
                "director":   [f"Director {np.random.randint(1,200)}" for _ in range(n)],
                "cast":       [f"Actor {np.random.randint(1,500)}, Actor {np.random.randint(1,500)}" for _ in range(n)],
                "country":    countries,
                "date_added": [f"{np.random.choice(months)} {np.random.randint(1,28)}, {np.random.randint(2013,2022)}" for _ in range(n)],
                "release_year": years,
                "rating":     ratings,
                "duration":   [f"{np.random.randint(60,180)} min" if t=="Movie" else f"{np.random.randint(1,8)} Seasons" for t in types],
                "listed_in":  [f"{np.random.choice(genres)}, {np.random.choice(genres)}" for _ in range(n)],
                "description": ["A great show." for _ in range(n)],
            })

    # ── Clean ────────────────────────────────────────────────────────────────
    if "show_id" in df.columns:
        df.drop_duplicates(subset="show_id", inplace=True)
    else:
        df.drop_duplicates(inplace=True)
    df.fillna({"director":"Unknown","cast":"Unknown","country":"Unknown","rating":"NR"}, inplace=True)

    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
        df["year_added"] = df["date_added"].dt.year
        df["month_added"]= df["date_added"].dt.month_name()

    if "duration" in df.columns:
        df["duration_int"] = df["duration"].str.extract(r"(\d+)").astype(float)

    # Genre explosion
    if "listed_in" in df.columns:
        df["genres"] = df["listed_in"].str.split(",")

    return df

df = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 Netflix Analytics")
    st.markdown("---")

    content_type = st.multiselect(
        "Content Type",
        options=df["type"].unique().tolist(),
        default=df["type"].unique().tolist()
    )

    years_range = st.slider(
        "Release Year",
        int(df["release_year"].min()),
        int(df["release_year"].max()),
        (2000, int(df["release_year"].max()))
    )

    if "rating" in df.columns:
        ratings = st.multiselect(
            "Rating",
            options=sorted(df["rating"].dropna().unique().tolist()),
            default=sorted(df["rating"].dropna().unique().tolist())
        )
    else:
        ratings = []

    st.markdown("---")
    st.markdown("### 📁 Project")
    st.markdown("[GitHub Repo](https://github.com/RituPanchal05/Netflix_Data_Analytics)", unsafe_allow_html=True)


# ── Filter ───────────────────────────────────────────────────────────────────
mask = (
    df["type"].isin(content_type) &
    df["release_year"].between(*years_range)
)
if ratings:
    mask &= df["rating"].isin(ratings)
dff = df[mask].copy()

# ── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 24px 0 8px 0;'>
  <h1 style='font-size:3rem; margin-bottom:0;'>🎬 Netflix Content Analytics</h1>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
movies = dff[dff["type"]=="Movie"]
shows  = dff[dff["type"]=="TV Show"]

k1.metric("📽️ Total Titles",   f"{len(dff):,}")
k2.metric("🎥 Movies",          f"{len(movies):,}")
k3.metric("📺 TV Shows",        f"{len(shows):,}")
k4.metric("🌍 Countries",       f"{dff['country'].nunique():,}")
if "duration_int" in dff.columns:
    avg_dur = movies["duration_int"].mean()
    k5.metric("⏱️ Avg Movie (min)", f"{avg_dur:.0f}" if pd.notna(avg_dur) else "N/A")
else:
    k5.metric("📅 Year Range", f"{years_range[0]}–{years_range[1]}")

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "🌍 Geography", "🎭 Genres", "📅 Trends", "🔍 Explore"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Overview
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 1])

    # ── Movies vs TV Shows donut ─────────────────────────────────────────────
    with col1:
        st.markdown('<div class="section-title">Movies vs TV Shows</div>', unsafe_allow_html=True)
        type_cnt = dff["type"].value_counts()
        fig = go.Figure(go.Pie(
            labels=type_cnt.index, values=type_cnt.values,
            hole=0.6,
            marker=dict(colors=["#E50914","#ff6b6b"]),
            textinfo="label+percent",
            textfont=dict(color=FONT_CLR, size=13),
        ))
        fig.update_layout(**make_layout(height=350))
        fig.add_annotation(text=f"{len(dff):,}<br>Titles", x=0.5, y=0.5,
                           font=dict(size=20, color=FONT_CLR), showarrow=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Rating distribution ──────────────────────────────────────────────────
    with col2:
        st.markdown('<div class="section-title">Content Rating Distribution</div>', unsafe_allow_html=True)
        rating_cnt = dff["rating"].value_counts().head(10)
        fig2 = go.Figure(go.Bar(
            x=rating_cnt.index, y=rating_cnt.values,
            marker=dict(
                color=rating_cnt.values,
                colorscale=[[0,"#831010"],[1,"#E50914"]],
                showscale=False,
                line=dict(color="#E50914", width=0.5)
            ),
            text=rating_cnt.values, textposition="outside",
            textfont=dict(color=FONT_CLR)
        ))
        fig2.update_layout(**make_layout(height=350))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top Directors ────────────────────────────────────────────────────────
    col3, col4 = st.columns([1,1])
    with col3:
        st.markdown('<div class="section-title">Top 10 Directors</div>', unsafe_allow_html=True)
        top_dir = (dff[dff["director"]!="Unknown"]["director"]
                   .value_counts().head(10).sort_values())
        fig3 = go.Figure(go.Bar(
            x=top_dir.values, y=top_dir.index, orientation="h",
            marker=dict(color=NETFLIX_COLORS[:10], line=dict(width=0)),
            text=top_dir.values, textposition="outside",
            textfont=dict(color=FONT_CLR)
        ))
        fig3.update_layout(**make_layout(height=380))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Movie Duration histogram ─────────────────────────────────────────────
    with col4:
        st.markdown('<div class="section-title">Movie Duration Distribution</div>', unsafe_allow_html=True)
        if "duration_int" in dff.columns:
            dur_data = movies["duration_int"].dropna()
            fig4 = go.Figure(go.Histogram(
                x=dur_data, nbinsx=40,
                marker=dict(color="#E50914", line=dict(color="#831010", width=0.5)),
                opacity=0.85
            ))
            fig4.update_layout(**make_layout(height=380))
            fig4.update_xaxes(title_text="Duration (minutes)")
            fig4.update_yaxes(title_text="Count")
            st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Geography
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Content by Country (Top 20)</div>', unsafe_allow_html=True)

    # Explode multi-country entries
    country_series = (dff["country"]
                      .str.split(",")
                      .explode()
                      .str.strip()
                      .replace("", pd.NA)
                      .dropna())
    country_cnt = country_series.value_counts().head(20)

    fig_geo = px.bar(
        x=country_cnt.values, y=country_cnt.index,
        orientation="h",
        color=country_cnt.values,
        color_continuous_scale=[[0,"#3a0000"],[0.5,"#831010"],[1,"#E50914"]],
        labels={"x":"Titles","y":"Country"}
    )
    fig_geo.update_layout(**make_layout(height=500))
    fig_geo.update_coloraxes(showscale=False)
    fig_geo.update_traces(text=country_cnt.values, textposition="outside",
                          textfont=dict(color=FONT_CLR))
    st.plotly_chart(fig_geo, use_container_width=True)

    # World choropleth
    st.markdown('<div class="section-title">🗺️ Global Footprint</div>', unsafe_allow_html=True)
    country_full = country_series.value_counts().reset_index()
    country_full.columns = ["country","count"]
    fig_map = px.choropleth(
        country_full, locations="country", locationmode="country names",
        color="count", color_continuous_scale=[[0,"#1a1a1a"],[0.3,"#831010"],[1,"#E50914"]],
        hover_name="country", hover_data={"count":True}
    )
    fig_map.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=PAPER_BG, height=420,
        geo=dict(bgcolor=PAPER_BG, showframe=False,
                 landcolor="#2a2a2a", oceancolor=PAPER_BG,
                 showocean=True, showcoastlines=True, coastlinecolor="#444"),
        coloraxis_colorbar=dict(title="Titles", tickfont=dict(color=FONT_CLR)),
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(color=FONT_CLR)
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Genres
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    col_g1, col_g2 = st.columns([1.2, 0.8])

    with col_g1:
        st.markdown('<div class="section-title">Top 15 Genres</div>', unsafe_allow_html=True)
        if "genres" in dff.columns:
            genre_series = dff["genres"].explode().str.strip().replace("", pd.NA).dropna()
            genre_cnt    = genre_series.value_counts().head(15).sort_values()
            fig_gen = go.Figure(go.Bar(
                x=genre_cnt.values, y=genre_cnt.index, orientation="h",
                marker=dict(
                    color=genre_cnt.values,
                    colorscale=[[0,"#831010"],[1,"#E50914"]],
                    showscale=False
                ),
                text=genre_cnt.values, textposition="outside",
                textfont=dict(color=FONT_CLR)
            ))
            fig_gen.update_layout(**make_layout(height=480))
            st.plotly_chart(fig_gen, use_container_width=True)

    with col_g2:
        st.markdown('<div class="section-title">Genre Mix by Type</div>', unsafe_allow_html=True)
        if "genres" in dff.columns:
            genre_type = (dff[["type","genres"]].explode("genres")
                          .assign(genre=lambda d: d["genres"].str.strip()))
            top15 = genre_type["genre"].value_counts().head(12).index.tolist()
            gt_cnt = (genre_type[genre_type["genre"].isin(top15)]
                      .groupby(["genre","type"]).size().reset_index(name="count"))
            fig_gt = px.bar(gt_cnt, x="count", y="genre", color="type",
                            color_discrete_map={"Movie":"#E50914","TV Show":"#ff6b6b"},
                            barmode="stack", orientation="h")
            fig_gt.update_layout(**make_layout(height=480))
            st.plotly_chart(fig_gt, use_container_width=True)

    # Genre heatmap by year
    st.markdown('<div class="section-title">Genre Popularity Over Years</div>', unsafe_allow_html=True)
    if "genres" in dff.columns and "release_year" in dff.columns:
        genre_year = (dff[["release_year","genres"]].explode("genres")
                      .assign(genre=lambda d: d["genres"].str.strip()))
        top10_genres = genre_year["genre"].value_counts().head(10).index.tolist()
        recent_years = list(range(2010, int(dff["release_year"].max())+1))
        hm = (genre_year[genre_year["genre"].isin(top10_genres) &
                         genre_year["release_year"].isin(recent_years)]
              .groupby(["release_year","genre"]).size().reset_index(name="count")
              .pivot(index="genre", columns="release_year", values="count").fillna(0))

        fig_hm = go.Figure(go.Heatmap(
            z=hm.values, x=[str(c) for c in hm.columns], y=hm.index,
            colorscale=[[0,"#1a1a1a"],[0.3,"#831010"],[1,"#E50914"]],
            text=hm.values.astype(int),
            hovertemplate="Year: %{x}<br>Genre: %{y}<br>Titles: %{z}<extra></extra>"
        ))
        fig_hm.update_layout(**make_layout(height=380))
        st.plotly_chart(fig_hm, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Trends
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">📈 Content Added Over the Years</div>', unsafe_allow_html=True)

    if "year_added" in dff.columns:
        yearly = (dff.groupby(["year_added","type"]).size().reset_index(name="count")
                  .dropna(subset=["year_added"]))
        yearly["year_added"] = yearly["year_added"].astype(int)

        fig_trend = px.line(yearly, x="year_added", y="count", color="type",
                            color_discrete_map={"Movie":"#E50914","TV Show":"#ff6b6b"},
                            markers=True, line_shape="spline")
        fig_trend.update_traces(line=dict(width=3))
        fig_trend.update_layout(**make_layout(height=380))
        st.plotly_chart(fig_trend, use_container_width=True)

    col_t1, col_t2 = st.columns(2)

    # Monthly additions heatmap
    with col_t1:
        st.markdown('<div class="section-title">Monthly Additions Pattern</div>', unsafe_allow_html=True)
        if "month_added" in dff.columns and "year_added" in dff.columns:
            month_order = ["January","February","March","April","May","June",
                           "July","August","September","October","November","December"]
            mon_yr = (dff.dropna(subset=["month_added","year_added"])
                      .groupby(["year_added","month_added"]).size().reset_index(name="count"))
            mon_yr["month_added"] = pd.Categorical(mon_yr["month_added"], categories=month_order, ordered=True)
            mon_piv = mon_yr.pivot(index="month_added", columns="year_added", values="count").fillna(0)
            fig_mon = go.Figure(go.Heatmap(
                z=mon_piv.values, x=[str(c) for c in mon_piv.columns],
                y=mon_piv.index.tolist(),
                colorscale=[[0,"#1a1a1a"],[0.5,"#831010"],[1,"#E50914"]]
            ))
            fig_mon.update_layout(**make_layout(height=380))
            st.plotly_chart(fig_mon, use_container_width=True)

    # Release year distribution
    with col_t2:
        st.markdown('<div class="section-title">Release Year vs Added Year Gap</div>', unsafe_allow_html=True)
        if "year_added" in dff.columns:
            df_gap = dff.dropna(subset=["year_added"]).copy()
            df_gap["gap"] = df_gap["year_added"].astype(int) - df_gap["release_year"].astype(int)
            df_gap = df_gap[(df_gap["gap"] >= 0) & (df_gap["gap"] <= 40)]
            fig_gap = go.Figure(go.Histogram(
                x=df_gap["gap"], nbinsx=30,
                marker=dict(color="#E50914", line=dict(color="#831010", width=0.5))
            ))
            fig_gap.update_layout(**make_layout(height=380))
            fig_gap.update_xaxes(title_text="Years Between Release & Netflix Addition")
            st.plotly_chart(fig_gap, use_container_width=True)

    # TV Show seasons distribution
    st.markdown('<div class="section-title">TV Show Season Count Distribution</div>', unsafe_allow_html=True)
    if "duration_int" in dff.columns:
        season_data = shows["duration_int"].dropna()
        fig_seas = go.Figure(go.Bar(
            x=season_data.value_counts().sort_index().index,
            y=season_data.value_counts().sort_index().values,
            marker=dict(color="#E50914"),
            text=season_data.value_counts().sort_index().values,
            textposition="outside", textfont=dict(color=FONT_CLR)
        ))
        fig_seas.update_layout(**make_layout(height=320))
        fig_seas.update_xaxes(title_text="Number of Seasons")
        fig_seas.update_yaxes(title_text="Count")
        st.plotly_chart(fig_seas, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Explore
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">🔍 Search & Filter Titles</div>', unsafe_allow_html=True)

    search_q = st.text_input("Search by Title, Director, or Cast", placeholder="e.g. Dark, Christopher Nolan, Leonardo...")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        sel_type = st.selectbox("Type", ["All"] + dff["type"].unique().tolist())
    with col_e2:
        sel_rating = st.selectbox("Rating", ["All"] + sorted(dff["rating"].dropna().unique().tolist()))

    result = dff.copy()
    if search_q:
        q = search_q.lower()
        result = result[
            result["title"].str.lower().str.contains(q, na=False) |
            result["director"].str.lower().str.contains(q, na=False) |
            result["cast"].str.lower().str.contains(q, na=False)
        ]
    if sel_type != "All":
        result = result[result["type"] == sel_type]
    if sel_rating != "All":
        result = result[result["rating"] == sel_rating]

    st.markdown(f"**{len(result):,} titles found**")
    show_cols = [c for c in ["title","type","release_year","rating","country","duration","listed_in"]
                 if c in result.columns]
    st.dataframe(
        result[show_cols].reset_index(drop=True),
        use_container_width=True, height=450
    )

    # ── Summary Stats ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Dataset Summary</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("**Shape**")
        st.code(f"Rows: {len(df):,}\nColumns: {len(df.columns)}")
    with s2:
        st.markdown("**Null Values (cleaned)**")
        nulls = df[show_cols].isnull().sum()
        st.code(nulls.to_string())
    with s3:
        st.markdown("**Data Types**")
        st.code(df[show_cols].dtypes.to_string())

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-tag">
  🎬 Netflix Content Analytics Dashboard &nbsp;|&nbsp; 
  Built with Streamlit + Plotly &nbsp;|&nbsp; 
  Ritu Panchal &nbsp;|&nbsp; 
  <a href='https://github.com/RituPanchal05/Netflix_Data_Analytics' 
     style='color:#E50914;'>GitHub</a>
</div>
""", unsafe_allow_html=True)