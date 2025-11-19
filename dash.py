# ===========================================
# IPL FULL EDA DASHBOARD - ADVANCED VERSION
# ===========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="IPL EDA Dashboard", layout="wide")

# -------------------------------
# PATHS TO YOUR IPL DATA FILES
# -------------------------------
DATA_MATCHES = r"C:\Users\KUNAL\Downloads\dataset_ipl\IPL Matches 2008-2020.csv"
DATA_BALLS   = r"C:\Users\KUNAL\Downloads\dataset_ipl\IPL Ball-by-Ball 2008-2020.csv"


# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    matches = pd.read_csv(DATA_MATCHES)
    balls = pd.read_csv(DATA_BALLS)

    matches.columns = matches.columns.str.strip()
    balls.columns = balls.columns.str.strip()

    if 'date' in matches.columns:
        matches['date'] = pd.to_datetime(matches['date'], errors='ignore')

    if 'season' not in matches.columns:
        matches['season'] = matches['date'].dt.year

    if 'is_wicket' not in balls.columns:
        balls['is_wicket'] = balls['dismissal_kind'].notna().astype(int)

    return matches, balls


matches, balls = load_data()

# ---------------------------------------------
# CREATE TABS FOR MULTIPLE ANALYSIS SECTIONS
# ---------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Season & Matches Overview",
    "👥 Players Analysis",
    "🏏 Batting Breakdown",
    "🎯 Bowling Breakdown",
    "📊 Venue / Toss / Extra Insights"
])

# =============================================================
# TAB 1: SEASON & MATCHES OVERVIEW
# =============================================================
with tab1:
    st.title("🏆 IPL Matches & Season Overview")

    # Matches per season
    matches_per_season = matches.groupby('season').size().reset_index(name='matches')
    fig = px.bar(matches_per_season, x='season', y='matches',
                 title="Matches Played Per Season")
    st.plotly_chart(fig, use_container_width=True)

    # Matches per venue
    venue = matches['venue'].value_counts().reset_index()
    venue.columns = ['venue', 'matches']
    fig = px.bar(venue.head(20), x='venue', y='matches',
                 title="Top 20 Most Played Venues")
    st.plotly_chart(fig, use_container_width=True)

    # Win by runs distribution
    if 'win_by_runs' in matches.columns:
        fig = px.histogram(matches, x='win_by_runs', nbins=40,
                           title="Distribution of Victory Margin (Runs)")
        st.plotly_chart(fig, use_container_width=True)

    # Win by wickets
    if 'win_by_wickets' in matches.columns:
        fig = px.histogram(matches, x='win_by_wickets', nbins=20,
                           title="Distribution of Victory Margin (Wickets)")
        st.plotly_chart(fig, use_container_width=True)

    # Top winning teams
    winners = matches['winner'].value_counts().reset_index()
    winners.columns = ['team', 'wins']
    fig = px.bar(winners, x='team', y='wins', title="Most Successful Teams")
    st.plotly_chart(fig, use_container_width=True)


# =============================================================
# TAB 2: PLAYER ANALYSIS
# =============================================================
with tab2:
    st.title("👥 Player Performance Analysis")

    # Most Player of the Match awards
    if 'player_of_match' in matches.columns:
        pom = matches['player_of_match'].value_counts().head(20).reset_index()
        pom.columns = ['player', 'awards']
        fig = px.bar(pom, x='player', y='awards', title="Top 20 Player of the Match Winners")
        st.plotly_chart(fig, use_container_width=True)

    # Most runs
    runs = balls.groupby('batsman')['batsman_runs'].sum().reset_index()
    runs = runs.sort_values('batsman_runs', ascending=False)
    fig = px.bar(runs.head(20), x='batsman', y='batsman_runs',
                 title="Top 20 Run Scorers")
    st.plotly_chart(fig, use_container_width=True)

    # Most wickets
    wk = balls[balls['is_wicket'] == 1].groupby('bowler').size().reset_index(name='wickets')
    wk = wk.sort_values('wickets', ascending=False)
    fig = px.bar(wk.head(20), x='bowler', y='wickets',
                 title="Top 20 Wicket Takers")
    st.plotly_chart(fig, use_container_width=True)


