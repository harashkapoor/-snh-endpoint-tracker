"""
South Niagara Hospital — Endpoint Deployment Readiness Tracker
Built by Harsh Kapoor | Niagara Health Technical Analyst Candidate
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
def now_est():
    return datetime.now(pytz.timezone("America/Toronto"))
import random
import io

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SNH Endpoint Tracker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 20px;
        border-left: 4px solid #00b4d8;
        margin: 5px 0;
    }
    .status-ready { color: #00b894; font-weight: bold; }
    .status-progress { color: #fdcb6e; font-weight: bold; }
    .status-failed { color: #e17055; font-weight: bold; }
    .status-pending { color: #636e72; font-weight: bold; }
    h1 { color: #00b4d8 !important; }
    .stProgress .st-bo { background-color: #00b894; }
</style>
""", unsafe_allow_html=True)

# ─── Data Generation ───────────────────────────────────────────────────────────
DEPARTMENTS = {
    "ICU": 1200,
    "Emergency": 1000,
    "Pharmacy": 400,
    "Radiology": 800,
    "Operating Rooms": 600,
    "Nursing Stations": 4000,
    "Administration": 2000,
    "Labs": 1200,
    "Outpatient": 1800,
    "Facilities": 800,
    "Biomedical": 600,
    "IT Infrastructure": 400,
    "Rehabilitation": 600,
    "Mental Health": 600,
}

DEVICE_TYPES = [
    "Clinical Workstation",
    "Laptop",
    "Mobile Device",
    "Tablet",
    "Printer",
    "Scanner",
    "Clinical Peripheral",
    "Reception Terminal"
]

STAGES = ["Received", "Staged", "Imaged", "Enrolled", "Tested", "Ready"]
STAGE_COLORS = {
    "Received": "#636e72",
    "Staged": "#fdcb6e",
    "Imaged": "#0984e3",
    "Enrolled": "#6c5ce7",
    "Tested": "#fd79a8",
    "Ready": "#00b894",
    "Failed": "#e17055"
}

@st.cache_data(show_spinner=False)
def generate_devices():
    devices = []
    device_id = 1
    random.seed(42)

    for dept, count in DEPARTMENTS.items():
        for i in range(count):
            stage_weights = [5, 10, 15, 20, 20, 25, 5]
            stage = random.choices(
                STAGES + ["Failed"],
                weights=stage_weights
            )[0]

            days_ago = random.randint(1, 90)
            last_updated = datetime.now() - timedelta(days=days_ago)

            devices.append({
                "Device ID": f"SNH-{dept[:3].upper()}-{device_id:04d}",
                "Department": dept,
                "Device Type": random.choice(DEVICE_TYPES),
                "Stage": stage,
                "Assigned User": f"user{device_id}@niagarahealth.on.ca" if stage in ["Enrolled", "Tested", "Ready"] else "",
                "Last Updated": last_updated.strftime("%Y-%m-%d"),
                "Notes": "" if stage != "Failed" else random.choice([
                    "Enrollment failed — Intune policy conflict",
                    "Driver issue — pending update",
                    "Hardware fault — replacement ordered",
                    "Compliance check failed — BitLocker required"
                ])
            })
            device_id += 1

    return pd.DataFrame(devices)

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "devices.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            department TEXT,
            device_type TEXT,
            stage TEXT,
            assigned_user TEXT DEFAULT '',
            last_updated TEXT,
            notes TEXT DEFAULT ''
        )
    """)
    conn.commit()
    # Seed with generated data if empty
    count = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    if count == 0:
        seed_df = generate_devices()
        seed_df.columns = [c.lower().replace(" ", "_") for c in seed_df.columns]
        seed_df.to_sql("devices", conn, if_exists="append", index=False)
        conn.commit()
    conn.close()

def load_devices() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM devices", conn)
    conn.close()
    df.columns = ["Device ID", "Department", "Device Type", "Stage",
                  "Assigned User", "Last Updated", "Notes"]
    return df

def save_device(row: dict):
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO devices
        (device_id, department, device_type, stage, assigned_user, last_updated, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (row["Device ID"], row["Department"], row["Device Type"],
          row["Stage"], row.get("Assigned User", ""),
          row["Last Updated"], row.get("Notes", "")))
    conn.commit()
    conn.close()

def update_device_stage(device_id_pattern: str, new_stage: str):
    conn = get_conn()
    conn.execute("""
        UPDATE devices SET stage=?, last_updated=?
        WHERE LOWER(device_id) LIKE LOWER(?)
    """, (new_stage, now_est().strftime("%B %d, %Y"), f"%{device_id_pattern}%"))
    conn.commit()
    conn.close()

def delete_device(device_id_pattern: str):
    conn = get_conn()
    conn.execute("DELETE FROM devices WHERE LOWER(device_id) LIKE LOWER(?)",
                 (f"%{device_id_pattern}%",))
    conn.commit()
    conn.close()

def import_devices(import_df: pd.DataFrame):
    conn = get_conn()
    for _, row in import_df.iterrows():
        conn.execute("""
            INSERT OR REPLACE INTO devices
            (device_id, department, device_type, stage, assigned_user, last_updated, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (row.get("Device ID",""), row.get("Department",""),
              row.get("Device Type",""), row.get("Stage","Received"),
              row.get("Assigned User",""), row.get("Last Updated", now_est().strftime("%B %d, %Y")),
              row.get("Notes","")))
    conn.commit()
    conn.close()

