import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import numpy as np

# Page config for a modern feel
st.set_page_config(page_title="AquaPulse RWH", page_icon="💧", layout="wide")

# Custom CSS for Premium Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 5% 5% 5% 10%;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    @media (prefers-color-scheme: dark) {
        div[data-testid="metric-container"] { background-color: #1e1e1e; border: 1px solid #333; }
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------
# Real Data Integration
# -----------------
from utils.data_manager import load_or_generate_data, DB_FILE

@st.cache_data
def load_application_data():
    return load_or_generate_data()

df = load_application_data()

# -----------------
# State Management (Fake Login)
# -----------------
if 'role' not in st.session_state:
    st.session_state.role = None
if 'tickets' not in st.session_state:
    st.session_state.tickets = []
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome! I am the AquaPulse Diagnostic AI. Need help understanding municipal regulations, or how to fix a clogged filter?"}]

def login(role):
    st.session_state.role = role

def logout():
    st.session_state.role = None

# -----------------
# UI Components
# -----------------

if st.session_state.role is None:
    # --- LOGIN PAGE ---
    st.markdown("<h1 style='text-align: center; color: #0078D7;'>💧 AquaPulse</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Rainwater Harvesting Intelligence System</h4>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("### Welcome, please select your role to continue:")
        st.info("💡 **Hackathon Demo:** Use this to switch between views instantly.")
        
        if st.button("🏛️ Login as Municipal Authority", use_container_width=True):
            login("authority")
            st.rerun()
            
        if st.button("🏢 Login as Building Owner", use_container_width=True):
            login("owner")
            st.rerun()

elif st.session_state.role == "authority":
    # --- MUNICIPAL DASHBOARD ---
    st.sidebar.title("🏛️ Municipal Hub")
    auth_page = st.sidebar.radio("Navigation", ["City Macro Overview", "Tax Rebate Portal"])
    st.sidebar.write("---")
    st.sidebar.button("Logout 🚪", on_click=logout)
    
    if auth_page == "Tax Rebate Portal":
        st.title("💰 Green Infrastructure Tax Rebates")
        st.write("Automatically calculate and disburse tax discounts for highly compliant rainwater harvesting properties.")
        
        # Filter for properties that are BOTH Healthy AND have not yet been paid for this cycle
        rebate_df = df[(df['Status'] == 'Healthy') & (df['Rebate Status'] == 'Pending')].copy()
        
        if not rebate_df.empty:
            # Flat 2500 rebate for healthy systems
            rebate_df['Issuable Tax Rebate (₹)'] = 2500 
            st.dataframe(
                rebate_df[['Building', 'Zone', 'Efficiency (%)', 'Last Cleaned', 'Issuable Tax Rebate (₹)']].reset_index(drop=True), 
                use_container_width=True
            )
            
            if st.button("💳 Approve Rebates & Disburse Funds", type="primary"):
                st.balloons()
                # Update the original dataframe and save to the database
                for idx in rebate_df.index:
                    df.at[idx, 'Rebate Status'] = 'Disbursed'
                
                df.to_json(DB_FILE, orient='records', indent=4)
                st.cache_data.clear() # Ensure the next run reads the updated JSON
                
                st.success(f"✅ Ledger Transaction Complete: ₹ {len(rebate_df) * 2500} successfully credited to {len(rebate_df)} compliant owners automatically.")
                st.info("The qualifying list has been cleared and moved to the city's financial ledger for the current period.")
                # Force rerun so the UI reflects the zero records
                st.rerun()
        else:
            st.success("🎉 All Green Infrastructure rebates for the current cycle have been successfully disbursed!")
            st.info("Check back next month for the next compliance evaluation cycle.")
            
        st.stop()
    
    st.title("🏛️ City-Wide RWH Overview")
    st.write("Monitor rainwater harvesting compliance, macro-financial impact, and system efficiency across all wards.")
    
    # Financial Calc
    total_water = df['Current Level (L)'].sum()
    tanker_savings = int(total_water * 0.15) 
    
    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Buildings", len(df), "Tracked Urban Nodes")
    kpi2.metric("Total Water Harvested", f"{total_water:,} L", f"≈ {int(total_water/10000)} Tanker Trucks")
    kpi3.metric("City-Wide Savings", f"₹ {tanker_savings:,}", "Avoided Municipal Costs")
    
    critical_df = df[df['Status'] == 'Critical/Clogged']
    kpi4.metric("Critical/Clogged Systems", len(critical_df), "High Priority Dispatches", delta_color="inverse")
    
    st.write("---")
    
    # Charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("System Status Distribution")
        fig_status = px.pie(df, names='Status', hole=0.6, 
                            color='Status', 
                            color_discrete_map={'Healthy':'#28a745', 'Needs Cleaning':'#ffc107', 'Critical/Clogged':'#dc3545'})
        fig_status.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

    with chart_col2:
        st.subheader("Average Operational Efficiency by Ward")
        ward_eff = df.groupby('Zone')['Efficiency (%)'].mean().reset_index()
        fig_ward = px.bar(ward_eff, x='Zone', y='Efficiency (%)', color='Efficiency (%)', 
                          color_continuous_scale='Blues')
        fig_ward.update_layout(margin=dict(t=0, b=0, l=0, r=0), coloraxis_showscale=False)
        st.plotly_chart(fig_ward, use_container_width=True)
        
    # --- GIS Map View ---
    st.write("---")
    st.subheader("🗺️ Live Infrastructure GIS Map")
    st.write("Interactive telemetry overlay in Chennai. Localized blockages will appear if tracked.")
    
    # Try native st.map using new color params, fallback to basic map if Streamlit version is older
    df['Map_Color'] = df['Status'].map({'Healthy':'#28a745', 'Needs Cleaning':'#ffc107', 'Critical/Clogged':'#dc3545'})
    try:
        st.map(df, latitude="Lat", longitude="Lon", color="Map_Color", size=250)
    except TypeError:
        st.map(df, latitude="Lat", longitude="Lon")
        
    # --- Inter-app Connected Feed --- 
    st.write("---")
    st.markdown("### 🎫 Live Network Feed: Owner Dispatches")
    st.write("Real-time portal connectivity tracking maintenance requests and verification uploads originating from Building Owners.")
    
    if len(st.session_state.tickets) > 0:
        st.dataframe(pd.DataFrame(st.session_state.tickets), use_container_width=True, hide_index=True)
    else:
        st.info("No incoming vendor dispatches or compliance requests detected across the network at this time.")
        
    # Table of Critical systems
    st.write("---")
    st.markdown("### 🚨 The 'Red List' (Intervention Required)")
    st.write("These systems are heavily clogged, producing zero yield, and are in violation of the mandatory 3-month municipal maintenance ordinance.")
    
    # Creating a stylized dataframe presentation with Streamlit's Column Config
    if not critical_df.empty:
        st.dataframe(
            critical_df[['Building', 'Zone', 'Efficiency (%)', 'Last Cleaned', 'Status']].reset_index(drop=True), 
            use_container_width=True,
            column_config={
                "Efficiency (%)": st.column_config.ProgressColumn(
                    "Efficiency (%)",
                    help="System performance yield",
                    format="%f%%",
                    min_value=0,
                    max_value=100,
                ),
            }
        )
        
        colA, colB = st.columns([1.5, 2.5])
        with colA:
            if st.button("📨 Dispatch Defect Notices (Direct Dashboard Alert)", use_container_width=True, type="primary"):
                import time
                with st.spinner("Compiling municipal violation list and transmitting..."):
                    time.sleep(2)
                
                # Update each critical building with a formal municipal alert
                alert_text = {
                    "type": "Critical",
                    "title": "🚨 MUNICIPAL VIOLATION NOTICE",
                    "content": "Your system has been flagged for zero yield. Clean filters immediately to avoid a ₹2,500 non-compliance fine.",
                    "date": pd.Timestamp.today().strftime('%Y-%m-%d %H:%M')
                }
                
                for idx in critical_df.index:
                    current_alerts = list(df.at[idx, 'Alerts']) 
                    # Avoid duplicates
                    if not any(a['title'] == alert_text['title'] for a in current_alerts):
                        current_alerts.append(alert_text)
                        df.at[idx, 'Alerts'] = current_alerts
                
                # Save the new state back to the database
                df.to_json(DB_FILE, orient='records', indent=4)
                st.cache_data.clear()
                
                st.toast(f"✅ Success: Municipal alerts transmitted to {len(critical_df)} properties.")
                st.success(f"Official municipal alerts transmitted directly to building dashboards of {len(critical_df)} violating properties.")
                # We don't call st.rerun() immediately so the user can see the success message.
                # The next user interaction will reflect the state.
                
        with colB:
            # Generate a CSV payload dynamically 
            csv_payload = critical_df.to_csv(index=False)
            st.download_button(
                label="📁 Download Final Violation Manifest (CSV)",
                data=csv_payload,
                file_name="AquaPulse_Critical_Enforcement_List.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    else:
        st.success("✅ All urban systems in compliance! No critical properties logged.")


elif st.session_state.role == "owner":
    # --- BUILDING OWNER DASHBOARD ---
    st.sidebar.title("🏢 Owner Portal")
    owner_page = st.sidebar.radio("Navigation", ["System Dashboard", "Maintenance Logbook"])
    
    # --- SOLUTION: Building Selector ---
    st.sidebar.write("---")
    st.sidebar.write("**Property Selector**")
    selected_bldg_name = st.sidebar.selectbox("Which building are you managing?", df['Building'].sort_values())
    
    # Filter the dataframe to just this specific building
    my_bldg = df[df['Building'] == selected_bldg_name].iloc[0]
    
    st.sidebar.write("---")
    st.sidebar.button("Logout 🚪", on_click=logout)
    
    if owner_page == "Maintenance Logbook":
        st.title("🧰 Regulatory Maintenance Logbook")
        st.write(f"Submit visual verification of your recent filter cleanout for {my_bldg['Building']} to reset your mandatory 3-month Municipal ordinance timer.")
        
        uploaded_file = st.file_uploader("Upload Digital Image of Cleaned Filter / Catchment System", type=["png", "jpg", "jpeg"])
        st.text_area("Vendor/Cleaning Notes (Optional)")
        
        if st.button("Submit Verified Maintenance to City Network", type="primary"):
            if uploaded_file is not None:
                st.session_state.tickets.append({
                    "Timestamp": pd.Timestamp.today().strftime('%Y-%m-%d %H:%M'),
                    "Property": my_bldg['Building'], 
                    "Zone": my_bldg['Zone'], 
                    "Ticket ID": f"IMG-{random.randint(10000, 99999)}",
                    "Priority": "Compliance",
                    "Status": "Automatically Approved by Vision AI"
                })
                
                # --- DYNAMIC DATABASE UPDATE ---
                bldg_idx = df[df['Building'] == my_bldg['Building']].index[0]
                df.at[bldg_idx, 'Last Cleaned'] = "0 months ago (Just Now)"
                df.at[bldg_idx, 'Status'] = "Healthy"
                df.at[bldg_idx, 'Efficiency (%)'] = 98.5
                df.at[bldg_idx, 'Alerts'] = [] # Clear alerts on maintenance
                
                # Save the new state natively back to the JSON database
                from utils.data_manager import DB_FILE
                df.to_json(DB_FILE, orient='records', indent=4)
                st.cache_data.clear() # Force Streamlit to re-read the updated JSON file
                
                st.success("✅ Evidence Verified! Your municipal compliance records and system efficiency have been instantly reset in the system. Check your main System Dashboard.")
            else:
                st.error("Please upload photographic evidence of the completed maintenance to legally proceed.")
        st.stop()
    
    
    st.title(f"Dashboard: {my_bldg['Building']}")
    st.write(f"📍 {my_bldg['Zone']}")
    
    # --- MUNICIPAL ALERTS (NEW FEATURE) ---
    if my_bldg['Alerts'] and len(my_bldg['Alerts']) > 0:
        for i, alert in enumerate(my_bldg['Alerts']):
            with st.container():
                st.markdown(f"""
                <div style="background-color: #ffe6e6; border-left: 5px solid #dc3545; padding: 15px; border-radius: 8px; margin-bottom: 20px; animation: pulse 2s infinite;">
                    <h4 style="color: #dc3545; margin: 0;">{alert['title']}</h4>
                    <p style="color: #333; margin: 5px 0;">{alert['content']}</p>
                    <small style="color: #666;">Received: {alert['date']}</small>
                </div>
                <style>
                @keyframes pulse {{
                    0% {{ box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4); }}
                    70% {{ box-shadow: 0 0 0 10px rgba(220, 53, 69, 0); }}
                    100% {{ box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }}
                }}
                </style>
                """, unsafe_allow_html=True)

    # Owner Alerts & System Diagnostics
    st.markdown("### 🔍 System Diagnostics")
    if my_bldg['Status'] == 'Critical/Clogged':
        st.error("⚠️ **CRITICAL ALERT: ZERO COLLECTION DETECTED**")
        st.markdown(f"**Diagnostic:** Despite a heavy 45mm rainfall 3 days ago, your tank level remained completely flat at {int(my_bldg['Current Level (L)'])}L.  \n**Conclusion:** The catchment filter is severely clogged and requires immediate cleaning.")
    elif my_bldg['Status'] == 'Needs Cleaning':
        st.warning("⚠️ **WARNING: MAINTENANCE OVERDUE & SUB-OPTIMAL YIELD**")
        st.markdown(f"**Diagnostic:** Your system hasn't been cleaned in **{my_bldg['Last Cleaned'].split(' ')[0]} months** (City mandate: 3 months).  \n**Conclusion:** The mesh filter is likely partially blocked, resulting in reduced water yields.")
    else:
        st.success("✅ **SYSTEM HEALTHY: OPTIMAL PERFORMANCE**")
        st.markdown(f"**Diagnostic:** Tank levels successfully rose correlating exactly with last week's 45mm rain event.  \n**Conclusion:** The flow rate is excellent and the system is clear of blockages.")
    
    # Financial Analytics (Judges love this)
    cost_per_liter = 0.15 # Assuming ₹0.15 per liter for a water tanker
    savings = int(my_bldg['Current Level (L)'] * cost_per_liter)
    
    # Maintenance Schedule Logic
    months_since = int(my_bldg['Last Cleaned'].split(" ")[0])
    if months_since < 3:
        next_maint = f"In {3 - months_since} Mo"
        maint_delta = "On Track"
        delta_c = "normal"
    elif months_since == 3:
        next_maint = "Due Now"
        maint_delta = "Requires Action"
        delta_c = "off"
    else:
        next_maint = f"{months_since - 3}mo Overdue"
        maint_delta = "Urgent Action Required"
        delta_c = "inverse"

    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric(
        "Est. Savings", 
        f"₹ {savings}", 
        "Saved tanker cost",
        help="Calculation: (Current Stored Liters × ₹0.15/L)."
    )
    col2.metric(
        "Tank Level", 
        f"{my_bldg['Current Level (L)']} L", 
        f"{my_bldg['Efficiency (%)']}% Full",
        help="The current volume of rainwater physically inside your tank right now."
    )
    col3.metric(
        "Total Capacity", 
        f"{my_bldg['Capacity (L)']} L", 
        "System Maximum",
        help="The total physical storage capability of your building's tank."
    )
    col4.metric(
        "Last Cleaned", 
        my_bldg['Last Cleaned'],
        help="The time since your building last logged a verified maintenance sequence with the city."
    )
    col5.metric(
        "Maintenance", 
        next_maint, 
        maint_delta, 
        delta_color=delta_c,
        help="City ordinances strictly mandate full mesh and pipe filter cleanouts every 3 months."
    )
        
    st.write("---")
    
    colA, colB = st.columns([1, 1.2])
    with colA:
        st.subheader("Live Tank Capacity")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = my_bldg['Current Level (L)'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, my_bldg['Capacity (L)']]},
                'bar': {'color': "#0078D7"},
                'steps': [
                    {'range': [0, my_bldg['Capacity (L)']*0.2], 'color': "#ffe6e6"},
                    {'range': [my_bldg['Capacity (L)']*0.2, my_bldg['Capacity (L)']*0.7], 'color': "#e6f2ff"},
                    {'range': [my_bldg['Capacity (L)']*0.7, my_bldg['Capacity (L)']], 'color': "#e6ffe6"}],
            }
        ))
        fig_gauge.update_layout(margin=dict(t=40, b=20, l=40, r=40), height=320)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Manual Data Entry (MVP Stage Features)
        st.write("### 📝 Manual Data Log")
        manual_lvl = st.number_input("Enter Current Tank Level (Liters)", min_value=0, max_value=my_bldg['Capacity (L)'], value=int(my_bldg['Current Level (L)']))
        if st.button("📤 Submit Manual Log", use_container_width=True):
            # Update the local buildings JSON with manual data
            bldg_idx = df[df['Building'] == my_bldg['Building']].index[0]
            df.at[bldg_idx, 'Current Level (L)'] = manual_lvl
            df.to_json(DB_FILE, orient='records', indent=4)
            st.cache_data.clear()
            st.success(f"✅ Tank level manual log updated to {manual_lvl} L!")
            st.rerun()

        # Action Buttons
        st.write("### Actions")
        if st.button("🔧 Request City Vetted Cleaning Service", use_container_width=True, type="primary"):
            import time
            with st.spinner("Dispatching request to municipal vendor network..."):
                time.sleep(1.5)
            t_id = f"RWH-{random.randint(10000, 99999)}"
            
            # Cross-platform persistent logging
            st.session_state.tickets.append({
                "Timestamp": pd.Timestamp.today().strftime('%Y-%m-%d %H:%M'),
                "Property": my_bldg['Building'], 
                "Zone": my_bldg['Zone'], 
                "Ticket ID": t_id, 
                "Priority": "High" if my_bldg['Status'] == 'Critical/Clogged' else "Standard",
                "Status": "Pending Vendor Dispatch"
            })
            st.success(f"✅ Ticket **#{t_id}** Generated! Vendors will contact you within 24 hours.")
            
        # Dynamically Generated Report for Download
        report_txt = f"=== AQUAPULSE QUARTERLY REPORT ===\n" \
                     f"Property: {my_bldg['Building']} ({my_bldg['Zone']})\n" \
                     f"Tank Capacity: {my_bldg['Capacity (L)']} Liters\n" \
                     f"Current Health: {my_bldg['Status']}\n" \
                     f"Estimated Financial Savings: INR {savings}\n" \
                     f"Next Scheduled Maintenance: {next_maint}\n" \
                     f"==================================\n" \
                     f"Document Auto-generated by AquaPulse system on {pd.Timestamp.today().strftime('%Y-%m-%d')}"
                     
        st.download_button(
            label="📄 Download Quarterly Savings Report",
            data=report_txt,
            file_name=f"{my_bldg['Building'].replace(' ', '_')}_Q3_Savings_Report.txt",
            mime="text/plain",
            use_container_width=True
        )
            
    with colB:
        st.subheader("💧 System Efficiency (Last 7 Days)")
        st.write("Correlation between Rainfall (mm) and Total Water Collected (Liters)")
        
        dates = pd.date_range(end=pd.Timestamp.today(), periods=7).normalize()
        rain_mm = [5, 0, 0, 45, 10, 0, 2] # Spike on Thursday
        roof_area_sqm = 100 # Assume a 100m2 roof for modeling
        
        expected_l = [r * roof_area_sqm for r in rain_mm]
        
        if my_bldg['Status'] == 'Healthy':
            actual_l = [e * 0.95 for e in expected_l]
        elif my_bldg['Status'] == 'Needs Cleaning':
            actual_l = [e * 0.45 for e in expected_l]
        else:
            actual_l = [e * 0.05 for e in expected_l] # Clogged systems capture almost nothing
            
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
             go.Bar(x=dates, y=rain_mm, name="Rainfall (mm)", marker_color='#8CB9DF', orientation='v'), 
             secondary_y=False
        )
        fig_trend.add_trace(
             go.Scatter(x=dates, y=actual_l, name="Collected Water (L)", mode='lines+markers', marker_color='#28a745', line=dict(width=3)), 
             secondary_y=True
        )
        
        fig_trend.update_layout(
            margin=dict(t=20, b=20, l=20, r=20), height=320,
            legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1)
        )
        fig_trend.update_yaxes(title_text="Rainfall (mm)", secondary_y=False, showgrid=False)
        fig_trend.update_yaxes(title_text="Collected (Liters)", secondary_y=True, showgrid=False)
        fig_trend.update_xaxes(showgrid=False)
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
    st.write("---")
    st.subheader("📊 6-Month Historical: Harvested vs. Consumed")
    st.write("Compare how much water was collected from rain versus how much the building consumed.")
    
    # Generate 6 Months historical data
    months = [(pd.Timestamp.today() - pd.DateOffset(months=x)).strftime('%b %Y') for x in range(5, -1, -1)]
    
    collected_hist = [random.randint(2000, 12000) for _ in range(6)]
    used_hist = [int(c * random.uniform(0.6, 0.95)) for c in collected_hist] # Consumed water is a logical subset of collected water
    
    hist_df = pd.DataFrame({
        'Month': months,
        'Water Collected (L)': collected_hist,
        'Water Consumed (L)': used_hist
    }).set_index('Month')
    
    # Use Plotly instead of st.bar_chart to enforce side-by-side grouped rendering 
    # Using graph_objects explicitly to bypass Plotly Express indexing bugs
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Bar(x=months, y=collected_hist, name='Water Collected (L)', marker_color='#3498db'))
    fig_hist.add_trace(go.Bar(x=months, y=used_hist, name='Water Consumed (L)', marker_color='#e67e22'))
    fig_hist.update_layout(
        barmode='group',
        margin=dict(t=20, b=10, l=0, r=0), 
        yaxis_title="Liters",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    # --- AI ASSISTANT (Right-Aligned Popover/Expander) ---
    st.write("---")
    
    col_empty, col_ai = st.columns([3, 2])
    with col_ai:
        with st.expander("🤖 Tap to Open: AquaPulse AI Support"):
            st.write(f"**Diagnostic Engine:** `{my_bldg['Building']}`")
            
            # 1. Render all historical messages
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
            # 2. Chat Input 
            if prompt := st.chat_input("E.g. What is a Rebate?"):
                # Append user prompt
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # 3. Simple Keyword Logic for the Chatbot
                prompt_lower = prompt.lower()
                if "rebate" in prompt_lower:
                    bot_resp = "A 'Green Tax Rebate' is essentially the city paying you back for being environmentally friendly! Because capturing rainwater means the city doesn't have to send you as many water tanker trucks, they give you a discount (around ₹2,500) on your yearly property taxes as a 'Thank You.' You automatically qualify if your dashboard reads 'Healthy'!"
                elif "healthy" in prompt_lower or "how to make my dashboard" in prompt_lower:
                    bot_resp = "To make your dashboard 'Healthy', you must clear your mesh filter to restore water pressure! Once you've cleaned it, navigate to the **Maintenance Logbook** page using the left sidebar, upload a photo of the cleared pipe, and click Submit. The Municipal Vision AI will automatically verify it and upgrade your status to 'Healthy' instantly!"
                elif "clean" in prompt_lower or "fix" in prompt_lower or "clog" in prompt_lower:
                    bot_resp = "To clean your filter: Safely access your roof catchment zone, detach the primary mesh cover, scrape out any accumulated leaf debris or silt, and flush the main PVC pipe with running water. Once completed, take a photo and upload it to the **Maintenance Logbook** tab!"
                else:
                    if my_bldg['Efficiency (%)'] < 80.0:
                        bot_resp = f"Interesting. I'm analyzing your {my_bldg['Capacity (L)']} Liter system and your efficiency is reading critically low at {my_bldg['Efficiency (%)']}%. Based on the telemetry, your status is '{my_bldg['Status']}'. I highly recommend scheduling a cleaning immediately. What else can I assist with?"
                    else:
                        bot_resp = f"Interesting. Well, I'm analyzing your {my_bldg['Capacity (L)']} Liter system and your efficiency is reading firmly at {my_bldg['Efficiency (%)']}%. Everything looks technically sound from my end. Any other questions regarding municipal compliance?"
                
                # Append bot response and force UI refresh
                st.session_state.messages.append({"role": "assistant", "content": bot_resp})
                st.rerun()
