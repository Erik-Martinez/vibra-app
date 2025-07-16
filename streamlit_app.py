import streamlit as st
import pandas as pd
import jsapy  as jsa
import os
os.system("pip install git+https://github.com/Erik-Martinez/jsapy.git")

st.set_page_config(page_title="Vibration Exposure Calculator", layout="wide")
st.title("Vibration Exposure Calculator")

vibration_type = st.radio("Select vibration type", ["Hand-arm", "Whole-body"], horizontal=True)

st.markdown("""
Enter the vibration data for each machine.  
For **hand-arm**, you can use either total vibration `aw` or components `ax`, `ay`, `az`.  
For **whole-body**, only components are valid (`ax`, `ay`, `az`).
""")

if "vibration_df" not in st.session_state:
    if vibration_type == "Hand-arm":
        st.session_state.vibration_df = pd.DataFrame({
            "Source Name": ["Drill", "Grinder"],
            "aw": [2.0, None],
            "ax": [None, 2.1],
            "ay": [None, 1.8],
            "az": [None, 1.2],
            "Exposure Time (hours)": [2.5, 3]
        })
    else:
        st.session_state.vibration_df = pd.DataFrame({
            "Source Name": ["Forklift", "Compactor"],
            "ax": [0.5, 1.1],
            "ay": [0.6, 1.2],
            "az": [0.4, 1.0],
            "Exposure Time (hours)": [3, 2]
        })

df = st.data_editor(
    st.session_state.vibration_df,
    num_rows="dynamic",
    use_container_width=True,
    key="vibration_input"
)

if st.button("Calculate A(8)"):
    try:
        machines = []
        for i, row in df.iterrows():
            machine = {
                "name": row.get("Source Name", f"Machine {i+1}"),
                "time": float(row["Exposure Time (hours)"])
            }

            if vibration_type == "Hand-arm":
                aw = row.get("aw")
                ax = row.get("ax")
                ay = row.get("ay")
                az = row.get("az")
                if pd.notna(aw):
                    machine["aw"] = float(aw)
                elif pd.notna(ax) and pd.notna(ay) and pd.notna(az):
                    machine["ax"] = float(ax)
                    machine["ay"] = float(ay)
                    machine["az"] = float(az)
                else:
                    raise ValueError(f"Row {i+1} - Missing valid vibration data.")
            else:
                
                ax = row.get("ax")
                ay = row.get("ay")
                az = row.get("az")
                if pd.notna(ax) and pd.notna(ay) and pd.notna(az):
                    machine["ax"] = float(ax)
                    machine["ay"] = float(ay)
                    machine["az"] = float(az)
                else:
                    raise ValueError(f"Row {i+1} - All components (ax, ay, az) are required for whole-body.")

            machines.append(machine)

        if vibration_type == "Hand-arm":
            result = jsa.vibrations_hand_arm(machines)
        else:
            result = jsa.vibrations_body(machines)

        a8 = result.exposure_value
        unit = result.unit

        if result.exceeds_limit == True:
            color, status = "🔴", "Danger - Above Limit Value"
        elif result.exceeds_action == True:
            color, status = "🟡", "Caution - Above Action Value"
        else:
            color, status = "🟢", "Safe - Below Action Value"
            
        st.markdown(f"""
            <div style="text-align:center; font-size: 24px;">
                <p>{color} <strong>{status}</strong></p>
                <p><strong>A(8):</strong> {a8:.2f} {unit}</p>
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error in calculation: {e}")
