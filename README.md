# 🏥 South Niagara Hospital — Endpoint Deployment Readiness Tracker

> A real-time endpoint deployment tracking dashboard built specifically for the **South Niagara Hospital ICAT team**, modelled around the **16,000+ device deployment scope** for the 2028 hospital opening.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://snH-endpoint-tracker.streamlit.app)

---

## 🌐 Live Demo

**[Live Demo](https://snH-endpoint-tracker.streamlit.app)**

> ⚠️ *Note: Live demo uses sample/mock data for demonstration purposes. Production deployment uses live ICAT inventory data.*

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Department-Level Readiness Tracking** | Monitor deployment progress across all hospital departments in real time |
| 🔄 **Device Stage Pipeline** | Full lifecycle tracking: `Received → Staged → Imaged → Enrolled → Tested → Ready` |
| 🚨 **Failed Device Alerts** | Instant visibility into failed/blocked devices with associated issue notes |
| 📥 **CSV Export** | Export filtered data as CSV for runbook documentation and audit trails |
| ⏱️ **Countdown Timers** | Live countdowns to **Network Go-Live (Early 2027)** and **Hospital Opening (Summer 2028)** |
| 🔍 **Smart Filters** | Filter device inventory by department, deployment stage, and device type |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11+ |
| **Dashboard Framework** | [Streamlit](https://streamlit.io) |
| **Data Processing** | [Pandas](https://pandas.pydata.org) |
| **Visualizations** | [Plotly](https://plotly.com/python/) |

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.11 or higher
- pip or pipenv

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/harashkapoor/snH-endpoint-tracker.git
cd snH-endpoint-tracker

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# OR
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run app.py
```

The dashboard will open automatically at **http://localhost:8501**

### One-liner (if venv already active)
```bash
streamlit run app.py
```

---

## 🏗️ Deployment Context

### South Niagara Hospital — ICAT Project Scope

The **South Niagara Hospital** (SNH), part of **Niagara Health**, is one of Canada's most significant healthcare infrastructure projects. Scheduled to open **Summer 2028**, the new facility will serve the greater Niagara region and replace aging infrastructure at existing Niagara Health sites.

**Key Project Parameters:**

| Parameter | Detail |
|---|---|
| **Hospital Opening** | Summer 2028 |
| **Network Go-Live Target** | Early 2027 |
| **Total Device Scope** | 16,000+ endpoints |
| **Organization** | Niagara Health — ICAT (Information, Communications & Analytics Technology) |

**Device Categories Tracked:**
- 🖥️ Workstations & Thin Clients
- 💻 Laptops & Mobile Workstations
- 🖨️ Network Printers & MFDs
- 📱 Mobile Devices (tablets, ruggedized handhelds)
- 📺 Digital Signage & Patient Displays
- 🔒 Specialty Clinical Devices (nurse call, telemetry endpoints)

**Deployment Pipeline Stages:**

```
Received → Staged → Imaged → Enrolled → Tested → ✅ Ready
                                              ↓
                                         ❌ Failed (with issue notes)
```

This tracker gives the ICAT team a **single pane of glass** to manage deployment velocity, surface blockers early, and ensure all 16,000+ devices are production-ready before the hospital opens its doors.

---

## 📁 Project Structure

```
endpoint-tracker/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .gitignore              # Git ignore rules
└── .venv/                  # Virtual environment (excluded from git)
```

---

## 📦 Requirements

```
streamlit
pandas
plotly
openpyxl
```

See [`requirements.txt`](./requirements.txt) for pinned versions.

---

## 🤝 Contributing

This tool is built for internal ICAT use. For feature requests or bug reports, please contact the project maintainer.

---

## 👤 About

**Built by Harsh Kapoor**
*Technical Analyst Candidate, Niagara Health*

> Developed as part of the South Niagara Hospital endpoint readiness initiative to support the ICAT team in tracking, managing, and reporting on the 16,000+ device deployment scope ahead of the 2028 hospital opening.

---

## 📄 License

Internal use — Niagara Health ICAT Team. All rights reserved.

---

*Last updated: August 2026 · South Niagara Hospital opens Summer 2028 🏥*
