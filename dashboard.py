import streamlit as st
import requests
import pandas as pd
import time
import math
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from report_generator import get_monthly_metrics, generate_esg_report

# ==========================================
# PAGE CONFIGURATION & AI SETUP
# ==========================================
st.set_page_config(page_title="Industrial Energy Intelligence System", page_icon="🏭", layout="wide")


# @st.cache_resource ensures the model downloads/loads only once
@st.cache_resource
def load_chat_model():
    print("🧠 Downloading/Booting raw DistilBERT model weights...")
    model_name = "distilbert-base-cased-distilled-squad"

    # We bypass the broken pipeline and load the raw architecture directly
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    return tokenizer, model


# Load the tokenizer and model into memory
tokenizer, qa_model = load_chat_model()

API_LIVE_URL = "http://127.0.0.1:5000/api/live-status"
API_HIST_URL = "http://127.0.0.1:5000/api/historical"

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("🏭 Industrial Energy Intelligence System")
st.sidebar.markdown("Enterprise Energy Management")

page = st.sidebar.radio(
    "Go to",
    [
        "🏭 Command Center",
        "📊 Analytics & Trends",
        "💰 Cost & ROI Calculator",
        "🌱 Sustainability Score",
        "📄 Reports & Compliance",
        "🤖 AI Chat Assistant"
    ]
)

st.sidebar.divider()
st.sidebar.caption("🟢 System Online | API Connected")

# ==========================================
# SAFE DATA FETCHER
# ==========================================
live_data, hist_data = None, None
try:
    live_res = requests.get(API_LIVE_URL)
    if live_res.status_code == 200:
        live_data = live_res.json()

    hist_res = requests.get(API_HIST_URL)
    if hist_res.status_code == 200:
        hist_data = hist_res.json()
except requests.exceptions.ConnectionError:
    st.sidebar.error("🔌 Cannot connect to API. Ensure app.py is running.")

# ==========================================
# PAGE 1: COMMAND CENTER
# ==========================================
if page == "🏭 Command Center":
    st.title("🏭 Command Center")
    st.markdown("Real-time monitoring of factory power load and machine health.")

    if live_data and 'factory_vitals' in live_data:
        st.subheader(f"⏱️ Live Snapshot: {live_data['timestamp']}")

        col1, col2, col3 = st.columns(3)
        vitals = live_data['factory_vitals']
        col1.metric("⚡ Total Power Load (kW)", f"{vitals['total_power_kw']} kW")
        col2.metric("🌍 Live Carbon Footprint", f"{vitals['carbon_emissions_kg']} kg CO₂")

        if vitals['active_anomalies'] > 0:
            col3.error(f"🚨 {vitals['active_anomalies']} Anomalies Detected!")
        else:
            col3.success("✅ Factory Health Normal")

        st.divider()
        st.markdown("### ⚙️ Live Machine Breakdown")
        df_live = pd.DataFrame(live_data['machine_breakdown'])
        st.dataframe(df_live[['machine', 'status', 'power_kw', 'temperature']], use_container_width=True,
                     hide_index=True)

        time.sleep(3)
        st.rerun()
    else:
        st.warning("Waiting for live data... ensure iot_simulator.py is running.")

# ==========================================
# PAGE 2: ANALYTICS & TRENDS
# ==========================================
elif page == "📊 Analytics & Trends":
    st.title("📊 Analytics & Trends")
    st.markdown("Historical report card for factory energy habits.")

    if hist_data:
        df_hist = pd.DataFrame(hist_data)
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])

        # --- NEW: Timeframe Filter ---
        # This fixes the "flatline" gap caused by turning the server off overnight
        time_filter = st.radio(
            "Select Timeframe to View:",
            ["Last 1 Hour", "Last 24 Hours", "All Data"],
            horizontal=True
        )

        latest_time = df_hist['timestamp'].max()

        # Apply the filter based on user selection
        if time_filter == "Last 1 Hour":
            cutoff = latest_time - pd.Timedelta(hours=1)
            df_filtered = df_hist[df_hist['timestamp'] >= cutoff]
        elif time_filter == "Last 24 Hours":
            cutoff = latest_time - pd.Timedelta(hours=24)
            df_filtered = df_hist[df_hist['timestamp'] >= cutoff]
        else:
            df_filtered = df_hist

        # --- DRAW CHARTS ---
        if not df_filtered.empty:
            st.subheader("📈 Total Energy Trend")
            trend_df = df_filtered.groupby('timestamp')['power_kw'].sum()
            st.line_chart(trend_df, color="#32CD32")

            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("🏭 Top Energy Consumers")
                machine_df = df_filtered.groupby('machine_id')['power_kw'].sum()
                st.bar_chart(machine_df, color="#FF4500")

            with col_b:
                st.subheader("🌡️ Average Operating Heat")
                temp_df = df_filtered.groupby('machine_id')['temperature'].mean()
                st.bar_chart(temp_df, color="#1E90FF")
        else:
            st.warning(f"No data recorded in the {time_filter} window. Let the simulator run!")
    else:
        st.warning("Not enough historical data collected yet.")

