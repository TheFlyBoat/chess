import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds_dict = {
    "type": st.secrets["GOOGLE_SHEETS_KEY_TYPE"],
    "project_id": st.secrets["GOOGLE_SHEETS_KEY_PROJECT_ID"],
    "private_key_id": st.secrets["GOOGLE_SHEETS_KEY_PRIVATE_KEY_ID"],
    "private_key": st.secrets["GOOGLE_SHEETS_KEY_PRIVATE_KEY"],
    "client_email": st.secrets["GOOGLE_SHEETS_KEY_CLIENT_EMAIL"],
    "client_id": st.secrets["GOOGLE_SHEETS_KEY_CLIENT_ID"],
    "auth_uri": st.secrets["GOOGLE_SHEETS_KEY_AUTH_URI"],
    "token_uri": st.secrets["GOOGLE_SHEETS_KEY_TOKEN_URI"],
    "auth_provider_x509_cert_url": st.secrets["GOOGLE_SHEETS_KEY_AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": st.secrets["GOOGLE_SHEETS_KEY_CLIENT_X509_CERT_URL"],
    "universe_domain": st.secrets["GOOGLE_SHEETS_KEY_UNIVERSE_DOMAIN"],
}

creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("Chess Championship Data").sheet1

# Title and Introduction
st.title('Chess Championship Tracker')
st.write("""
Welcome to the Chess Championship Tracker!
Use this application to save and track the scores of your chess matches.
Create championships, log match results, and compare overall scores between players.
""")

# Sidebar Setup
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the options below to explore the app.")

# Initialising session state to store data
if 'championships' not in st.session_state:
    st.session_state['championships'] = []
    rows = sheet.get_all_records(expected_headers=["Championship Name", "Winner", "Winner Colour", "Date"])
    for row in rows:
        if row['Championship Name'] not in [c['name'] for c in st.session_state['championships']]:
            st.session_state['championships'].append({
                'name': row['Championship Name'],
                'matches': []
            })
        for champ in st.session_state['championships']:
            if champ['name'] == row['Championship Name']:
                champ['matches'].append({
                    'winner': row['Winner'],
                    'colour': row['Winner Colour'],
                    'date': row['Date']
                })

# Adding a new championship
st.sidebar.header("Add New Championship")
championship_name = st.sidebar.text_input("Championship Name")
player_name_1 = st.sidebar.text_input("Player 1 Name", value="User 1")
player_name_2 = st.sidebar.text_input("Player 2 Name", value="User 2")

if st.sidebar.button("Create Championship") and championship_name:
    st.session_state['championships'].append({
        'name': championship_name,
        'matches': []
    })
    sheet.append_row([championship_name, "", "", ""])
    st.sidebar.success(f"Championship '{championship_name}' created!")

# Selecting a Championship
if st.session_state['championships']:
    st.sidebar.header("Select Championship")
    selected_championship = st.sidebar.selectbox("Select Championship", [c['name'] for c in st.session_state['championships']])
    championship = next(c for c in st.session_state['championships'] if c['name'] == selected_championship)
    
    st.sidebar.header("Log Match Result")
    winner = st.sidebar.selectbox("Winner", [player_name_1, player_name_2, "User 3"])
    colour = st.sidebar.selectbox("Winner's Colour", ["White", "Black"])
    match_date = st.sidebar.date_input("Match Date", value=datetime.date.today())
    if st.sidebar.button("Save Match Result"):
        championship['matches'].append({
            'winner': winner,
            'colour': colour,
            'date': match_date
        })
        sheet.append_row([selected_championship, winner, colour, str(match_date)])

        st.sidebar.success(f"Match result saved for championship '{selected_championship}'!")

    st.write(f"### Championship: {selected_championship}")
    if championship['matches']:
        match_data = pd.DataFrame(championship['matches'])
        st.write("### Match Results:")
        st.write(match_data)

    if st.checkbox("Show Overall Statistics for Selected Championship"):
        player_wins = match_data['winner'].value_counts()
        st.write("### Overall Statistics for Selected Championship:")
        for player, wins in player_wins.items():
            st.write(f"{player} Wins: {wins}")

    if st.checkbox("Show Overall Statistics Across All Championships"):
        all_matches = []
        for champ in st.session_state['championships']:
            all_matches.extend(champ['matches'])
        if all_matches:
            all_matches_data = pd.DataFrame(all_matches)
            overall_wins = all_matches_data['winner'].value_counts()
            st.write("### Overall Statistics Across All Championships:")
            for player, wins in overall_wins.items():
                st.write(f"{player} Wins: {wins}")
else:
    st.write("No championships available. Please create a new championship to get started.")

st.write("""
---
Developed by FlyBoat
""")