# ─── Load Data ─────────────────────────────────────────────────────────────────
init_db()
df = load_devices()

# ─── Header ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🏥 South Niagara Hospital")
    st.markdown("### Endpoint Deployment Readiness Tracker")
    st.markdown(f"*Last updated: {now_est().strftime('%B %d, %Y at %I:%M %p')} EST*")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    go_live = datetime(2027, 3, 1)
    days_left = (go_live - datetime.now()).days
    st.metric("Days to Network Go-Live", f"{days_left}", "March 2027")
    opening = datetime(2028, 6, 1)
    days_to_open = (opening - datetime.now()).days
    st.metric("Days to Hospital Opening", f"{days_to_open}", "Summer 2028")

st.divider()

# ─── Top Metrics ───────────────────────────────────────────────────────────────
total = len(df)
ready = len(df[df["Stage"] == "Ready"])
in_progress = len(df[df["Stage"].isin(["Staged", "Imaged", "Enrolled", "Tested"])])
failed = len(df[df["Stage"] == "Failed"])
pending = len(df[df["Stage"] == "Received"])
pct_ready = round(ready / total * 100, 1)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Total Devices", f"{total:,}", f"of 16,000 target")
c2.metric("✅ Ready", f"{ready:,}", f"{pct_ready}%")
c3.metric("🔄 In Progress", f"{in_progress:,}", f"{round(in_progress/total*100,1)}%")
c4.metric("⚠️ Failed", f"{failed:,}", f"{round(failed/total*100,1)}%", delta_color="inverse")
c5.metric("📬 Pending", f"{pending:,}", f"{round(pending/total*100,1)}%")

st.divider()

# ─── Overall Progress Bar ──────────────────────────────────────────────────────
st.markdown("### 📊 Overall Deployment Progress")
st.progress(pct_ready / 100)
st.markdown(f"**{pct_ready}% Ready** — {ready:,} of {total:,} devices confirmed ready for patient care")

st.divider()

