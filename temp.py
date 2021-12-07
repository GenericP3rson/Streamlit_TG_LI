import pyTigerGraph as tg
import streamlit as st 
import pandas as pd 

host = "http://cc360.servehttp.com"
graphname = "Linkedin"
username = "tigergraph"
password = "ESSNL02mtRSFzs8q" 

conn = tg.TigerGraphConnection(host=host, graphname=graphname, username=username, password=password)

secret = conn.createSecret()
token = conn.getToken(secret, setToken=True)

@st.cache
def company_search(Company):
    cString = "\""+Company+"\""
    results = results = conn.runInstalledQuery("GetConnectionsOFCompany", params={"c":Company})
    df = pd.DataFrame(results[0]["@@myEdges"])
    return df

@st.cache
def name_search(Name):
    pString = "\""+Name+"\""
    results = results = conn.runInstalledQuery("GetConnectionsOfPerson", params={"lname":Name})
    df2 = pd.DataFrame(results[0]["@@myEdges"])
    return df2

st.title('Look at the Data in Streamlit!')
st.markdown('### Search by Company')

# Inputs
company_input = st.text_input("Company", "IBM")
companies = company_search(company_input)

# Tables and Charts
st.dataframe(companies)



st.markdown('### Search by Name')

# Inputs
name_input = st.text_input("Name", "Herke")
names = name_search(name_input)

# Tables and Charts
st.dataframe(names)

