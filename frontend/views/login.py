#frontend>views>login.py
import streamlit as st
import requests
from utils.api_client import login

def show():
    st.markdown("## ERP Portal Login")
    st.caption("Demo admin: `admin` / `admin123` · Demo student: `student` / `student123`")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

    if submitted:
        if not username or not password:
            st.warning("Enter credentials")
            return

        try:
            res = login(username, password)
        except requests.RequestException:
            st.error("Cannot reach the API. If you are using Docker, the frontend must call http://api:8000, not localhost.")
            return
        except RuntimeError as exc:
            st.error(str(exc))
            return

        if res:
            st.session_state["token"] = res["access_token"]
            st.session_state["role"] = res["role"]
            st.session_state["username"] = username

            if res["role"] == "admin":
                st.session_state["current_page"] = "admin_dashboard"
            else:
                st.session_state["current_page"] = "student_marksheet"

            st.rerun()