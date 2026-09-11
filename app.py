import streamlit as st

# Set web page configuration
st.set_page_config(page_title="IS 10262:2019 Calculator", layout="centered")

st.title("🏗️ IS 10262:2019 Concrete Mix Design Calculator")
st.write("An interactive web tool for calculating concrete mix proportions per cubic meter.")

# Create two columns for clean input organization
col1, col2 = st.columns(2)

with col1:
    fck = st.number_input("Concrete Grade ($f_{ck}$ in N/mm²)", min_value=10, max_value=100, value=30, step=5)
    nominal_size = st.selectbox("Max Aggregate Size (mm)", options=[10, 20, 40], index=1)
    zone = st.selectbox("Fine Agg. Grading Zone", options=["Zone I", "Zone II", "Zone III", "Zone IV"], index=1)
    slump = st.number_input("Required Slump Workability (mm)", min_value=25, max_value=200, value=100, step=25)

with col2:
    wc_ratio = st.number_input("Water-Cement (W/C) Ratio", min_value=0.25, max_value=0.70, value=0.45, step=0.01)
    sp_gr_cement = st.number_input("Specific Gravity (Cement)", min_value=2.50, max_value=3.50, value=3.15, step=0.01)
    sp_gr_fa = st.number_input("Specific Gravity (Fine Agg.)", min_value=2.00, max_value=3.00, value=2.65, step=0.01)
    sp_gr_ca = st.number_input("Specific Gravity (Coarse Agg.)", min_value=2.00, max_value=3.00, value=2.74, step=0.01)

# Calculation logic triggers instantly when inputs change
try:
    # 1. Precise Target Strength (IS 10262:2019 Table 2)
    if fck <= 15:
        S = 3.5
    elif fck <= 25:
        S = 4.0
    elif 30 <= fck <= 60:
        S = 5.0
    else:
        S = 6.0
    target_strength = fck + (1.65 * S)
    
    # 2. Base Water Content (IS 10262:2019 Table 4 for 50mm slump)
    water_table = {10: 208, 20: 186, 40: 165}
    base_water = water_table.get(nominal_size, 186)
    
    # Adjust water for slump (3% increase for every 25mm above 50mm)
    if slump > 50:
        extra_slump = slump - 50
        water_multiplier = 1 + (0.03 * (extra_slump / 25))
        calculated_water = base_water * water_multiplier
    else:
        calculated_water = base_water
    
    # 3. Cement Content calculation
    cement_content = calculated_water / wc_ratio
    
    # 4. Aggregates Volume Calculations (Table 6 adjustments)
    ca_base_table = {10: 0.48, 20: 0.62, 40: 0.71}
    vol_ca_base = ca_base_table.get(nominal_size, 0.62)
    
    # Adjust coarse aggregate volume based on Sand Grading Zone
    zone_adjustments = {"Zone I": -0.02, "Zone II": 0.0, "Zone III": 0.02, "Zone IV": 0.04}
    zone_adj = zone_adjustments.get(zone, 0.0)
    
    # Adjust for change in W/C ratio
    wc_deviation = (0.50 - wc_ratio) / 0.05
    wc_adj = wc_deviation * 0.01
    
    vol_ca = vol_ca_base + zone_adj + wc_adj
    vol_fa = 1.0 - vol_ca
    
    # Net aggregate volume framework (Assuming 1% standard entrapped air volume)
    vol_net = 1.0 - 0.01
    vol_cement = cement_content / (sp_gr_cement * 1000)
    vol_water = calculated_water / (1.0 * 1000)
    vol_aggregates = vol_net - (vol_cement + vol_water)
    
    if vol_aggregates <= 0:
        st.error("⚠️ Invalid proportions resulting in negative spatial volume values.")
    else:
        # Final mass distribution weights (kg/m³)
        mass_ca = vol_aggregates * vol_ca * sp_gr_ca * 1000
        mass_fa = vol_aggregates * vol_fa * sp_gr_fa * 1000
        
        # Display Results in a stylized card layout
        st.write("---")
        st.subheader("📊 Design Output (per Cubic Meter of Concrete)")
        
        # Using Streamlit metric boxes for prominent visual presentation
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Target Mean Strength", value=f"{target_strength:.2f} N/mm²")
        m2.metric(label="Cement Content", value=f"{cement_content:.2f} kg/m³")
        m3.metric(label="Water Content", value=f"{calculated_water:.2f} kg/m³")
        
        m4, m5 = st.columns(2)
        m4.metric(label="Fine Aggregate (Sand)", value=f"{mass_fa:.2f} kg/m³")
        m5.metric(label="Coarse Aggregate (Stone)", value=f"{mass_ca:.2f} kg/m³")

except Exception as e:
    st.error(f"Execution error. Please check your structural metrics: {e}")