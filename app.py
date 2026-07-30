import os
import glob
import tempfile
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dtscalibration

# -----------------------------------------------------------------------------
# 1. Page Configuration & Theme State
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="DTS Temperature Viewer",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# -----------------------------------------------------------------------------
# 2. CSS Design System
# -----------------------------------------------------------------------------
if IS_DARK:
    bg = "#09090b"
    bg_subtle = "#0c0c0f"
    card = "#0c0c0f"
    card_hover = "#131316"
    border = "#1e1e24"
    border_subtle = "#16161a"
    text = "#fafafa"
    text_muted = "#a1a1aa"
    text_dim = "#52525b"
    accent = "#2563eb"
    green = "#22c55e"
    green_muted = "rgba(34,197,94,0.12)"
    red = "#ef4444"
    red_muted = "rgba(239,68,68,0.12)"
    amber = "#f59e0b"
    amber_muted = "rgba(245,158,11,0.12)"
    shadow = "none"
else:
    bg = "#ffffff"
    bg_subtle = "#f9fafb"
    card = "#ffffff"
    card_hover = "#f4f4f5"
    border = "#e4e4e7"
    border_subtle = "#f0f0f2"
    text = "#09090b"
    text_muted = "#71717a"
    text_dim = "#a1a1aa"
    accent = "#2563eb"
    green = "#16a34a"
    green_muted = "rgba(22,163,74,0.08)"
    red = "#dc2626"
    red_muted = "rgba(220,38,38,0.08)"
    amber = "#d97706"
    amber_muted = "rgba(217,119,6,0.08)"
    shadow = "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"

css_code = f"""
<style>
:root {{
    --bg: {bg};
    --bg-subtle: {bg_subtle};
    --card: {card};
    --card-hover: {card_hover};
    --border: {border};
    --border-subtle: {border_subtle};
    --text: {text};
    --text-muted: {text_muted};
    --text-dim: {text_dim};
    --accent: {accent};
    --green: {green};
    --green-muted: {green_muted};
    --red: {red};
    --red-muted: {red_muted};
    --amber: {amber};
    --amber-muted: {amber_muted};
    --shadow: {shadow};
    --radius: 10px;
}}

/* Hide standard Streamlit chrome */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}}
.block-container {{
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1400px !important;
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background-color: var(--bg-subtle) !important;
    border-right: 1px solid var(--border) !important;
    max-width: 340px !important;
}}
[data-testid="stSidebar"] .block-container {{
    padding: 1.5rem 1rem !important;
}}

/* Brand header */
.brand {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}}
.brand-icon {{
    font-size: 1.5rem;
    color: var(--accent);
    line-height: 1;
}}
.brand-name {{
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text);
}}

/* Card wrapper for plots */
.chart-wrap {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.5rem;
}}
.chart-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.2rem;
}}
.chart-subtitle {{
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-bottom: 1.2rem;
}}

/* Key Performance Indicators */
.metric-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    box-shadow: var(--shadow);
}}
.metric-label {{
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.metric-value {{
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text);
    margin-top: 0.2rem;
    letter-spacing: -0.02em;
}}

/* Styled Status Badges */
.badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 500;
}}
.badge-blue {{
    color: var(--accent);
    background: rgba(37, 99, 235, 0.12);
}}
.badge-green {{
    color: var(--green);
    background: var(--green-muted);
}}
.badge-amber {{
    color: var(--amber);
    background: var(--amber-muted);
}}

/* Modern Table Layout */
.data-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.8rem;
    margin-top: 1rem;
}}
.data-table th {{
    text-align: left;
    padding: 0.6rem 0.8rem;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border);
}}
.data-table td {{
    padding: 0.65rem 0.8rem;
    color: var(--text);
    border-bottom: 1px solid var(--border-subtle);
}}
.data-table tr:last-child td {{
    border-bottom: none;
}}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Plotly Layout Config
# -----------------------------------------------------------------------------
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#a1a1aa" if IS_DARK else "#71717a", size=11),
    margin=dict(l=55, r=25, t=15, b=45),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        zerolinecolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        tickfont=dict(size=10, color="#a1a1aa" if IS_DARK else "#71717a"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        zerolinecolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        tickfont=dict(size=10, color="#a1a1aa" if IS_DARK else "#71717a"),
    ),
)

# -----------------------------------------------------------------------------
# 4. Helper Functions
# -----------------------------------------------------------------------------
def metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def detect_manufacturer(xml_files):
    """Inspects the first XML file to guess manufacturer"""
    if not xml_files:
        return "silixa"
    try:
        with open(xml_files[0], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1500)
            if "witsml" in content.lower() or "silixa" in content.lower():
                return "silixa"
            elif "apsensing" in content.lower() or "ap sensing" in content.lower():
                return "apsensing"
    except Exception:
        pass
    return "silixa"  # Default fallback

@st.cache_data(show_spinner="Loading and parsing DTS files...")
def load_data(directory_path, manufacturer):
    """Loads DTS data from the specified directory based on manufacturer"""
    if manufacturer == "silixa":
        return dtscalibration.read_silixa_files(directory=directory_path)
    elif manufacturer == "apsensing":
        return dtscalibration.read_apsensing_files(directory=directory_path)
    else:
        raise ValueError(f"Unknown manufacturer: {manufacturer}")

# -----------------------------------------------------------------------------
# 5. Header Section
# -----------------------------------------------------------------------------
head_left, head_right = st.columns([8, 2])
with head_left:
    st.markdown("""
    <div class="brand">
        <span class="brand-icon">◆</span>
        <span class="brand-name">DTS Data Visualizer</span>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light Theme" if IS_DARK else "🌙 Dark Theme"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. Sidebar (Configuration & Controls with Folder Dialog Upload)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# 6. Sidebar (Configuration & Controls with Multi-file / Folder Handling)