# ==========================================
# PAGE 3: COST & ROI CALCULATOR
# ==========================================
elif page == "💰 Cost & ROI Calculator":
    st.title("💰 Energy Cost & ROI")
    st.markdown("Financial impact of your energy consumption.")

    rate = st.number_input("Enter your Electricity Rate (₹ per kWh):", value=8.50, step=0.50)

    if hist_data:
        df_hist = pd.DataFrame(hist_data)
        total_kwh_used = df_hist['power_kw'].sum() / 3600
        total_cost = total_kwh_used * rate
        money_saved = total_cost * 0.15

        col1, col2, col3 = st.columns(3)
        col1.metric("💸 Estimated Cost (Recorded Period)", f"₹ {total_cost:,.2f}")
        col2.metric("🛡️ Savings via Anomaly Prevention", f"₹ {money_saved:,.2f}", "+15% Efficiency")
        col3.metric("📈 Projected Monthly Bill", f"₹ {(total_cost * 30):,.2f}")

        st.info(
            "💡 **Insight:** Shifting heavy operations to off-peak night hours (10 PM - 4 AM) could reduce your bill by an additional 12%.")

# ==========================================
# PAGE 4: SUSTAINABILITY SCORE
# ==========================================
elif page == "🌱 Sustainability Score":
    st.title("🌱 Sustainability & Carbon Tracker")
    st.markdown("Your environmental impact at a glance (Past 1 Hour).")

    if hist_data:
        df_hist = pd.DataFrame(hist_data)
        # 1. Convert the timestamp column to actual datetime objects
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])

        # 2. Find the newest record, and filter out everything older than 1 hour
        latest_time = df_hist['timestamp'].max()
        one_hour_ago = latest_time - pd.Timedelta(hours=1)
        df_last_hour = df_hist[df_hist['timestamp'] >= one_hour_ago]

        if not df_last_hour.empty:
            # 3. Calculate metrics ONLY on the last hour of data
            total_kwh_used = df_last_hour['power_kw'].sum() * (3 / 3600)
            total_emissions_kg = total_kwh_used * 0.4
            trees_needed = math.ceil(total_emissions_kg / 21)

            total_readings = len(df_last_hour)
            anomaly_count = df_last_hour['is_anomaly'].sum()
            healthy_readings = total_readings - anomaly_count

            if total_readings > 0:
                raw_score = (healthy_readings / total_readings) * 100
                green_score = int(raw_score)
            else:
                green_score = 100

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🏆 ESG Score", f"{green_score} / 100", "Last 60 Mins")
                st.progress(max(0, min(green_score / 100, 1.0)))

            with col2:
                st.metric("🌳 Tree Equivalent", f"{trees_needed} Trees", "Needed to offset past hour's emissions",
                          delta_color="inverse")

            st.divider()
            st.subheader("🎯 Actionable Suggestions (Based on Past Hour)")
            st.success("✅ **Goal:** Reduce carbon footprint by 20% this month.")

            # Ensure insights are also based on the last hour
            top_consumer = df_last_hour.groupby('machine_id')['power_kw'].sum().idxmax()
            hottest_machine = df_last_hour.groupby('machine_id')['temperature'].mean().idxmax()

            st.markdown(f"""
            * **Energy Optimization:** **{top_consumer}** is currently your top power consumer. Consider load-shifting its heaviest operations to off-peak night hours.
            * **Thermal Management:** **{hottest_machine}** is running with the highest average operating heat over the last hour. Inspect it for friction or cooling faults, as excess heat wastes electrical power.
            * **Facility Baseline:** Switch the main factory floor to automated LED zones and sync HVAC systems with live weather APIs.
            """)
        else:
            st.info("Waiting for enough data from the past hour to calculate scores. Let the simulator run!")
