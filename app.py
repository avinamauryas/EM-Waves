import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Interactive Wave Propagation", page_icon="〰️", layout="wide"
)

st.title("Interactive Wave Propagation - Source / Tx POV")
st.markdown(
    "Explore electromagnetic wave polarization, components, and 3D propagation dynamically."
)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Wave Parameters")
a_y = st.sidebar.slider("Ex Amplitude", 0.0, 1.2, 1.0, 0.05)
a_z = st.sidebar.slider("Ey Amplitude", 0.0, 1.2, 0.5, 0.05)
deg_offset = st.sidebar.slider("Phase Angle (deg)", -180.0, 180.0, 0.0, 1.0)

st.sidebar.markdown("---")
st.sidebar.header("Wave Motion Control")
# Drag this slider to scrub smoothly through the wave propagation
phase_shift = st.sidebar.slider(
    "Phase / Time Scrubber", 0.0, 2 * np.pi, 0.0, 0.05
)

# Determine Polarization State
if a_y < 0.05 and a_z > 0.05:
  pol_state = "Linear (Vertical)"
elif a_z < 0.05 and a_y > 0.05:
  pol_state = "Linear (Horizontal)"
elif abs(a_y - a_z) < 0.05 and abs(deg_offset) < 5.0:
  pol_state = "Linear (Diagonal)"
elif abs(a_y - a_z) < 0.05 and abs(abs(deg_offset) - 90.0) < 5.0:
  pol_state = "LHCP" if deg_offset < 0 else "RHCP"
else:
  pol_state = "LHEP" if deg_offset < 0 else "RHEP"

st.markdown(
    f"### Polarization State: **{pol_state}** | Ex: `{a_y:.2f}` | Ey:"
    f" `{a_z:.2f}`"
)

# Constants & Calculations
x = np.linspace(0, 5 * np.pi, 600)
x_paper = 2.7 * np.pi
p_offset = np.radians(deg_offset)

phase = x - phase_shift
ey = a_y * np.cos(phase)
ez = a_z * np.cos(phase + p_offset)

cur_theta = x_paper - phase_shift
cur_ey = a_y * np.cos(cur_theta)
cur_ez = a_z * np.cos(cur_theta + p_offset)

theta_circle = np.linspace(0, 2 * np.pi, 400)

# Build Subplots Figure
fig = make_subplots(
    rows=1,
    cols=3,
    specs=[
        [{"type": "scene"}, {"type": "scene"}, {"type": "scene"}],
    ],
    subplot_titles=(
        "Component Decomposition (Ex & Ey)",
        "Full 3D Traveling Wave Propagation",
        "Transverse Plane: Polarization State",
    ),
)


def add_paper_plane(fig_obj, col_idx):
  y_p = np.linspace(-1.3, 1.3, 10)
  z_p = np.linspace(-1.3, 1.3, 10)
  Y_p, Z_p = np.meshgrid(y_p, z_p)
  X_p = np.full_like(Y_p, x_paper)

  fig_obj.add_trace(
      go.Surface(
          x=X_p,
          y=Y_p,
          z=Z_p,
          colorscale=[[0, "wheat"], [1, "wheat"]],
          opacity=0.25,
          showscale=False,
      ),
      row=1,
      col=col_idx,
  )
  fig_obj.add_trace(
      go.Scatter3d(
          x=[0, 5 * np.pi],
          y=[0, 0],
          z=[0, 0],
          mode="lines",
          line=dict(color="black", width=4),
          showlegend=False,
      ),
      row=1,
      col=col_idx,
  )


# --- PLOT 1: Component Decomposition ---
add_paper_plane(fig, 1)
fig.add_trace(
    go.Scatter3d(
        x=x,
        y=ey,
        z=np.zeros_like(x),
        mode="lines",
        name="Ex component",
        line=dict(color="crimson", width=3),
    ),
    row=1,
    col=1,
)
fig.add_trace(
    go.Scatter3d(
        x=x,
        y=np.zeros_like(x),
        z=ez,
        mode="lines",
        name="Ey component",
        line=dict(color="royalblue", width=3),
    ),
    row=1,
    col=1,
)
fig.add_trace(
    go.Scatter3d(
        x=[x_paper, x_paper],
        y=[0, cur_ey],
        z=[0, cur_ez],
        mode="lines+markers",
        name="Net E vector",
        line=dict(color="darkgreen", width=5),
    ),
    row=1,
    col=1,
)

# --- PLOT 2: Full Traveling Wave ---
add_paper_plane(fig, 2)
fig.add_trace(
    go.Scatter3d(
        x=x,
        y=a_y * np.cos(x - phase_shift),
        z=a_z * np.cos(x - phase_shift + p_offset),
        mode="lines",
        name="Net E wave",
        line=dict(color="royalblue", width=4),
    ),
    row=1,
    col=2,
)

# --- PLOT 3: Polarization Ellipse Trace ---
add_paper_plane(fig, 3)
fig.add_trace(
    go.Scatter3d(
        x=np.full_like(theta_circle, x_paper),
        y=a_y * np.cos(theta_circle),
        z=a_z * np.cos(theta_circle + p_offset),
        mode="lines",
        name="E vector trace",
        line=dict(color="royalblue", width=4),
    ),
    row=1,
    col=3,
)
fig.add_trace(
    go.Scatter3d(
        x=[x_paper],
        y=[cur_ey],
        z=[cur_ez],
        mode="markers",
        name="Instantaneous E",
        marker=dict(color="crimson", size=6),
    ),
    row=1,
    col=3,
)

# Layout Configuration
fig.update_layout(
    height=550,
    margin=dict(l=0, r=0, b=0, t=30),
    scene=dict(
        xaxis_range=[0, 5 * np.pi],
        yaxis_range=[-1.2, 1.2],
        zaxis_range=[-1.2, 1.2],
        xaxis_title="z",
        yaxis_title="Ex",
        zaxis_title="Ey",
    ),
    scene2=dict(
        xaxis_range=[0, 5 * np.pi],
        yaxis_range=[-1.2, 1.2],
        zaxis_range=[-1.2, 1.2],
        xaxis_title="z",
        yaxis_title="Ex",
        zaxis_title="Ey",
    ),
    scene3=dict(
        xaxis_range=[0, 5 * np.pi],
        yaxis_range=[-1.2, 1.2],
        zaxis_range=[-1.2, 1.2],
        xaxis_title="z",
        yaxis_title="Ex",
        zaxis_title="Ey",
    ),
)

# Render cleanly without any lagging loops
st.plotly_chart(fig, use_container_width=True)
