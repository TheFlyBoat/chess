import streamlit as st
import pandas as pd
import gspread
import toml
import json
from google.oauth2.service_account import Credentials
import datetime

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Load credentials from config.toml
config = toml.load("config.toml")

# Ensure GOOGLE_SHEETS_KEY exists in the config
if "GOOGLE_SHEETS_KEY" not in config:
    raise ValueError("Missing GOOGLE_SHEETS_KEY section in config.toml")

# Convert TOML section to dictionary
creds_dict = config["GOOGLE_SHEETS_KEY"]

# Ensure private key is present
if "private_key" not in creds_dict or not creds_dict["private_key"]:
    raise ValueError("Missing private_key in GOOGLE_SHEETS_KEY section of config.toml")

# Validate correct private key format
private_key = creds_dict["private_key"]
if not private_key.startswith("-----BEGIN PRIVATE KEY-----") or not private_key.endswith("-----END PRIVATE KEY-----"):
    raise ValueError("Invalid private key format. Ensure config.toml contains the correct key structure.")

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