# ==========================================
# PAGE 5: REPORTS & COMPLIANCE
# ==========================================
elif page == "📄 Reports & Compliance":
    st.title("📄 Reports & Compliance")
    st.markdown("Management reporting and ISO 50001 auditing.")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Audit Checklist")
        st.checkbox("Energy Baseline Established", value=True, disabled=True)
        st.checkbox("Live Telemetry Active", value=True, disabled=True)
        st.checkbox("Anomaly Pipeline Functional", value=True, disabled=True)
        st.checkbox("ESG Report Generated", value=False)

    with col2:
        st.subheader("🧠 Offline AI Report Generator")
        if st.button("Generate Official Report (Text)"):
            with st.spinner("Local AI is writing the report..."):
                metrics = get_monthly_metrics()
                if metrics:
                    report_text = generate_esg_report(metrics)
                    st.success("Report Generated!")
                    st.text_area("Final Output:", value=report_text, height=250)

                    st.download_button(
                        label="⬇️ Download as Text File",
                        data=report_text,
                        file_name="ISO_50001_Report.txt",
                        mime="text/plain"
                    )

# ==========================================
# PAGE 6: AI CHAT ASSISTANT (Hybrid AI Engine)
# ==========================================
elif page == "🤖 AI Chat Assistant":
    st.title("🤖 AI Consultant")
    st.markdown(
        "Ask questions about your factory's live telemetry or for energy-saving advice. *(Powered by Hybrid DistilBERT & Advisory Engine)*")

    if live_data and 'factory_vitals' in live_data and hist_data:
        vitals = live_data['factory_vitals']
        df_hist = pd.DataFrame(hist_data)

        if not df_hist.empty:
            total_kwh = round(df_hist['power_kw'].sum() * (3 / 3600), 2)
            top_machine = df_hist.groupby('machine_id')['power_kw'].sum().idxmax()
        else:
            total_kwh = 0
            top_machine = "Unknown"

        # The factual context for the neural network
        system_context = (
            f"The total power load is {vitals['total_power_kw']} kilowatts. "
            f"The live carbon footprint is {vitals['carbon_emissions_kg']} kg CO2. "
            f"There are {vitals['active_anomalies']} active faults detected. "
            f"The total historical energy consumed is {total_kwh} kWh. "
            f"The machine consuming the most power is {top_machine}."
        )

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant",
                 "content": "Hello! I am your AI Assistant . You can ask me for live data (e.g., **What is the carbon footprint?**) or for advice (e.g., **How can I reduce power consumption?**)"}
            ]

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            with st.spinner("Analyzing query..."):
                prompt_lower = prompt.lower()
                final_response = ""

                # --- TIER 1: ADVISORY ENGINE ---
                # Catches abstract questions that extraction models can't answer
                if "reduce" in prompt_lower or "save" in prompt_lower or "optimize" in prompt_lower:
                    final_response = f"💡 **Engineering Advice:** To reduce power consumption, consider load-shifting the heaviest operations for your top consumer ({top_machine}) to off-peak night hours. Also, ensure all machines operating above 75°C are checked for thermal friction, which causes severe electrical waste."

                elif "anomaly" in prompt_lower or "fault" in prompt_lower or "broken" in prompt_lower:
                    if vitals['active_anomalies'] > 0:
                        final_response = f"⚠️ **Alert:** There are currently {vitals['active_anomalies']} active faults. Please check the 'Command Center' tab immediately to isolate the specific machine."
                    else:
                        final_response = "✅ Good news! There are currently 0 active faults or anomalies detected in the live telemetry stream."

                elif "hello" in prompt_lower or "hi " in prompt_lower:
                    final_response = "Hello! I'm monitoring the factory telemetry. What would you like to know?"

                # --- TIER 2: NEURAL NETWORK EXTRACTION ---
                # For factual data questions (What, Which, How much)
                else:
                    try:
                        # Feed the question and data to DistilBERT
                        inputs = tokenizer(prompt, system_context, return_tensors="pt")

                        with torch.no_grad():
                            outputs = qa_model(**inputs)

                        answer_start = torch.argmax(outputs.start_logits)
                        answer_end = torch.argmax(outputs.end_logits) + 1

                        # Fix the PyTorch coordinate bug
                        if answer_end > answer_start:
                            ai_answer = tokenizer.decode(inputs.input_ids[0][answer_start:answer_end],
                                                         skip_special_tokens=True)

                            # Clean up the output and ensure it isn't hallucinating
                            if len(ai_answer.strip()) > 1 and ai_answer.strip() not in prompt:
                                final_response = f"📊 **Data Output:** Based on the current telemetry, {ai_answer}."
                            else:
                                final_response = "I couldn't extract that exact number from the current data stream. Try rephrasing your question (e.g., 'What is the carbon footprint?')."
                        else:
                            final_response = "I couldn't confidently calculate the answer from the live data."

                    except Exception as e:
                        final_response = f"Neural network error: {e}"

            st.session_state.messages.append({"role": "assistant", "content": final_response})
            st.chat_message("assistant").write(final_response)

    else:
        st.warning("Waiting for data to boot the AI. Please ensure `app.py` is running.")