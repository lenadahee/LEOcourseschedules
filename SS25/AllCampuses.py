import streamlit as st
import pandas as pd
import json
import requests

# ---------- Load Data ----------

@st.cache_data
def load_buildings():
    url = "https://raw.githubusercontent.com/umsi-amadaman/LEOcourseschedules/main/UMICHbuildings_dict.json"
    response = requests.get(url)
    return json.loads(response.text)

@st.cache_data
def load_schedule(file_path, campus_name):
    df = pd.read_csv(file_path)
    df["Campus"] = campus_name
    return df

@st.cache_data
def load_monthly():
    url = "https://github.com/umsi-amadaman/LEOcourseschedules/raw/main/W25/LEOmonthly_Jan25.csv"
    return pd.read_csv(url)


def merge_data(sched, monthly):
    sched["Class Instr ID"] = pd.to_numeric(sched["Class Instr ID"], errors="coerce")
    monthly["UM ID"] = pd.to_numeric(monthly["UM ID"], errors="coerce")
    sched.dropna(subset=["Class Instr ID"], inplace=True)
    monthly.dropna(subset=["UM ID"], inplace=True)
    sched["Class Instr ID"] = sched["Class Instr ID"].astype(float)
    monthly["UM ID"] = monthly["UM ID"].astype(float)
    merged = sched.merge(
        monthly[["UM ID", "Job Title", "Appointment Start Date", "FTE", "Department Name", "Deduction"]],
        left_on="Class Instr ID",
        right_on="UM ID",
        how="left"
    )
    merged["UM ID"] = merged["UM ID"].apply(lambda x: f"{x:.0f}" if pd.notnull(x) else "")
    return merged

def find_longest_match(string, key_list):
    matches = [key for key in key_list if string in key or key in string]
    return max(matches, key=len, default=None)

def predict_buildings(df, bldg_dict):
    bldg_keys = list(bldg_dict.keys())
    def extract_info(fac):
        if not isinstance(fac, str) or not fac.strip():
            return '', '', ''
        match = find_longest_match(fac, bldg_keys)
        if match:
            remaining = fac.replace(match, '').strip()
            return remaining, match, bldg_dict[match][-1]
        return fac, '', ''
    preds = df['Facility ID'].apply(extract_info)
    df[['RoomPrediction', 'BldgPrediction', 'CampusPrediction']] = pd.DataFrame(preds.tolist(), index=df.index)
    return df

def format_times(df):
    df['Meeting Time Start'] = pd.to_datetime(df['Meeting Time Start'], errors='coerce').dt.strftime('%H:%M')
    df['Meeting Time End'] = pd.to_datetime(df['Meeting Time End'], errors='coerce').dt.strftime('%H:%M')
    return df

# ---------- Load Everything ----------

bldg_dict = load_buildings()
monthly = load_monthly()

sched_AA = load_schedule("A2_S25.csv", "Ann Arbor")
sched_DB = load_schedule("Dearborn_S25.csv", "Dearborn")
sched_FL = load_schedule("Flint_S25.csv", "Flint")

combined_sched = pd.concat([sched_AA, sched_DB, sched_FL], ignore_index=True)
combined_sched = merge_data(combined_sched, monthly)
combined_sched = predict_buildings(combined_sched, bldg_dict)

# ---------- UI: Filters ----------

st.title("Combined Class Schedules: All UM Campuses")

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_map = {'Monday':'Mon','Tuesday':'Tues','Wednesday':'Wed','Thursday':'Thurs','Friday':'Fri','Saturday':'Sat','Sunday':'Sun'}
sel_day = st.selectbox("Select a Day of the Week", days)
filtered = combined_sched[combined_sched[dow_map[sel_day]] == 'Y']

# Campus filter
campus_opts = ["ALL"] + sorted(filtered["Campus"].unique().tolist())
sel_campus = st.selectbox("Select a Campus (or ALL)", campus_opts)
if sel_campus != "ALL":
    filtered = filtered[filtered["Campus"] == sel_campus]

# Building filter
bldg_opts = ["ALL"] + sorted(filtered["BldgPrediction"].dropna().unique().tolist())
sel_bldg = st.selectbox("Select a Building (or ALL)", bldg_opts)
if sel_bldg != "ALL":
    filtered = filtered[filtered["BldgPrediction"] == sel_bldg]

# Format + Display
filtered = format_times(filtered)
filtered = filtered.drop(columns=['Class Nbr'], errors='ignore')
display_cols = [
    'Meeting Time Start', 'Meeting Time End', 'RoomPrediction', 'BldgPrediction', 'CampusPrediction', 'Campus',
    'Crse Descr', 'Subject', 'Catalog Nbr', 'Class Section', 'Class Instr Name', 'UM ID',
    'Job Title', 'Appointment Start Date', 'FTE', 'Department Name', 'Deduction',
    'Class Mtg Nbr', 'Facility ID', 'Facility Descr',
    'Instruction Mode Descrshort', 'Meeting Start Dt', 'Meeting End Dt',
    'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'
]
st.write(f"### Schedule for {sel_day}{' - ' + sel_campus if sel_campus != 'ALL' else ''}{' - ' + sel_bldg if sel_bldg != 'ALL' else ''}")
st.dataframe(filtered[display_cols])

# Download
st.download_button(
    label="📥 Download filtered schedule as CSV",
    data=filtered.to_csv(index=False).encode('utf-8'),
    file_name=f"{sel_day}_{sel_campus}_{sel_bldg}_schedule.csv".replace(' ', '_'),
    mime='text/csv'
)

st.write(f"**Total classes shown:** {len(filtered)}")
