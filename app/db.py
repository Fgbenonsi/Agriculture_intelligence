import os
from sqlalchemy import create_engine
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def get_engine_cloud():
    url = os.getenv("DATABASE_URL", "postgresql+psycopg://fabriceg@localhost:5433/agri_intel")
    return create_engine(url)