# =============================================================
# TAB 3: BATTING ANALYSIS
# =============================================================
with tab3:
    st.title("🏏 Batting Detailed Analysis")

    # Boundary count
    balls['is_four'] = (balls['batsman_runs'] == 4).astype(int)
    balls['is_six'] = (balls['batsman_runs'] == 6).astype(int)

    boundary = balls.groupby('batsman')[['is_four', 'is_six']].sum().reset_index()
    boundary = boundary.sort_values('is_six', ascending=False)

    fig = px.bar(boundary.head(20), x='batsman', y='is_six',
                 title="Top 20 Six Hitters")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(boundary.head(20), x='batsman', y='is_four',
                 title="Top 20 Four Hitters")
    st.plotly_chart(fig, use_container_width=True)

    # Strike rate
    balls['ball_faced'] = 1
    sr = balls.groupby('batsman').agg({'batsman_runs': 'sum', 'ball_faced': 'count'}).reset_index()
    sr['strike_rate'] = sr['batsman_runs'] / sr['ball_faced'] * 100
    sr = sr.sort_values('strike_rate', ascending=False)

    fig = px.bar(sr.head(20), x='batsman', y='strike_rate',
                 title="Highest Strike Rate (Min Balls Faced = 200)")
    st.plotly_chart(fig, use_container_width=True)

    # Runs per over
    ro = balls.groupby('over')['total_runs'].sum().reset_index()
    fig = px.line(ro, x='over', y='total_runs',
                  title="Runs Scored Per Over")
    st.plotly_chart(fig, use_container_width=True)


# =============================================================
# TAB 4: BOWLING ANALYSIS
# =============================================================
with tab4:
    st.title("🎯 Bowling Detailed Analysis")

    # Dismissal types
    if 'dismissal_kind' in balls.columns:
        dis = balls['dismissal_kind'].value_counts().reset_index()
        dis.columns = ['dismissal', 'count']
        fig = px.pie(dis, names='dismissal', values='count',
                     title="Types of Dismissals")
        st.plotly_chart(fig, use_container_width=True)

    # Economy rate
    balls['runs_conceded'] = balls['total_runs']
    eco = balls.groupby('bowler').agg({'runs_conceded': 'sum', 'ball_faced': 'count'}).reset_index()
    eco['economy'] = eco['runs_conceded'] / (eco['ball_faced'] / 6)
    eco = eco.sort_values('economy')

    fig = px.bar(eco.head(20), x='bowler', y='economy',
                 title="Top Economy Bowlers (Best)")
    st.plotly_chart(fig, use_container_width=True)

    # Overs with most wickets
    w_over = balls[balls['is_wicket'] == 1].groupby('over').size().reset_index(name='wickets')
    fig = px.line(w_over, x='over', y='wickets', title="Wickets Per Over")
    st.plotly_chart(fig, use_container_width=True)


# =============================================================
# TAB 5: VENUE, TOSS & EXTRAS
# =============================================================
with tab5:
    st.title("📊 Venue, Toss & Extra Statistics")

    # Toss winner → Match winner
    if {'toss_winner', 'winner'}.issubset(matches.columns):
        toss = matches.groupby('toss_winner').apply(lambda x: (x['toss_winner'] == x['winner']).sum()).reset_index()
        toss.columns = ['team', 'toss_win_match_win']
        fig = px.bar(toss, x='team', y='toss_win_match_win',
                     title="Teams Winning Toss & Match")
        st.plotly_chart(fig, use_container_width=True)

    # Toss decision trends
    if 'toss_decision' in matches.columns:
        toss_dec = matches['toss_decision'].value_counts().reset_index()
        toss_dec.columns = ['decision', 'count']
        fig = px.pie(toss_dec, names='decision', values='count',
                     title="Toss Decision: Bat vs Field")
        st.plotly_chart(fig, use_container_width=True)

    # Extra runs distribution
    if 'extra_runs' in balls.columns:
        fig = px.histogram(balls, x='extra_runs', nbins=15,
                           title="Distribution of Extra Runs")
        st.plotly_chart(fig, use_container_width=True)

    # Extra type breakdown
    if 'extra_type' in balls.columns:
        extra_type = balls['extra_type'].value_counts().reset_index()
        extra_type.columns = ['type', 'count']
        fig = px.bar(extra_type, x='type', y='count',
                     title="Type of Extras")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Full IPL Dashboard — Generated with ChatGPT")
