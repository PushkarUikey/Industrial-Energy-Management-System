import sqlite3


def view_recent_data():
    # 1. Connect to your database
    conn = sqlite3.connect('factory_data.db')
    cursor = conn.cursor()

    # 2. Fetch the last 10 rows created
    cursor.execute("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()

    # 3. Print them neatly
    print("\n--- 🏭 LAST 10 FACTORY READINGS ---")
    for row in rows:
        timestamp = row[1]
        machine = row[2]
        voltage = row[3]
        temp = row[4]
        power = row[5]
        anomaly = "⚠️ YES" if row[6] == 1 else "No"

        print(f"[{timestamp}] {machine} | {voltage}V | {temp}°C | {power}kW | Anomaly: {anomaly}")

    conn.close()


if __name__ == "__main__":
    view_recent_data()