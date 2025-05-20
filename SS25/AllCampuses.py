import streamlit as st
import pandas as pd
import json
import requests

# ---------- Utilities ----------
@st.cache_data
def load_buildings():
    url = "https://raw.githubusercontent.com/umsi-amadaman/LEOcourseschedules/main/UMICHbuildings_dict.json"
    response = requests.get(url)
    return json.loads(response.text)

@st.cache_data
def load_monthly():
    url = "https://github.com/umsi-amadaman/LEOcourseschedules/raw/main/W25/LEOmonthly_Jan25.csv"
    return pd.read_csv(url)

# ---------- Campus-Specific Functions ----------
def show_ann_arbor():
    st.header("Ann Arbor Schedule by Day and Subject")
    df = pd.read_csv("A2_S25.csv")
    monthly = load_monthly()

    # Merge
    df['Class Instr ID'] = pd.to_numeric(df['Class Instr ID'], errors='coerce')
    monthly['UM ID'] = pd.to_numeric(monthly['UM ID'], errors='coerce')
    df = df.dropna(subset=['Class Instr ID'])
    monthly = monthly.dropna(subset=['UM ID'])
    df['Class Instr ID'] = df['Class Instr ID'].astype(float)
    merged_df = df.merge(monthly, left_on='Class Instr ID', right_on='UM ID', how='left')

    # Filter by Day and Subject
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    sel_day = st.selectbox("Select Day", days)
    day_map = {'Monday':'Mon','Tuesday':'Tues','Wednesday':'Wed','Thursday':'Thurs','Friday':'Fri'}
    day_df = merged_df[merged_df[day_map[sel_day]] == 'Y']

    subject_opts = sorted(day_df['Subject'].dropna().unique().tolist())
    sel_subj = st.selectbox("Select Subject", ["All"] + subject_opts)

    if sel_subj != "All":
        day_df = day_df[day_df['Subject'] == sel_subj]

    st.dataframe(day_df)
    st.write(f"Total classes: {len(day_df)}")


def show_dearborn():
    st.header("Dearborn Schedule by Day and Subject")
    df = pd.read_csv("Dearborn_S25.csv")

    # Filter by day (uses 'Monday Indicator', etc.)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    day_keys = {
        'Monday': 'Monday Indicator',
        'Tuesday': 'Tuesday Indicator',
        'Wednesday': 'Wednesday Indicator',
        'Thursday': 'Thursday Indicator',
        'Friday': 'Friday Indicator'
    }
    sel_day = st.selectbox("Select Day", days)
    df_day = df[df[day_keys[sel_day]].isin(['M', 'T', 'W', 'R', 'F', 'X'])]

    subject_opts = sorted(df_day['Subject'].dropna().unique().tolist())
    sel_subj = st.selectbox("Select Subject", ["All"] + subject_opts)

    if sel_subj != "All":
        df_day = df_day[df_day['Subject'] == sel_subj]

    st.dataframe(df_day)
    st.write(f"Total classes: {len(df_day)}")


def show_flint():
    st.header("Flint Schedule by Day and Subject")
    df = pd.read_csv("Flint_S25.csv")

    # Filter by Day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    dow_map = {'Monday':'Mon','Tuesday':'Tues','Wednesday':'Wed','Thursday':'Thurs','Friday':'Fri'}
    sel_day = st.selectbox("Select Day", days)
    df_day = df[df[dow_map[sel_day]] == 'X']

    subject_opts = sorted(df_day['Subject'].dropna().unique().tolist())
    sel_subj = st.selectbox("Select Subject", ["All"] + subject_opts)

    if sel_subj != "All":
        df_day = df_day[df_day['Subject'] == sel_subj]

    st.dataframe(df_day)
    st.write(f"Total classes: {len(df_day)}")

# ---------- Main App ----------
st.title("UM Schedule Explorer")
campus = st.selectbox("Select a Campus", ["Ann Arbor", "Dearborn", "Flint"])

if campus == "Ann Arbor":
    show_ann_arbor()
elif campus == "Dearborn":
    show_dearborn()
elif campus == "Flint":
    show_flint()