# -----------------------------------------------------------------------------
st.sidebar.markdown('<div class="brand"><span class="brand-name">Settings</span></div>', unsafe_allow_html=True)

st.sidebar.subheader("📂 Data Files Upload")
st.sidebar.markdown(
    "<p style='font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;'>"
    "Select your DTS folder or choose all the XML files inside your channel folder.</p>",
    unsafe_allow_html=True
)

# Folder/Files uploader widget
uploaded_folder_files = st.file_uploader(
    "Select DTS Files or Folder",
    type=["xml", "tra", "ddf", "dat"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if not uploaded_folder_files:
    st.info("👈 Please upload your DTS channel XML measurement files using the uploader above.")
    st.stop()

# Reconstruct folder structure inside a temporary directory safely
temp_dir = tempfile.mkdtemp()
for file_obj in uploaded_folder_files:
    # Some browsers provide full relative paths in file_obj.name, others just filenames.
    file_path_attr = getattr(file_obj, "name", "file.xml")
    target_path = os.path.join(temp_dir, file_path_attr)
    
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "wb") as f:
        f.write(file_obj.getbuffer())

# Scan for XML files in the temporary directory (searching recursively)
xml_files = glob.glob(os.path.join(temp_dir, "**", "*.xml"), recursive=True)
if not xml_files:
    xml_files = glob.glob(os.path.join(temp_dir, "*.xml"))

num_files = len(xml_files)

if num_files == 0:
    st.warning("No XML measurement files found. Make sure you selected the contents of a valid DTS channel directory.")
    st.stop()

# Auto-detect manufacturer
detected_mfg = detect_manufacturer(xml_files)

mfg_choice = st.sidebar.selectbox(
    "Device Manufacturer",
    options=["Auto-Detect", "Silixa (Ultima / XT-DTS)", "AP Sensing"],
    index=0
)

if mfg_choice == "Auto-Detect":
    manufacturer = detected_mfg
    mfg_source = "Auto-detected"
elif mfg_choice == "Silixa (Ultima / XT-DTS)":
    manufacturer = "silixa"
    mfg_source = "User selected"
else:
    manufacturer = "apsensing"
    mfg_source = "User selected"

# Load the dataset from the temp directory path
try:
    ds = load_data(temp_dir, manufacturer)
except Exception as e:
    st.error(f"Failed to load dataset: {str(e)}")
    st.stop()

# Verify dataset structure
if "tmp" not in ds.variables:
    st.error("The loaded dataset does not contain temperature ('tmp') variable.")
    st.stop()

# Ensure x coordinate is sorted
if ds.x[0] > ds.x[-1]:
    ds = ds.sortby('x')

# Extract basic dataset metrics
dist_min = float(ds.x.min().values)
dist_max = float(ds.x.max().values)
num_times = len(ds.time.values)

# Get temperature limits for default values
valid_tmp = ds.tmp.values[~np.isnan(ds.tmp.values)]
if len(valid_tmp) > 0:
    temp_min_obs = float(valid_tmp.min())
    temp_max_obs = float(valid_tmp.max())
else:
    temp_min_obs, temp_max_obs = 0.0, 100.0

# Sidebar Range Sliders
st.sidebar.subheader("🎛️ Filter Parameters")

distance_range = st.sidebar.slider(
    "Distance range (m)",
    min_value=dist_min,
    max_value=dist_max,
    value=(dist_min, dist_max),
    step=0.1
)

temp_range = st.sidebar.slider(
    "Temperature Range Limit (°C)",
    min_value=float(np.floor(temp_min_obs - 5)),
    max_value=float(np.ceil(temp_max_obs + 5)),
    value=(float(np.floor(temp_min_obs)), float(np.ceil(temp_max_obs))),
    step=1.0
)

colormap_options = ["Viridis", "Plasma", "Inferno", "Cividis", "Thermal", "RdBu_r", "Turbo", "Jet"]
selected_colormap = st.sidebar.selectbox(
    "2D Heatmap Colormap",
    options=colormap_options,
    index=0
)

# Apply distance range slice to the dataset
ds_filtered = ds.sel(x=slice(distance_range[0], distance_range[1]))

filtered_tmp = ds_filtered.tmp.values[~np.isnan(ds_filtered.tmp.values)]
if len(filtered_tmp) > 0:
    cur_min_temp = float(filtered_tmp.min())
    cur_max_temp = float(filtered_tmp.max())
else:
    cur_min_temp, cur_max_temp = 0.0, 0.0

# -----------------------------------------------------------------------------
# 7. Main Dashboard Area
# -----------------------------------------------------------------------------
mfg_badge_color = "badge-blue" if manufacturer == "silixa" else "badge-amber"
st.markdown(f"""
<div style="margin-bottom: 1.5rem; display: flex; gap: 0.75rem; align-items: center;">
    <span class="badge {mfg_badge_color}">{manufacturer.upper()} ({mfg_source})</span>
    <span class="badge badge-green">{num_files} XML files loaded successfully</span>
</div>
""", unsafe_allow_html=True)

# KPI Metrics row
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Timesteps", f"{num_times}")
with c2:
    metric_card("Active Fiber Length", f"{distance_range[1] - distance_range[0]:.2f} m")
with c3:
    metric_card("Min Temperature", f"{cur_min_temp:.2f} °C")
with c4:
    metric_card("Max Temperature", f"{cur_max_temp:.2f} °C")

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. 2D Plot (Distance vs Time & Temperature Heatmap)
# -----------------------------------------------------------------------------
x_coords_2d = ds_filtered.x.values
time_coords_2d = ds_filtered.time.values
z_values_2d = ds_filtered.tmp.values

fig_2d = go.Figure(data=go.Heatmap(
    x=time_coords_2d,
    y=x_coords_2d,
    z=z_values_2d,
    colorscale=selected_colormap,
    zmin=temp_range[0],
    zmax=temp_range[1],
    colorbar=dict(
        title=dict(text="Temp (°C)", font=dict(size=10)),
        thickness=15,
        len=0.8,
        tickfont=dict(size=9)
    ),
    hoverongaps=False,
    hovertemplate="Time: %{x}<br>Distance: %{y:.2f} m<br>Temp: %{z:.2f} °C<extra></extra>"
))

fig_2d.update_layout(
    xaxis_title="Time",
    yaxis_title="Distance along fiber (m)",
    **PLOT_LAYOUT
)

st.markdown("""
<div class="chart-wrap">
    <div class="chart-title">2D Temperature Profile (Time Series)</div>
    <div class="chart-subtitle">Heatmap showing fiber temperature distribution over time. Select coordinates or zoom to inspect specific zones.</div>
""", unsafe_allow_html=True)

st.plotly_chart(fig_2d, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. Time Series Selector Slider
# -----------------------------------------------------------------------------
st.markdown("<h3 style='font-size: 1.1rem; font-weight: 600; margin-top: 1rem;'>🕒 Slice Time Series</h3>", unsafe_allow_html=True)

if num_times > 1:
    time_options = [pd.to_datetime(t) for t in ds_filtered.time.values]
    time_labels = [t.strftime("%Y-%m-%d %H:%M:%S") for t in time_options]
    
    selected_time_idx = st.slider(
        "Use this slider to select a specific time measurement to display in the 1D profile below.",
        min_value=0,
        max_value=num_times - 1,
        value=0,
        label_visibility="collapsed"
    )
    selected_time = time_options[selected_time_idx]
    
    st.markdown(f"""
    <div style='margin-bottom: 1.5rem; font-size: 0.85rem; color: var(--accent); font-weight: 600;'>
        Selected Timestamp: {time_labels[selected_time_idx]} (Step {selected_time_idx + 1} of {num_times})
    </div>
    """, unsafe_allow_html=True)
else:
    selected_time_idx = 0
    selected_time = pd.to_datetime(ds_filtered.time.values[0])
    st.markdown(f"""
    <div style='margin-bottom: 1.5rem; font-size: 0.85rem; color: var(--text-muted); font-weight: 600;'>
        Single Timestamp loaded: {selected_time.strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 10. 1D Plot (Temperature vs Distance)
# -----------------------------------------------------------------------------
ds_1d = ds_filtered.isel(time=selected_time_idx)
x_coords_1d = ds_1d.x.values
temp_coords_1d = ds_1d.tmp.values

fig_1d = go.Figure()
fig_1d.add_trace(go.Scatter(
    x=x_coords_1d,
    y=temp_coords_1d,
    mode="lines",
    line=dict(color=accent, width=2),
    name="Temperature",
    hovertemplate="Distance: %{x:.2f} m<br>Temp: %{y:.2f} °C<extra></extra>"
))

layout_1d = PLOT_LAYOUT.copy()
layout_1d["yaxis"] = dict(range=[temp_range[0], temp_range[1]], **PLOT_LAYOUT["yaxis"])

fig_1d.update_layout(
    xaxis_title="Distance along fiber (m)",
    yaxis_title="Temperature (°C)",
    **layout_1d
)

selected_time_str = pd.to_datetime(ds_filtered.time.values[selected_time_idx]).strftime('%Y-%m-%d %H:%M:%S')

st.markdown(f"""
<div class="chart-wrap">
    <div class="chart-title">1D Temperature Profile (Single Time Slice)</div>
    <div class="chart-subtitle">Linear temperature profile along the fiber length at <b>{selected_time_str}</b>.</div>
""", unsafe_allow_html=True)

st.plotly_chart(fig_1d, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 11. Extra Detail: Raw Metadata Explorer (Expander)
# -----------------------------------------------------------------------------
with st.expander("📄 Dataset Attributes & Metadata Explorer"):
    st.markdown("### File-level Metadata Attributes")
    
    rows = []
    attrs_keys = sorted(list(ds.attrs.keys()))[:15]
    for key in attrs_keys:
        val = str(ds.attrs[key])
        if len(val) > 80:
            val = val[:80] + "..."
        rows.append(f"<tr><td><b>{key}</b></td><td>{val}</td></tr>")
        
    attrs_table = f"""
    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 30%;">Metadata Property</th>
                <th style="width: 70%;">Value</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
    """
    st.markdown(attrs_table, unsafe_allow_html=True)
    
    if len(ds.attrs) > 15:
        st.caption(f"Showing 15 of {len(ds.attrs)} attributes. Open the raw XML files to see full vendor configuration parameters.")