# ─── Charts Row ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏢 Readiness by Department")
    dept_stats = df.groupby(["Department", "Stage"]).size().reset_index(name="Count")
    dept_ready = df[df["Stage"] == "Ready"].groupby("Department").size().reset_index(name="Ready")
    dept_total = df.groupby("Department").size().reset_index(name="Total")
    dept_merged = dept_total.merge(dept_ready, on="Department", how="left").fillna(0)
    dept_merged["% Ready"] = (dept_merged["Ready"] / dept_merged["Total"] * 100).round(1)
    dept_merged = dept_merged.sort_values("% Ready", ascending=True)

    fig = px.bar(
        dept_merged,
        x="% Ready",
        y="Department",
        orientation="h",
        color="% Ready",
        color_continuous_scale=["#e17055", "#fdcb6e", "#00b894"],
        range_color=[0, 100],
        text="% Ready",
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        font_color="white",
        showlegend=False,
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=0, r=50, t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 🔄 Stage Distribution")
    stage_counts = df["Stage"].value_counts().reset_index()
    stage_counts.columns = ["Stage", "Count"]
    stage_counts["Color"] = stage_counts["Stage"].map(STAGE_COLORS)

    fig2 = px.pie(
        stage_counts,
        values="Count",
        names="Stage",
        color="Stage",
        color_discrete_map=STAGE_COLORS,
        hole=0.4
    )
    fig2.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        font_color="white",
        height=400,
        legend=dict(orientation="v", x=1, y=0.5)
    )
    fig2.update_traces(textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ─── Device Type Breakdown ─────────────────────────────────────────────────────
st.markdown("### 💻 Readiness by Device Type")
type_stats = df.groupby(["Device Type", "Stage"]).size().reset_index(name="Count")
type_ready = df[df["Stage"] == "Ready"].groupby("Device Type").size().reset_index(name="Ready")
type_total = df.groupby("Device Type").size().reset_index(name="Total")
type_merged = type_total.merge(type_ready, on="Device Type", how="left").fillna(0)
type_merged["% Ready"] = (type_merged["Ready"] / type_merged["Total"] * 100).round(1)

cols = st.columns(4)
for i, row in type_merged.iterrows():
    col = cols[i % 4]
    pct = row["% Ready"]
    color = "#00b894" if pct >= 70 else "#fdcb6e" if pct >= 40 else "#e17055"
    col.markdown(f"""
    <div style="background:#1e2130; border-radius:8px; padding:12px; margin:4px 0; border-left:3px solid {color}">
        <div style="font-size:12px; color:#b2bec3">{row['Device Type']}</div>
        <div style="font-size:20px; font-weight:bold; color:{color}">{pct:.0f}%</div>
        <div style="font-size:11px; color:#636e72">{int(row['Ready'])}/{int(row['Total'])} ready</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ─── Failed Devices ────────────────────────────────────────────────────────────
st.markdown("### ⚠️ Failed Devices — Requires Attention")
failed_df = df[df["Stage"] == "Failed"][["Device ID", "Department", "Device Type", "Notes", "Last Updated"]]
if len(failed_df) > 0:
    st.dataframe(
        failed_df.head(20),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Device ID": st.column_config.TextColumn("Device ID", width="small"),
            "Notes": st.column_config.TextColumn("Issue", width="large"),
        }
    )
else:
    st.success("No failed devices! ✅")

st.divider()

# ─── Sidebar Filters + Device Search ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    dept_filter = st.multiselect("Department", options=sorted(df["Department"].unique()), default=[])
    stage_filter = st.multiselect("Stage", options=STAGES + ["Failed"], default=[])
    type_filter = st.multiselect("Device Type", options=sorted(df["Device Type"].unique()), default=[])

    st.divider()
    st.markdown("## 📤 Export")
    if st.button("Export Full Report (CSV)"):
        export_df = load_devices()
        csv = export_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            csv,
            "SNH_Endpoint_Readiness_Report.csv",
            "text/csv"
        )

    st.divider()
    st.markdown("## ➕ Add Device")
    new_id = st.text_input("Device ID", placeholder="SNH-ICU-0001", key="new_device_id")
    new_dept = st.selectbox("Department", options=sorted(DEPARTMENTS.keys()), key="new_dept")
    new_type = st.selectbox("Device Type", options=DEVICE_TYPES, key="new_type")
    new_stage = st.selectbox("Stage", options=STAGES + ["Failed"], key="new_stage")
    new_notes = st.text_input("Notes (optional)", placeholder="e.g. Enrollment failed — policy conflict", key="new_notes")
    if st.button("➕ Add Device", type="primary"):
        if not new_id.strip():
            st.error("Device ID is required")
        else:
            save_device({
                "Device ID": new_id.strip(),
                "Department": new_dept,
                "Device Type": new_type,
                "Stage": new_stage,
                "Assigned User": "",
                "Last Updated": now_est().strftime("%B %d, %Y"),
                "Notes": new_notes
            })
            st.success(f"✅ Added: {new_id.strip()}")
            st.rerun()

    st.divider()
    st.markdown("## 🔍 Search & Manage Device")
    search_id = st.text_input("Search by Device ID", placeholder="SNH-ICU-0001")
    if search_id:
        result = df[df["Device ID"].str.contains(search_id, case=False, na=False)]
        if len(result) > 0:
            st.dataframe(result, use_container_width=True, hide_index=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Update Stage:**")
                new_stage_update = st.selectbox("New Stage", options=STAGES + ["Failed"], key="update_stage")
                if st.button("✅ Update Stage"):
                    update_device_stage(search_id, new_stage_update)
                    st.success(f"✅ Updated to {new_stage_update}")
                    st.rerun()
            with col_b:
                st.markdown("**Remove Device:**")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Delete Device", type="secondary"):
                    delete_device(search_id)
                    st.success(f"✅ Deleted {search_id}")
                    st.rerun()
        else:
            st.warning("Device not found")

    st.divider()
    st.markdown("## 📥 Import Devices (CSV)")
    st.caption("Upload a CSV with columns: Device ID, Department, Device Type, Stage, Notes")
    uploaded = st.file_uploader("Choose CSV file", type="csv", label_visibility="collapsed")
    if uploaded:
        try:
            import_df = pd.read_csv(uploaded)
            required = {"Device ID", "Department", "Device Type", "Stage"}
            if required.issubset(set(import_df.columns)):
                if "Notes" not in import_df.columns:
                    import_df["Notes"] = ""
                if "Assigned User" not in import_df.columns:
                    import_df["Assigned User"] = ""
                if "Last Updated" not in import_df.columns:
                    import_df["Last Updated"] = now_est().strftime("%B %d, %Y")
                import_devices(import_df)
                st.success(f"✅ Imported {len(import_df)} devices — scroll up to see updated dashboard")
                st.cache_data.clear()
            else:
                missing = required - set(import_df.columns)
                st.error(f"Missing columns: {missing}")
        except Exception as e:
            st.error(f"Import failed: {e}")

    st.divider()
    st.markdown("## 📅 Key Milestones")
    st.markdown("""
    - 🔵 **Now** — Staging & Imaging
    - 🟡 **Q3 2026** — Enrollment wave 1
    - 🟠 **Q1 2027** — Network go-live
    - 🟢 **Q2 2027** — Clinical validation
    - ✅ **Summer 2028** — Hospital opening
    """)

    st.divider()
    st.markdown("## ℹ️ About")
    st.markdown("""
    Built by **Harsh Kapoor**
    Technical Analyst Candidate
    Niagara Health — ICAT Team

    *Modelled around the South Niagara
    Hospital endpoint deployment scope*
    """)

# ─── Filtered Device Table ─────────────────────────────────────────────────────
filtered = df.copy()
if dept_filter:
    filtered = filtered[filtered["Department"].isin(dept_filter)]
if stage_filter:
    filtered = filtered[filtered["Stage"].isin(stage_filter)]
if type_filter:
    filtered = filtered[filtered["Device Type"].isin(type_filter)]

if dept_filter or stage_filter or type_filter:
    st.markdown(f"### 📋 Filtered Results ({len(filtered):,} devices)")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ─── Tabs — Deployment Waves + Runbook ────────────────────────────────────────
st.divider()
tab1, tab2, tab3 = st.tabs(["🌊 Deployment Waves", "📋 Runbook", "ℹ️ About"])

with tab1:
    st.markdown("## 🌊 Deployment Wave Plan — 16,000 Devices")
    waves = {
        "Wave": ["1 — Pilot", "2 — Non-Clinical", "3 — Network Go-Live", "4 — Clinical", "5 — Final + ICU"],
        "Period": ["Q3 2026", "Q4 2026", "Q1 2027", "Q2–Q3 2027", "Q4 2027–Q2 2028"],
        "Devices": [200, 2500, 4000, 6500, 2800],
        "Departments": ["Administration", "Admin, Facilities, Labs", "Outpatient, Radiology", "Nursing, ER, OR, Pharmacy", "ICU + remaining clinical"],
        "Status": ["🔄 In Progress", "⏳ Planned", "⏳ Planned", "⏳ Planned", "⏳ Planned"],
    }
    wave_df = pd.DataFrame(waves)
    st.dataframe(wave_df, use_container_width=True, hide_index=True)

    st.markdown("### Wave Principles")
    st.markdown("""
    - ✅ **Pilot first** — validate every process on 200 devices before scaling
    - 🏥 **Clinical areas last** — protect patient care, non-clinical areas deploy first
    - 📋 **Document every wave** — what broke, what changed, lessons learned
    - 🔒 **PHIPA compliance** — every device checked before clinical go-live
    - 🔄 **5% spare buffer** — ~800 spare devices staged for go-live day
    """)

    fig_wave = px.bar(
        wave_df, x="Wave", y="Devices",
        color="Devices",
        color_continuous_scale=["#0984e3", "#6c5ce7", "#00b894"],
        text="Devices",
        title="Devices Per Wave"
    )
    fig_wave.update_layout(
        plot_bgcolor="#1e2130", paper_bgcolor="#1e2130",
        font_color="white", coloraxis_showscale=False,
        height=300, margin=dict(t=40, b=0)
    )
    fig_wave.update_traces(textposition="outside")
    st.plotly_chart(fig_wave, use_container_width=True)

with tab2:
    st.markdown("## 📋 Deployment Runbook")
    st.markdown("### Device Stage Pipeline")
    st.markdown("""
    ```
    📦 RECEIVED → 🔧 STAGED → 💿 IMAGED → ☁️ ENROLLED → ✅ TESTED → 🟢 READY
    ```
    """)
    stages_doc = {
        "Stage": ["Received", "Staged", "Imaged", "Enrolled", "Tested", "Ready", "Failed"],
        "Action": [
            "Log device, apply asset tag, record serial number",
            "Verify hardware, place in imaging queue",
            "PXE boot, deploy OS via SCCM task sequence, install drivers",
            "Autopilot or manual Intune enrollment, verify compliance",
            "Functional test, clinical workflow validation with staff",
            "Deliver to assigned location, notify department",
            "Log issue, assign remediation, re-enter pipeline after fix"
        ],
        "Owner": ["Logistics", "Tech Analyst", "Tech Analyst", "Tech Analyst", "Tech Analyst + Clinical", "ICAT Team", "Tech Analyst"],
    }
    st.dataframe(pd.DataFrame(stages_doc), use_container_width=True, hide_index=True)

    st.markdown("### Pre-Deployment Checklist")
    st.markdown("""
    - ☐ Intune tenant configured — auto-enrollment enabled
    - ☐ Entra ID device groups created by department
    - ☐ Compliance policies tested on pilot device
    - ☐ Configuration profiles created (Wi-Fi, VPN, certs)
    - ☐ App packages prepared and tested
    - ☐ Autopilot profiles assigned to device groups
    - ☐ SCCM task sequence validated
    - ☐ Hardware hash CSV ready for Autopilot upload
    - ☐ PHIPA checklist signed off
    - ☐ Change request ticket opened
    """)

    st.markdown("### Failure Handling")
    st.markdown("""
    If a device fails at any stage:
    1. Update tracker → **FAILED**
    2. Document issue in Notes (error message, steps tried)
    3. Categorize: Hardware / Enrollment / Compliance / Driver / App
    4. Assign to team member for resolution
    5. Re-enter pipeline at correct stage after fix
    6. Document resolution for future reference
    """)

with tab3:
    st.markdown("## ℹ️ About This Project")
    st.markdown("""
    **South Niagara Hospital Endpoint Deployment Tracker**

    Built by **Harsh Kapoor** — Technical Analyst Candidate, Niagara Health ICAT Team.

    This tool was designed to support the South Niagara Hospital redevelopment project,
    modelled around the 16,000+ device deployment scope leading to hospital opening in Summer 2028.

    **Key Milestones:**
    - 🔵 Now → Q3 2026: Pilot wave + staging
    - 🟡 Q4 2026: Non-clinical rollout
    - 🟠 Early 2027: Network go-live
    - 🟢 Q2 2027: Clinical validation
    - ✅ Summer 2028: Hospital opening day

    **Tech Stack:** Python · Streamlit · Pandas · Plotly

    **GitHub:** [harashkapoor/-snh-endpoint-tracker](https://github.com/harashkapoor/-snh-endpoint-tracker)
    """)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#636e72; font-size:12px">
    South Niagara Hospital Endpoint Deployment Tracker •
    Built for Niagara Health ICAT Team •
    Network Go-Live: Early 2027 • Hospital Opening: Summer 2028
</div>
""", unsafe_allow_html=True)
