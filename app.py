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

# Sidebar Controls (These will NEVER flicker or reset now)
st.sidebar.header("Wave Parameters")
a_y = st.sidebar.slider("Ex Amplitude", 0.0, 1.2, 1.0, 0.05)
a_z = st.sidebar.slider("Ey Amplitude", 0.0, 1.2, 0.5, 0.05)
deg_offset = st.sidebar.slider("Phase Angle (deg)", -180.0, 180.0, 0.0, 1.0)

st.sidebar.markdown("---")
st.sidebar.header("Animation Controls")
auto_play = st.sidebar.checkbox("Auto-Play Animation", value=True)
speed = st.sidebar.slider("Animation Speed", 0.02, 0.3, 0.1, 0.02)

# Initialize session state for animation frame
if "animation_frame" not in st.session_state:
  st.session_state.animation_frame = 0.0


# Define an isolated fragment that updates automatically without reloading the page layout
@st.fragment(run_every=0.05 if auto_play else None)
def render_wave_plots():
  # Advance frame if auto-play is active
  if auto_play:
    st.session_state.animation_frame += speed
    if st.session_state.animation_frame > 2 * np.pi:
      st.session_state.animation_frame = 0.0

  # Constants & Computations
  x = np.linspace(0, 5 * np.pi, 600)
  x_paper = 2.7 * np.pi
  p_offset = np.radians(deg_offset)
  phase = x - st.session_state.animation_frame

  ey = a_y * np.cos(phase)
  ez = a_z * np.cos(phase + p_offset)

  cur_theta = x_paper - st.session_state.animation_frame
  cur_ey = a_y * np.cos(cur_theta)
  cur_ez = a_z * np.cos(cur_theta + p_offset)

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

  # Layout: 3 columns for 3 plots
  col1, col2, col3 = st.columns(3)

  def add_paper_plane(fig_ax):
    y_p = np.linspace(-1.3, 1.3, 10)
    z_p = np.linspace(-1.3, 1.3, 10)
    Y_p, Z_p = np.meshgrid(y_p, z_p)
    X_p = np.full_like(Y_p, x_paper)

    fig_ax.add_trace(
        go.Surface(
            x=X_p,
            y=Y_p,
            z=Z_p,
            colorscale=[[0, "wheat"], [1, "wheat"]],
            opacity=0.25,
            showscale=False,
        )
    )
    fig_ax.add_trace(
        go.Scatter3d(
            x=[0, 5 * np.pi],
            y=[0, 0],
            z=[0, 0],
            mode="lines",
            line=dict(color="black", width=4),
            showlegend=False,
        )
    )

  # --- PLOT 1 ---
  fig1 = go.Figure()
  add_paper_plane(fig1)
  fig1.add_trace(
      go.Scatter3d(
          x=x,
          y=ey,
          z=np.zeros_like(x),
          mode="lines",
          name="Ex component",
          line=dict(color="crimson", width=3),
      )
  )
  fig1.add_trace(
      go.Scatter3d(
          x=x,
          y=np.zeros_like(x),
          z=ez,
          mode="lines",
          name="Ey component",
          line=dict(color="royalblue", width=3),
      )
  )
  fig1.add_trace(
      go.Scatter3d(
          x=[x_paper, x_paper],
          y=[0, cur_ey],
          z=[0, cur_ez],
          mode="lines+markers",
          name="Net E vector",
          line=dict(color="darkgreen", width=5),
      )
  )
  fig1.update_layout(
      title="Component-wise Decomposition",
      scene=dict(
          xaxis_range=[0, 5 * np.pi],
          yaxis_range=[-1.2, 1.2],
          zaxis_range=[-1.2, 1.2],
          xaxis_title="z",
          yaxis_title="Ex",
          zaxis_title="Ey",
      ),
      margin=dict(l=0, r=0, b=0, t=30),
      height=450,
  )
  col1.plotly_chart(fig1, use_container_width=True, key="p1")

  # --- PLOT 2 ---
  fig2 = go.Figure()
  add_paper_plane(fig2)
  fig2.add_trace(
      go.Scatter3d(
          x=x,
          y=a_y * np.cos(x - st.session_state.animation_frame),
          z=a_z * np.cos(x - st.session_state.animation_frame + p_offset),
          mode="lines",
          name="Net E wave",
          line=dict(color="royalblue", width=4),
      )
  )
  fig2.update_layout(
      title="Full 3D Traveling Wave",
      scene=dict(
          xaxis_range=[0, 5 * np.pi],
          yaxis_range=[-1.2, 1.2],
          zaxis_range=[-1.2, 1.2],
          xaxis_title="z",
          yaxis_title="Ex",
          zaxis_title="Ey",
      ),
      margin=dict(l=0, r=0, b=0, t=30),
      height=450,
  )
  col2.plotly_chart(fig2, use_container_width=True, key="p2")

  # --- PLOT 3 ---
  fig3 = go.Figure()
  add_paper_plane(fig3)
  theta = np.linspace(0, 2 * np.pi, 400)
  fig3.add_trace(
      go.Scatter3d(
          x=np.full_like(theta, x_paper),
          y=a_y * np.cos(theta),
          z=a_z * np.cos(theta + p_offset),
          mode="lines",
          name="E vector trace",
          line=dict(color="royalblue", width=4),
      )
  )
  fig3.add_trace(
      go.Scatter3d(
          x=[x_paper],
          y=[cur_ey],
          z=[cur_ez],
          mode="markers",
          name="Instantaneous E",
          marker=dict(color="crimson", size=6),
      )
  )
  fig3.update_layout(
      title="Transverse Plane Polarization",
      scene=dict(
          xaxis_range=[0, 5 * np.pi],
          yaxis_range=[-1.2, 1.2],
          zaxis_range=[-1.2, 1.2],
          xaxis_title="z",
          yaxis_title="Ex",
          zaxis_title="Ey",
      ),
      margin=dict(l=0, r=0, b=0, t=30),
      height=450,
  )
  col3.plotly_chart(fig3, use_container_width=True, key="p3")


# Render the isolated auto-updating fragment
render_wave_plots()
