import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime
import random

st.set_page_config(page_title="PriceWatcher", layout="wide")

FILE = "menu_prices.csv"

# ---------- LOAD DATA ----------
def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    else:
        df = pd.DataFrame(columns=[
            "State","Dish",
            "Your_Price",
            "Swiggy_Price",
            "Zomato_Price",
            "Date"
        ])
        df.to_csv(FILE, index=False)
        return df

# ---------- LIVE PRICE UPDATE (SIMULATED API) ----------
def live_price_update(df):
    df["Swiggy_Price"] = df["Swiggy_Price"].apply(lambda x: x + random.randint(-5,5))
    df["Zomato_Price"] = df["Zomato_Price"].apply(lambda x: x + random.randint(-5,5))
    return df

# ---------- AUTO DATA ----------
def fetch_demo_data():
    states = ["Karnataka", "Tamil Nadu", "Telangana"]
    dishes = ["Dosa", "Idli", "Vada", "Biryani", "Pizza", "Burger"]

    rows = []
    for state in states:
        for dish in dishes:
            swiggy = random.randint(100,220)
            zomato = swiggy + random.randint(-10,10)
            your = swiggy - random.randint(10,20)

            rows.append({
                "State": state,
                "Dish": dish,
                "Your_Price": your,
                "Swiggy_Price": swiggy,
                "Zomato_Price": zomato,
                "Date": datetime.now().strftime("%Y-%m-%d")
            })
    return pd.DataFrame(rows)

# ---------- LOGIN / REGISTRATION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    # Default user
    st.session_state.users = {"admin": "1234"}

if not st.session_state.logged_in:
    st.markdown("<h1 style='color:#ff4b4b'>🍽️ PriceWatcher Login</h1>", unsafe_allow_html=True)
    u = st.text_input("Username (sample input: admin)")
    p = st.text_input("Password (sample input: 1234)", type="password")

    if st.button("Login"):
        if u in st.session_state.users and st.session_state.users[u] == p:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong login")

    st.markdown("### Or Register New Account")
    new_u = st.text_input("New Username")
    new_p = st.text_input("New Password", type="password")
    if st.button("Register"):
        if new_u and new_p:
            if new_u in st.session_state.users:
                st.warning("Username already exists")
            else:
                st.session_state.users[new_u] = new_p
                st.success("Registration successful! Please login.")
        else:
            st.error("Enter both username and password")
    st.stop()

# ---------- COLORFUL THEME ----------
st.markdown("""
<style>
body {
background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
color:white;
}
.block-container {
background: transparent;
}
.card {
background: rgba(255,255,255,0.08);
padding:15px;
border-radius:15px;
box-shadow:0 0 15px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# ---------- LOAD DATA ----------
df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.header("⚙ Controls")

if st.sidebar.button("🍔 Load Demo Swiggy Data"):
    df = fetch_demo_data()
    df.to_csv(FILE, index=False)
    st.sidebar.success("Loaded demo data")
    st.rerun()

if st.sidebar.button("🔄 Live Update Prices"):
    df = live_price_update(df)
    df.to_csv(FILE, index=False)
    st.sidebar.success("Prices refreshed")
    st.rerun()

st.sidebar.header("➕ Add Dish")

state = st.sidebar.text_input("State")
dish = st.sidebar.text_input("Dish")
your_price = st.sidebar.number_input("Your Price", 0.0)
swiggy_price = st.sidebar.number_input("Swiggy Price", 0.0)
zomato_price = st.sidebar.number_input("Zomato Price", 0.0)

if st.sidebar.button("Add Dish"):
    if state and dish:
        new = {
            "State": state,
            "Dish": dish,
            "Your_Price": your_price,
            "Swiggy_Price": swiggy_price,
            "Zomato_Price": zomato_price,
            "Date": datetime.now().strftime("%Y-%m-%d")
        }
        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.sidebar.success("Dish added successfully!")
        st.success(f"✅ New dish '{dish}' added for {state}")
        st.rerun()
    else:
        st.sidebar.error("Please enter both State and Dish")

# ---------- MAIN ----------
st.markdown("<h1 style='color:#4dd0e1'>📊 Restaurant Price Intelligence</h1>", unsafe_allow_html=True)

if len(df) == 0:
    st.warning("Click 'Load Demo Swiggy Data'")
    st.stop()

states = df["State"].unique().tolist()
selected_state = st.selectbox("Select State", states)
state_df = df[df["State"] == selected_state]

st.metric("Total Dishes", len(state_df))

st.dataframe(state_df, use_container_width=True)

# ---------- GRAPH 1 ----------
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=state_df["Dish"], y=state_df["Your_Price"],
                          mode="lines+markers", name="Your Price"))
fig1.add_trace(go.Scatter(x=state_df["Dish"], y=state_df["Swiggy_Price"],
                          mode="lines+markers", name="Swiggy"))
fig1.add_trace(go.Scatter(x=state_df["Dish"], y=state_df["Zomato_Price"],
                          mode="lines+markers", name="Zomato"))
fig1.update_layout(template="plotly_dark", title="Live Market Comparison")
st.plotly_chart(fig1, use_container_width=True)

# ---------- PROFIT STRATEGY ----------
state_df["Market_Avg"] = state_df[["Swiggy_Price","Zomato_Price"]].mean(axis=1)
state_df["Suggested_Price"] = state_df["Market_Avg"] * 0.95

fig2 = go.Figure()
fig2.add_trace(go.Bar(x=state_df["Dish"], y=state_df["Your_Price"], name="Your Price"))
fig2.add_trace(go.Bar(x=state_df["Dish"], y=state_df["Market_Avg"], name="Market Avg"))
fig2.add_trace(go.Bar(x=state_df["Dish"], y=state_df["Suggested_Price"], name="Suggested Price"))
fig2.update_layout(template="plotly_dark", title="💡 Profitable Price Strategy")
st.plotly_chart(fig2, use_container_width=True)

# ---------- LOGOUT ----------
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()