import sqlite3
import time
import random
from datetime import datetime


# 1. Database Setup
def setup_database():
    conn = sqlite3.connect('factory_data.db')
    cursor = conn.cursor()
    # Create a table to store our simulated telemetry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            machine_id TEXT,
            voltage REAL,
            temperature REAL,
            power_kw REAL,
            is_anomaly INTEGER
        )
    ''')
    conn.commit()
    return conn


# 2. Logic to generate realistic fake data
def generate_machine_data():
    machines = ['Machine_1_Lathe', 'Machine_2_CNC', 'Machine_3_Press', 'Machine_4_Welder', 'Machine_5_Assembly']
    current_hour = datetime.now().hour

    data_batch = []

    for machine in machines:
        # Base voltage is usually stable around 480V for industrial
        voltage = round(random.uniform(475.0, 485.0), 2)

        # Determine if it's active shift hours (8 AM to 6 PM)
        if 8 <= current_hour <= 18:
            base_power = random.uniform(30.0, 50.0)  # Active power usage
            temp = random.uniform(60.0, 85.0)  # Running hot
        else:
            base_power = random.uniform(2.0, 5.0)  # Idle mode
            temp = random.uniform(25.0, 35.0)  # Cooled down

        # 3. Inject random Anomalies (Faults)
        is_anomaly = 0
        if random.random() < 0.05:  # 5% chance of a machine fault
            base_power += random.uniform(40.0, 60.0)  # Massive power spike
            temp += random.uniform(20.0, 40.0)  # Overheating
            is_anomaly = 1
            print(f"⚠️ ANOMALY GENERATED on {machine}!")

        power_kw = round(base_power, 2)
        temperature = round(temp, 2)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data_batch.append((timestamp, machine, voltage, temperature, power_kw, is_anomaly))

    return data_batch


# 4. Main Execution Loop
def run_factory_simulator():
    print("🏭 Starting Smart Factory IoT Simulator...")
    conn = setup_database()
    cursor = conn.cursor()

    try:
        while True:
            # Generate a batch of data for all 5 machines
            batch = generate_machine_data()

            # Insert into database
            cursor.executemany('''
                INSERT INTO telemetry (timestamp, machine_id, voltage, temperature, power_kw, is_anomaly)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', batch)
            conn.commit()

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged data for 5 machines.")

            # Wait 3 seconds before sending the next batch (simulating real-time)
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n🛑 Factory Simulator Stopped.")
        conn.close()


if __name__ == "__main__":
    run_factory_simulator()