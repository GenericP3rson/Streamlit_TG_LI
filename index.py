### IMPORT LIBRARIES

# Use Graphistry and pyTigerGraph
import graphistry
import pyTigerGraph as tg

# Pandas, flat_table, and NumPy to manipulate DFs
import pandas as pd
import flat_table
import numpy as np

# Streamlit apps
import streamlit as st
import streamlit.components.v1 as components

# cred.py Credentials
import cred

### SET UP STREAMLIT

# Set Layout as Wide
st.set_page_config(layout="wide")

# Create Sidebar
st.sidebar.title('Pick a Visualization')
sidebar = st.sidebar
graph_option = sidebar.radio(
    'Choose a Visualization', ("Graphistry", "Streamlit Songs", "Streamlit Artist Search"))

### CREDENTIALS

# Connect to your TigerGraph Host and Graphistry

conn = tg.TigerGraphConnection(host=cred.SUBDOMAIN, graphname=cred.GRAPHNAME,
                               username=cred.TIGERGRAPH_USERNAME, password=cred.TIGERGRAPH_PASSWORD)
conn.apiToken = conn.getToken(conn.createSecret())

graphistry.register(api=3, protocol="https", server="hub.graphistry.com", username=cred.GRAPHISTRY_USERNAME, password=cred.GRAPHISTRY_PASSWORD)

### DATA LOADING

@st.cache # Improves performance
def data_overview():
    result = conn.runInstalledQuery('edgeCrawl')
    data = pd.DataFrame(result[0]['@@edgeList'])
    g = graphistry.edges(data, 'from_id', 'to_id')
    graph = g.plot(render=False)
    return graph

@st.cache
def song_database():
    results = conn.runInstalledQuery("getSongs")
    df = pd.DataFrame(results[0]["Seed"])
    df = flat_table.normalize(df)
    return df

@st.cache
def artist_search(user_input):
    res2 = conn.runInstalledQuery("getSongsByArtist", {"artist": user_input})
    df2 = pd.DataFrame(res2[0]["Res"])
    data2 = flat_table.normalize(df2)
    return data2

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

### PAGES AND INFORMATION

if graph_option == 'Graphistry':
    # Title
    st.title('Look at the Data in Graphistry!')

    # Grab data and adds the iframe
    graph = data_overview()
    st.write("**Check out the songs, artists, and playlists connected!**")
    components.iframe(graph, width=1200, height=600)

elif graph_option == 'Streamlit Songs':
    # Title
    st.title('Look at the Data in Streamlit!')
    
    # Grab the data
    df = song_database()

    # Choose songs by the slider
    st.markdown('#### Select Songs with the Slider')
    min_id, max_id = st.slider("Select Song IDs", 0, 18398, [500, 1000])
    data = df[df["index"].between(left=min_id, right=max_id)]

    # Show the graphs in two columns
    st.markdown('#### Check out the attributes of the songs')
    left_column, right_column = st.columns(2) # Create Columns
    
    with left_column: # Add multiple elements to a column
        left_graph_type = st.selectbox(
    'Pick a Graph Type', ("Line Graph", "Bar Graph", "Area Chart"), 1)
        opts_one = st.multiselect("Pick Attributes", ['time_signature', 'duration_ms', 'tempo', 'valence', 'liveness', 'instrumentalness', 'acousticness', 'speechiness', 'mode', 'loudness', 'key_id', 'energy', 'energy_level', 'dancibility', 'popularity'], ['loudness'])
        if left_graph_type == "Line Graph":
            st.line_chart(pd.DataFrame(np.array([data[f'attributes.{attr}'] for attr in opts_one]).T, columns = opts_one))
        elif left_graph_type == "Bar Graph":
            st.bar_chart(pd.DataFrame(np.array([data[f'attributes.{attr}'] for attr in opts_one]).T, columns = opts_one))
        elif left_graph_type == "Area Chart":
            st.area_chart(pd.DataFrame(np.array([data[f'attributes.{attr}'] for attr in opts_one]).T, columns = opts_one))
    
    with right_column:
        right_graph_type = st.selectbox(
    'Pick a Graph Type', ("Line Graph", "Bar Graph", "Area Chart"), 2)
        opts_two = st.multiselect("Pick Attributes", ['time_signature', 'duration_ms', 'tempo', 'valence', 'liveness', 'instrumentalness', 'acousticness', 'speechiness', 'mode', 'loudness', 'key_id', 'energy', 'energy_level', 'dancibility', 'popularity'], ['dancibility'])
        if right_graph_type == "Line Graph":
            st.line_chart(pd.DataFrame(np.array([data[f'attributes.{attr}'] for attr in opts_two]).T, columns = opts_two))
        elif right_graph_type == "Bar Graph":
            st.bar_chart(pd.DataFrame(np.array([data[f'attributes.{attr}'] for attr in opts_two]).T, columns = opts_two))
        elif right_graph_type == "Area Chart":
            st.area_chart(pd.DataFrame(np.array([data[f'attributes.{attr}'] for attr in opts_two]).T, columns = opts_two))

    # Show the data
    bottom_left_column, bottom_right_column = st.columns(2)
    bottom_left_column.markdown('#### View your data in the chart') # Adding just one element to a column
    bottom_right_column.download_button(label="Download data as CSV", data=convert_df(data), file_name='songs.csv', mime='text/csv')
    st.write(data)

elif graph_option == 'Streamlit Artist Search':
    # Title
    st.title('Look at the Data in Streamlit!')
    st.markdown('### Search for Artists')

    # Inputs
    user_input = st.text_input("Artist", "BTS")
    artist_songs = artist_search(user_input)

    # Tables and Charts
    st.dataframe(artist_songs)
    st.bar_chart(artist_songs['attributes.popularity'])

else:
    # Error Message
    st.title("**404 Error**\nSomething went wrong.")
