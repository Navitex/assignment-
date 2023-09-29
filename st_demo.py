import streamlit as st
import googleapiclient.discovery
from pprint import pprint
import pymongo
from sqlalchemy import create_engine,text
import pandas as pd
# My-SQL- connections:
engine = create_engine('mysql+pymysql://root:admin@localhost:3306/youtube_data')
# Mongo DB connections:
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["youtube_data"]
collection = db["ydata"]
st.title("My Youtube Data Harvester")
user_input = st.text_area("Enter youtube channel Name:")
col1, col2,col3,col4 = st.columns(4)
def get_channel_details(channel_id):
            request = youtube.channels().list(part="snippet,contentDetails,statistics",id =channel_id)
            response = request.execute()
            d=dict(channel_name = response['items'][0]['snippet']['title'],
                channel_dis= response['items'][0]['snippet']['description'],
                channel_joined= response['items'][0]['snippet']['publishedAt'],
                channel_SC = response['items'][0]['statistics']['subscriberCount'],
                channel_VC = response['items'][0]['statistics'][ 'videoCount'],
                channel_ViewCount = response['items'][0]['statistics'][ 'viewCount'],
                upload_id= response['items'][0][ 'contentDetails']['relatedPlaylists']['uploads' ])
            return d
with col1:
    button_press=st.button('get Channel Details')
with col2:
    button_pressed=st.button('save to Mongo DB')
with col3:
    col3_button=st.button('Migrate to SQL')
with col4:
    col4_button = st.button('View data in SQL')
    
if button_press or button_pressed or col3_button or col4_button:    
    api_key='AIzaSyDs-kfOg2dw2h7yf0DDOH-PIK59fYpJpfM'
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    chn_name=user_input
    user_input=user_input.lower().replace(' ','')
    def get_channel_ids(chn_name):
        response = youtube.channels().list(part='id',forUsername=chn_name).execute()
        if 'items' in response:
            channel_id = response['items'][0]['id']
            return channel_id
        else:
            st.write(f'Channel ID for {chn_name} not found !!')
    if button_press or button_pressed:
        channel_id = get_channel_ids(user_input)
        cds=get_channel_details(channel_id)
        if button_press:
            st.write('Channel ID:')
            st.write(channel_id)
            st.write('channel details:')
            st.write(cds)        
    if button_pressed:
        progress_bar =st.progress(0)
        result=collection.insert_one(cds)
        st.write('Inserted ID:')
        result.inserted_id
        progress_bar.progress(100)
    if col3_button:
        st.write('Migration Started !!')
        progress_bar = st.progress(0)
        results = collection.find()
        data=pd.DataFrame(list(results))
        data.to_sql(name='youtube_data',con=engine,if_exists='replace',index=False)
        engine.dispose()
        progress_bar.progress(100)
    if col4_button:
        st.write('Fetching data from MySQL Database !!')
        engine = create_engine('mysql+pymysql://root:admin@localhost:3306/youtube_data')
        sql_query = text("select * from youtube_data")
        df=pd.read_sql_query(sql_query,engine.connect())
        df2=df.drop_duplicates(subset='channel_dis',keep='last')
        st.dataframe(df2)
        engine.dispose()