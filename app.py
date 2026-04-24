from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# Standard grid emission factor
EMISSION_FACTOR = 0.4


def get_latest_data():
    conn = sqlite3.connect('factory_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# -----------------------------------------
# CORE API ENDPOINT (LIVE DATA)
# -----------------------------------------
@app.route('/api/live-status', methods=['GET'])
def live_status():
    latest_data = get_latest_data()

    if not latest_data:
        return jsonify({"error": "No data found."}), 404

    total_power = 0.0
    anomalies_detected = 0
    machine_details = []

    for row in latest_data:
        total_power += row['power_kw']
        if row['is_anomaly'] == 1:
            anomalies_detected += 1

        machine_details.append({
            "machine": row['machine_id'],
            "power_kw": row['power_kw'],
            "temperature": row['temperature'],
            "status": "⚠️ FAULT" if row['is_anomaly'] == 1 else "✅ Normal"
        })

    total_carbon_kg = round(total_power * EMISSION_FACTOR, 2)

    response = {
        "timestamp": latest_data[0]['timestamp'],
        "factory_vitals": {
            "total_power_kw": round(total_power, 2),
            "carbon_emissions_kg": total_carbon_kg,
            "active_anomalies": anomalies_detected
        },
        "machine_breakdown": machine_details
    }
    return jsonify(response)


# -----------------------------------------
# NEW: HISTORICAL ANALYTICS ENDPOINT
# -----------------------------------------
@app.route('/api/historical', methods=['GET'])
def historical_data():
    conn = sqlite3.connect('factory_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Grab the last 2000 records to build our charts
    cursor.execute("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 2000")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


if __name__ == '__main__':
    print("🚀 Starting OmniGreen Backend API on port 5000...")
    app.run(debug=True, port=5000)