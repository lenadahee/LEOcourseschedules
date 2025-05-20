import json 
import requests
import streamlit as st
import pandas as pd


url = "https://raw.githubusercontent.com/umsi-amadaman/LEOcourseschedules/main/UMICHbuildings_dict.json"
response = requests.get(url)
new_Bldgs = json.loads(response.text)



DATA = 'https://github.com/umsi-amadaman/LEOcourseschedules/raw/main/SS25/A2_S25.csv'
#https://github.com/umsi-amadaman/LEOcourseschedules/blob/main/W25/A2SchedW25.csv

sched = pd.read_csv(DATA)

monthlydata = 'https://github.com/umsi-amadaman/LEOcourseschedules/raw/main/W25/LEOmonthly_Jan25.csv'


monthly = pd.read_csv(monthlydata)


# Convert 'Class Instr ID' in sched to numeric, setting errors='coerce' to handle non-numeric values
sched['Class Instr ID'] = pd.to_numeric(sched['Class Instr ID'], errors='coerce')
monthly['UM ID'] = pd.to_numeric(monthly['UM ID'], errors='coerce')

# Drop rows with NaN in 'Class Instr ID' or 'UM ID'
sched = sched.dropna(subset=['Class Instr ID']).copy()
monthly = monthly.dropna(subset=['UM ID']).copy()

# Convert columns to float explicitly using .loc
sched.loc[:, 'Class Instr ID'] = sched['Class Instr ID'].astype(float)
monthly.loc[:, 'UM ID'] = monthly['UM ID'].astype(float)

# Perform an inner join, matching 'Class Instr ID' from sched with 'UM ID' from monthly
merged_df = sched.merge(
    monthly[['UM ID', 'Job Title', 'Appointment Start Date', 'FTE', 'Department Name', 'Deduction']],
    left_on='Class Instr ID',
    right_on='UM ID',
    how='inner'
)

# Drop the redundant 'UM ID' column from the result
sched = merged_df.drop(columns=['Class Instr ID'])
sched['UM ID'] = sched['UM ID'].apply(lambda x: f"{x:.0f}")


def find_longest_match(string, key_list):
    matches = [key for key in key_list if string in key or key in string]
    return max(matches, key=len, default=None)

# Create new columns with default values
sched['RoomPrediction'] = ''
sched['BldgPrediction'] = ''
sched['CampusPrediction'] = ''

# Iterate through unique Facility IDs
for x in sched['Facility ID'].unique():
    # Check if x is a string AND not just whitespace
    if isinstance(x, str) and x.strip():  # Added .strip() check here
        match = find_longest_match(x, new_Bldgs.keys())
        if match:
            # Remove the matched part from the original string
            remaining = x.replace(match, '').strip()
            
            # Update the DataFrame for all rows with this Facility ID
            mask = sched['Facility ID'] == x
            sched.loc[mask, 'RoomPrediction'] = remaining
            sched.loc[mask, 'BldgPrediction'] = match
            sched.loc[mask, 'CampusPrediction'] = new_Bldgs[match][-1]
        else:
            # If no match, set only RoomPrediction to the original string
            mask = sched['Facility ID'] == x
            sched.loc[mask, 'BldgPrediction'] = x

# After the loop, fill NaN values if any
sched['RoomPrediction'] = sched['RoomPrediction'].fillna('')
sched['BldgPrediction'] = sched['BldgPrediction'].fillna('')
sched['CampusPrediction'] = sched['CampusPrediction'].fillna('')


# Title of the app
st.title('Ann Arbor Schedule Viewer by Day - Subject - Campus')

# Create a dropdown for days of the week
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
selected_day = st.selectbox('Select a day of the week:', days)

DaysOfWeek = {'Monday':'Mon', 'Tuesday':'Tues', 'Wednesday':'Wed', 'Thursday':'Thurs', 'Friday':'Fri', 'Saturday':'Sat', 'Sunday':'Sun'}

selDay = DaysOfWeek[selected_day]

# Filter the DataFrame based on the selected day
# Assuming you have a 'Day' column in your DataFrame
day_filtered_df = sched[sched[selDay] == 'Y']







# Create a dropdown for subjects
subject_counts = day_filtered_df['Subject'].value_counts().to_dict()
subject_options = [f"{subject} ({count})" for subject, count in subject_counts.items()]
selected_subject_option = st.selectbox('Select a subject:', subject_options)

# Extract the subject name from the selected option
selected_subject = selected_subject_option.split(' (')[0]

# Filter the DataFrame based on the selected subject
subject_filtered_df = day_filtered_df[day_filtered_df['Subject'] == selected_subject]

# Create a dropdown for campuses
campus_counts = subject_filtered_df['CampusPrediction'].value_counts().to_dict()
campus_options = [f"{campus} ({count})" for campus, count in campus_counts.items()]
selected_campus_option = st.selectbox('Select a campus:', campus_options)

# Extract the campus name from the selected option
selected_campus = selected_campus_option.split(' (')[0]

# Filter the DataFrame based on the selected campus
final_df = subject_filtered_df[subject_filtered_df['CampusPrediction'] == selected_campus]

# Sort the final_df by BldgPrediction
final_df = final_df.sort_values(by='BldgPrediction')

final_df = final_df.drop(columns=['Class Nbr'])

final_df = final_df[['Meeting Time Start', 'Meeting Time End','RoomPrediction', 'BldgPrediction', 'Crse Descr', 'Subject',
       'Catalog Nbr', 'Class Section', 'Class Instr Name', 'UM ID', 'Job Title', 
       'Appointment Start Date', 'FTE', 'Department Name', 'Deduction' ,
       'Class Mtg Nbr', 'Facility ID', 'Facility Descr',
       'Instruction Mode Descrshort', 'Meeting Start Dt', 'Meeting End Dt',
       'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun', 'CampusPrediction']]

final_df['Meeting Time Start'] = pd.to_datetime(final_df['Meeting Time Start'], errors='coerce').dt.strftime('%H:%M')
final_df['Meeting Time End'] = pd.to_datetime(final_df['Meeting Time End'], errors='coerce').dt.strftime('%H:%M')


# Display the final filtered DataFrame
st.write(f"Showing schedule for {selected_subject} on {selected_campus} campus for {selected_day}:")
st.dataframe(final_df)

# Optional: Display unique buildings for this selection
unique_buildings = final_df['BldgPrediction'].unique()
st.write(f"Buildings used: {', '.join(unique_buildings)}")

#st.write("Columns right before display:", final_df.columns)
#st.write("Sample of UM ID values:", final_df['UM ID'].head())
