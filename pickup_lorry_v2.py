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
# Load CSV (no cache to allow live updates)
# -------------------------
def load_data():
    return pd.read_csv("data/pickup_schedule.csv")

df = load_data()

# -------------------------
# Current time
# -------------------------
now_time = datetime.now().time()
st.caption(f"🕒 Current Time: **{datetime.now().strftime('%H:%M')}**")

# -------------------------
# DRIVER WHEREABOUT UPDATE (Auto-fill)
# -------------------------
st.subheader("📍 Driver Whereabout Update (Auto-Save)")

vehicle = st.selectbox("Vehicle", df["vehicle_id"].unique())

# Convert times for comparison
df["time_start_dt"] = pd.to_datetime(df["time_start"], errors="coerce").dt.time
df["time_end_dt"] = pd.to_datetime(df["time_end"], errors="coerce").dt.time

# Get active schedule for selected vehicle
active_row = df[
    (df["vehicle_id"] == vehicle) &
    (df["time_start_dt"] <= now_time) &
    (df["time_end_dt"] >= now_time)
]

# If no active slot, use first schedule of vehicle
if active_row.empty:
    active_row = df[df["vehicle_id"] == vehicle].iloc[[0]]

location_default = active_row["current_location"].values[0]
status_default = active_row["status"].values[0]
remarks_default = active_row["remarks"].values[0]

with st.form("driver_update"):
    location = st.text_input(
        "Current Location / Site Code",
        value=location_default,
        placeholder="e.g. P201, P202, Dormitory, On road"
    )

    status = st.selectbox(
        "Status",
        ["Available", "Busy"],
        index=0 if status_default == "Available" else 1
    )

    remarks = st.text_input("Remarks", value=remarks_default)

    submit = st.form_submit_button("Update Whereabout")

# -------------------------
# Update CSV after submit
# -------------------------
if submit:
    mask = (
        (df["vehicle_id"] == vehicle) &
        (df["time_start_dt"] <= now_time) &
        (df["time_end_dt"] >= now_time)
    )

    if df[mask].empty:
        st.error("❌ No active time slot found for this vehicle.")
        st.info("Check time slot or current time.")
    else:
        # Update in-memory dataframe
        df.loc[mask, "current_location"] = location
        df.loc[mask, "status"] = status
        df.loc[mask, "remarks"] = remarks
        df.loc[mask, "last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Save CSV
        df.to_csv("data/pickup_schedule.csv", index=False)

        st.success("✅ Whereabout updated and saved.")

# -------------------------
# AVAILABLE NOW
# -------------------------
available_now = df[
    (df["status"] == "Available") &
    (df["time_start_dt"] <= now_time) &
    (df["time_end_dt"] >= now_time)
]

st.subheader("🟢 Available Now")
if available_now.empty:
    st.warning("No pick-up lorry available at this time.")
else:
    st.dataframe(
        available_now[
            ["vehicle_id", "plate_no", "driver", "current_location",
             "status", "time_start", "time_end", "remarks", "last_updated"]
        ],
        use_container_width=True
    )

# -------------------------
# TODAY'S SCHEDULE with active slot
# -------------------------
st.subheader("📅 Today's Pick-up Lorry Schedule")

vehicle_filter = st.multiselect(
    "Filter by Vehicle",
    df["vehicle_id"].unique(),
    default=df["vehicle_id"].unique()
)

filtered_df = df[df["vehicle_id"].isin(vehicle_filter)].copy()

# Highlight active slot
filtered_df["active_now"] = filtered_df.apply(
    lambda row: "✅ Active" if row["time_start_dt"] <= now_time <= row["time_end_dt"] else "",
    axis=1
)

st.dataframe(
    filtered_df.sort_values(["vehicle_id", "time_start"])[
        ["vehicle_id", "plate_no", "driver", "current_location",
         "status", "time_start", "time_end", "remarks", "last_updated", "active_now"]
    ],
    use_container_width=True
)

