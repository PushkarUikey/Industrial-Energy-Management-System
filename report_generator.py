import sqlite3
from transformers import pipeline
from datetime import datetime

# 1. Fetch the aggregated data from the database
def get_monthly_metrics():
    print("📊 Extracting telemetry data from secure database...")
    conn = sqlite3.connect('factory_data.db')
    cursor = conn.cursor()

    # Grab all data (In a real app, you'd filter by the last 30 days)
    cursor.execute("SELECT power_kw, is_anomaly FROM telemetry")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    total_power = sum([row[0] for row in rows])
    total_anomalies = sum([row[1] for row in rows])
    total_carbon = total_power * 0.4  # 0.4 kg CO2 per kWh

    return {
        "power": round(total_power, 2),
        "carbon": round(total_carbon, 2),
        "anomalies": total_anomalies
    }

# 2. The Local AI Engine
def generate_esg_report(metrics):
    print("🧠 Loading Local Transformer Model (GPT-2)...")
    # We use a text-generation pipeline.
    # The first time you run this, it will download the model to your PC.
    generator = pipeline('text-generation', model='gpt2')

    print("✍️ Generating Executive Summary...\n")

    # We "prime" the model by starting the professional report for it
    prompt = (
        f"ISO 50001 Energy & ESG Compliance Report - {datetime.now().strftime('%B %Y')}\n\n"
        f"Hard Metrics:\n"
        f"- Total Energy Consumed: {metrics['power']} kWh\n"
        f"- Carbon Footprint: {metrics['carbon']} kg CO2\n"
        f"- Equipment Faults Detected: {metrics['anomalies']}\n\n"
        f"Executive Summary of Operations:\n"
        f"During this operating period, the facility's energy management system tracked the metrics above. "
        f"The impact of these operations on our sustainability goals indicates that"
    )

    # Generate the rest of the text (Increased to 100 tokens)
    output = generator(
        prompt,
        max_new_tokens=100,
        num_return_sequences=1,
        temperature=0.7,  # Controls creativity (lower is more professional)
        pad_token_id=50256  # Standard padding for GPT-2
    )

    raw_text = output[0]['generated_text']

    # Clean up the output by cutting off any incomplete sentences at the end
    last_period_index = raw_text.rfind('.')
    if last_period_index != -1:
        clean_text = raw_text[:last_period_index + 1]
    else:
        clean_text = raw_text

    # 3. Save to a secure local file
    filename = f"ESG_Report_{datetime.now().strftime('%Y_%m_%d')}.txt"
    with open(filename, 'w') as file:
        file.write(clean_text)

    print(f"✅ SUCCESS: Official ESG Report generated and saved securely as '{filename}'.")
    return clean_text

if __name__ == "__main__":
    metrics = get_monthly_metrics()
    if metrics:
        generate_esg_report(metrics)
    else:
        print("❌ No data found in the database. Run the simulator first!")