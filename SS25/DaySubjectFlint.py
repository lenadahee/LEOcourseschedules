import json 
import requests
import streamlit as st
import pandas as pd


url = "https://raw.githubusercontent.com/umsi-amadaman/LEOcourseschedules/main/UMICHbuildings_dict.json"
response = requests.get(url)
new_Bldgs = json.loads(response.text)



DATA = 'https://github.com/umsi-amadaman/LEOcourseschedules/raw/main/SS25/Flint_S25.csv'
#https://github.com/umsi-amadaman/LEOcourseschedules/blob/main/W25/A2SchedW25.csv

sched = pd.read_csv(DATA)

#Breakout Room and Building
sched['Room'] = sched['Facility ID'].str.rsplit(' ', n=1).str[0]
sched['Bldg'] = sched['Facility Desccr'].str.rsplit(' ', n=1).str[-1]

monthlydata = 'https://github.com/umsi-amadaman/LEOcourseschedules/raw/main/W25/LEOmonthly_Jan25.csv'


monthly = pd.read_csv(monthlydata)

IGNORED = '''
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
'''

# Title of the app
st.title('Flint Schedule Viewer by Day - Subject')

# Create a dropdown for days of the week
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
selected_day = st.selectbox('Select a day of the week:', days)

DaysOfWeek = {'Monday':'Mon', 'Tuesday':'Tues', 'Wednesday':'Wed', 'Thursday':'Thurs', 'Friday':'Fri', 'Saturday':'Sat', 'Sunday':'Sun'}

selDay = DaysOfWeek[selected_day]

# Filter the DataFrame based on the selected day
# Assuming you have a 'Day' column in your DataFrame
day_filtered_df = sched[sched[selDay] == 'X']






#st.write("Available columns:", list(day_filtered_df.columns))
#st.write("Number of rows:", len(day_filtered_df))
#st.write("First few rows:", day_filtered_df.head())

# Create a dropdown for subjects
subject_counts = day_filtered_df['Subject'].value_counts().to_dict()
subject_options = [f"{subject} ({count})" for subject, count in subject_counts.items()]
selected_subject_option = st.selectbox('Select a subject:', subject_options)

# Extract the subject name from the selected option
selected_subject = selected_subject_option.split(' (')[0]

# Filter the DataFrame based on the selected subject
subject_filtered_df = day_filtered_df[day_filtered_df['Subject'] == selected_subject]

final_df = subject_filtered_df

# Sort the final_df by BldgPrediction
final_df = final_df

final_df = final_df.drop(columns=['Class Nbr'])
#st.write("Available columns in final_df:", list(final_df.columns))

final_df = final_df[['Meeting Time Start', 'Meeting Time End','Room', 'Bldg', 'Class Instr Name', 'Crse Descr', 'Subject',
       'Catalog Nbr',
       #'Class Nbr',
       'Meeting Start Dt', 'Meeting EndDt',
       'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']]

### we're not looking up lecs like we do for A2... so you gotta get their appt info yourself

IGNORE2 = '''
final_df = final_df[['Meeting Time Start', 'Meeting Time End','Room', 'Bldg', 'Crse Descr', 'Subject',
       'Catalog Nbr', 'Class Section', 'Class Instr Name', 'UM ID', 'Job Title', 
       'Appointment Start Date', 'FTE', 'Department Name', 'Deduction' ,
       'Class Nbr',
       'Instruction Mode Descrshort', 'Meeting Start Dt', 'Meeting EndDt',
       'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']]
'''
final_df['Meeting Time Start'] = pd.to_datetime(final_df['Meeting Time Start'], errors='coerce').dt.strftime('%H:%M')
final_df['Meeting Time End'] = pd.to_datetime(final_df['Meeting Time End'], errors='coerce').dt.strftime('%H:%M')


# Display the final filtered DataFrame
st.write(f"Showing schedule for {selected_subject} for {selected_day}:")
st.dataframe(final_df)

# Optional: Display unique buildings for this selection
#unique_buildings = final_df['Bldg'].unique()
#st.write(f"Buildings used: {', '.join(Bldg)}")

#st.write("Columns right before display:", final_df.columns)
#st.write("Sample of UM ID values:", final_df['UM ID'].head())
