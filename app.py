import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Interactive Wave Propagation", page_icon="〰️", layout="wide"
)

st.title("Interactive Wave Propagation - Source / Tx POV")
st.markdown(
    "Explore electromagnetic wave polarization, components, and 3D propagation dynamically."
)

# Sidebar Controls for Static Wave Parameters
st.sidebar.header("Wave Parameters")
a_y = st.sidebar.slider("Ex Amplitude", 0.0, 1.2, 1.0, 0.05)
a_z = st.sidebar.slider("Ey Amplitude", 0.0, 1.2, 0.5, 0.05)
deg_offset = st.sidebar.slider("Phase Angle (deg)", -180.0, 180.0, 0.0, 1.0)

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

# Constants
x = np.linspace(0, 5 * np.pi, 600)
x_paper = 2.7 * np.pi
p_offset = np.radians(deg_offset)
theta_circle = np.linspace(0, 2 * np.pi, 400)

# Build Frames for Native Client-Side Animation
frames_list = []
animation_steps = 40
phases = np.linspace(0, 2 * np.pi, animation_steps, endpoint=False)

for i, phi in enumerate(phases):
  ey = a_y * np.cos(x - phi)
  ez = a_z * np.cos(x - phi + p_offset)

  cur_theta = x_paper - phi
  cur_ey = a_y * np.cos(cur_theta)
  cur_ez = a_z * np.cos(cur_theta + p_offset)

  net_wave_x = x
  net_wave_y = a_y * np.cos(x - phi)
  net_wave_z = a_z * np.cos(x - phi + p_offset)

  # Each frame contains updates for all 3 subplots (traces 0 to 8)
  frame_data = [
      # Subplot 1 Traces
      go.Scatter3d(
          x=x, y=ey, z=np.zeros_like(x)
      ),  # Ex component (trace 1 in fig)
      go.Scatter3d(
          x=x, y=np.zeros_like(x), z=ez
      ),  # Ey component (trace 2 in fig)
      go.Scatter3d(
          x=[x_paper, x_paper], y=[0, cur_ey], z=[0, cur_ez]
      ),  # Net vector (trace 3)
      # Subplot 2 Traces
      go.Scatter3d(
          x=net_wave_x, y=net_wave_y, z=net_wave_z
      ),  # Traveling wave (trace 5)
      # Subplot 3 Traces
      go.Scatter3d(
          x=np.full_like(theta_circle, x_paper),
          y=a_y * np.cos(theta_circle),
          z=a_z * np.cos(theta_circle + p_offset),
      ),  # Trace circle (trace 7)
      go.Scatter3d(
          x=[x_paper], y=[cur_ey], z=[cur_ez]
      ),  # Instantaneous marker (trace 8)
  ]
  frames_list.append(go.Frame(data=frame_data, name=str(i)))

# --- CREATE SINGLE FIGURE WITH SUBPLOTS AND ANIMATION ---
from plotly.subplots import make_subplots

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


# Helper function to add paper plane background
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


# Populate initial traces (Frame 0 state)
initial_phi = 0.0
init_ey = a_y * np.cos(x - initial_phi)
init_ez = a_z * np.cos(x - initial_phi + p_offset)
init_cur_theta = x_paper - initial_phi
init_cur_ey = a_y * np.cos(init_cur_theta)
init_cur_ez = a_z * np.cos(init_cur_theta + p_offset)

# Plot 1 Traces
add_paper_plane(fig, 1)
fig.add_trace(
    go.Scatter3d(
        x=x,
        y=init_ey,
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
        z=init_ez,
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
        y=[0, init_cur_ey],
        z=[0, init_cur_ez],
        mode="lines+markers",
        name="Net E vector",
        line=dict(color="darkgreen", width=5),
    ),
    row=1,
    col=1,
)

# Plot 2 Traces
add_paper_plane(fig, 2)
fig.add_trace(
    go.Scatter3d(
        x=x,
        y=a_y * np.cos(x - initial_phi),
        z=a_z * np.cos(x - initial_phi + p_offset),
        mode="lines",
        name="Net E wave",
        line=dict(color="royalblue", width=4),
    ),
    row=1,
    col=2,
)

# Plot 3 Traces
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
        y=[init_cur_ey],
        z=[init_cur_ez],
        mode="markers",
        name="Instantaneous E",
        marker=dict(color="crimson", size=6),
    ),
    row=1,
    col=3,
)

# Assign frames to figure
fig.frames = frames_list

# Configure layout with native Play/Pause buttons
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
    updatemenus=[
        {
            "type": "buttons",
            "showactive": False,
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [
                        None,
                        {
                            "frame": {"duration": 50, "redraw": False},
                            "fromcurrent": True,
                            "transition": {"duration": 0},
                        },
                    ],
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                },
            ],
            "x": 0.1,
            "y": 1.15,
            "xanchor": "right",
            "yanchor": "top",
        }
    ],
)

# Render seamlessly without full page flickers
st.plotly_chart(fig, use_container_width=True)
