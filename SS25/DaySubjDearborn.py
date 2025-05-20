import json 
import requests
import streamlit as st
import pandas as pd


url = "https://raw.githubusercontent.com/umsi-amadaman/LEOcourseschedules/main/UMICHbuildings_dict.json"
response = requests.get(url)
new_Bldgs = json.loads(response.text)



DATA = 'https://github.com/umsi-amadaman/LEOcourseschedules/raw/main/SS25/Dearborn_S25.csv'
#https://github.com/umsi-amadaman/LEOcourseschedules/blob/main/W25/A2SchedW25.csv

sched = pd.read_csv(DATA)

#Breakout Room and Building
sched['Room'] = sched['Room Code']
sched['Bldg'] = sched['Building Code']

monthlydata = 'https://github.com/umsi-amadaman/LEOcourseschedules/raw/main/W25/LEOmonthly_Jan25.csv'


monthly = pd.read_csv(monthlydata)

# Convert Primary Instructor ID to numeric (int64) to match Monthly's UM ID
sched['Primary Instructor ID'] = pd.to_numeric(sched['Primary Instructor ID'], errors='coerce')

# Create a filter for rows where Primary Instructor ID exists in Monthly's UM ID
valid_ids = sched['Primary Instructor ID'].isin(monthly['UM ID'])

# Apply the filter to sched
sched = sched[valid_ids]

# Title of the app
st.title('Dearborn Schedule Viewer by Day - Subject')

# Create a dropdown for days of the week
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
selected_day = st.selectbox('Select a day of the week:', days)

DaysOfWeek = {'Monday':'Monday Indicator', 'Tuesday':'Tuesday Indicator', 'Wednesday':'Wednesday Indicator', 'Thursday':'Thursday Indicator', 'Friday':'Friday Indicator', 'Saturday':'Saturday Indicator', 'Sunday':'Sunday Indicator'}

selDay = DaysOfWeek[selected_day]

# Filter the DataFrame based on the selected day
# Assuming you have a 'Day' column in your DataFrame
day_filtered_df = sched[sched[selDay].isin(['M', 'T', 'W', 'R', 'F'])]






#st.write("Available columns:", list(day_filtered_df.columns))
#st.write("Number of rows:", len(day_filtered_df))
#st.write("First few rows:", day_filtered_df.head())

# Create a dropdown for subjects
subject_counts = day_filtered_df['Subject'].value_counts().to_dict()
subject_options = [f"{subject} ({count})" for subject, count in subject_counts.items()]
subject_options.insert(0, f"All ({len(day_filtered_df)})")
selected_subject_option = st.selectbox('Select a subject:', subject_options)

# Extract the subject name from the selected option
selected_subject = selected_subject_option.split(' (')[0]

# Apply subject filter if NOT "All"
if selected_subject != 'All':
    subject_filtered_df = day_filtered_df[day_filtered_df['Subject'] == selected_subject]
else:
    subject_filtered_df = day_filtered_df

final_df = subject_filtered_df

# Sort the final_df by BldgPrediction
#final_df = final_df

#final_df = final_df.drop(columns=['Class Nbr'])
#st.write("Available columns in final_df:", list(final_df.columns))


final_df = final_df[['Meeting Time Start', 'Meeting Time End','Room Code', 'Building Code', 'Primary Instructor Last Name',
                     'Primary Instructor First Name', 'Subject','Class Nbr', 'Class Section',
       'Term Start Date', 'Term End Date',
        'Monday Indicator', 'Tuesday Indicator', 'Wednesday Indicator', 
                     'Thursday Indicator', 'Friday Indicator', 'Saturday Indicator', 'Sunday Indicator', 'Instructional Mode']]

### we're not looking up lecs like we do for A2... so you gotta get their appt info yourself
IGNORE ='''
final_df['Meeting Time Start'] = pd.to_datetime(final_df['Meeting Time Start'], errors='coerce').dt.strftime('%H:%M')
final_df['Meeting Time End'] = pd.to_datetime(final_df['Meeting Time End'], errors='coerce').dt.strftime('%H:%M')


# Display the final filtered DataFrame
st.write(f"Showing schedule for {selected_subject} for {selected_day}:")
st.dataframe(final_df)
'''
# Add a dropdown for instruction mode
instruction_modes = sorted(final_df['Instructional Mode'].dropna().unique())
selected_mode = st.selectbox('Filter by Instruction Mode:', options=['All'] + list(instruction_modes))

# Filter by selected instruction mode
if selected_mode != 'All':
    final_df = final_df[final_df['Instructional Mode'] == selected_mode]

# Format times
#final_df['Meeting Time Start'] = pd.to_datetime(final_df['Meeting Time Start'], errors='coerce').dt.strftime('%H:%M')
#final_df['Meeting Time End'] = pd.to_datetime(final_df['Meeting Time End'], errors='coerce').dt.strftime('%H:%M')

# Display the final filtered DataFrame with mode information
mode_text = f" ({selected_mode} mode)" if selected_mode != 'All' else " (all modes)"
st.write(f"Showing schedule for {selected_subject} for {selected_day}{mode_text}:")
st.dataframe(final_df)

