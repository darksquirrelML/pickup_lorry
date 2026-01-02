#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Pick-up Lorry Availability",
    page_icon="🚐",
    layout="wide"
)

st.title("🚐 Pick-up Lorry Availability & Whereabout")

# -------------------------
# Load data
# -------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/pickup_schedule.csv")

df = load_data()

# -------------------------
# Current time
# -------------------------
now = datetime.now().strftime("%H:%M")
st.caption(f"🕒 Current Time: **{now}**")

# -------------------------
# AVAILABLE NOW
# -------------------------
st.subheader("🟢 Available Now")

available_now = df[
    (df["status"] == "Available") &
    (df["time_start"] <= now) &
    (df["time_end"] >= now)
]

if available_now.empty:
    st.warning("No pick-up lorry available at this time.")
else:
    st.dataframe(
        available_now[
            ["vehicle_id", "plate_no", "driver", "current_location",
             "time_start", "time_end", "remarks"]
        ],
        use_container_width=True
    )

# -------------------------
# TODAY SCHEDULE
# -------------------------
st.subheader("📅 Today's Pick-up Lorry Schedule")

vehicle_filter = st.multiselect(
    "Filter by Vehicle",
    df["vehicle_id"].unique(),
    default=df["vehicle_id"].unique()
)

filtered_df = df[df["vehicle_id"].isin(vehicle_filter)]

st.dataframe(
    filtered_df.sort_values(["vehicle_id", "time_start"]),
    use_container_width=True
)

# -------------------------
# DRIVER WHEREABOUT UPDATE
# -------------------------
# st.subheader("📍 Driver Whereabout Update")

# with st.form("driver_update"):
#     col1, col2 = st.columns(2)

#     with col1:
#         vehicle = st.selectbox("Vehicle", df["vehicle_id"].unique())
#         location = st.text_input("Current Location")

#     with col2:
#         status = st.selectbox("Status", ["Available", "Busy"])
#         remarks = st.text_input("Remarks")

#     submit = st.form_submit_button("Update Whereabout")

# if submit:
#     st.success("✅ Update submitted (admin can save this to system).")




st.subheader("📍 Driver Whereabout Update (Auto-Save)")

with st.form("driver_update"):
    vehicle = st.selectbox("Vehicle", df["vehicle_id"].unique())

    location = st.text_input(
        "Current Location / Site Code",
        placeholder="e.g. P201, P202, Dormitory, On road"
    )
    
#     location = st.selectbox(
#         "Current Location",
#         ["Dormitory", "Depot", "On Road", "Site A", "Site B", "Site C"]
#     )

    status = st.selectbox("Status", ["Available", "Busy"])
    remarks = st.text_input("Remarks")

    submit = st.form_submit_button("Update Whereabout")

# if submit:
#     now = datetime.now().strftime("%H:%M")

#     mask = (
#         (df["vehicle_id"] == vehicle) &
#         (df["time_start"] <= now) &
#         (df["time_end"] >= now)
#     )

#     if df[mask].empty:
#         st.error("❌ No active time slot found for this vehicle.")
#     else:
#         df.loc[mask, "current_location"] = location
#         df.loc[mask, "status"] = status
#         df.loc[mask, "remarks"] = remarks

#         # 🔴 AUTO-SAVE TO CSV
#         df.to_csv("data/pickup_schedule.csv", index=False)

#         st.success("✅ Whereabout updated and saved.")
#         st.rerun()
if submit:
    from datetime import datetime

    # Convert times robustly
    df["time_start"] = pd.to_datetime(df["time_start"], errors="coerce").dt.time
    df["time_end"] = pd.to_datetime(df["time_end"], errors="coerce").dt.time

    now_time = datetime.now().time()

    mask = (
        (df["vehicle_id"] == vehicle) &
        (df["time_start"] <= now_time) &
        (df["time_end"] >= now_time)
    )

    if df[mask].empty:
        st.error("❌ No active time slot found for this vehicle.")
    else:
        df.loc[mask, "current_location"] = location
        df.loc[mask, "status"] = status
        df.loc[mask, "remarks"] = remarks
        df.loc[mask, "last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 🔹 Save CSV
        df.to_csv("data/pickup_schedule.csv", index=False)

        st.success("✅ Whereabout updated and saved.")



