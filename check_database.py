import sqlite3

# Connect to database
conn = sqlite3.connect('attendance.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all attendance records
records = cursor.execute('''
    SELECT 
        id, user_id, check_in_time, check_out_time,
        checkin_latitude, checkin_longitude, 
        checkout_latitude, checkout_longitude,
        city, full_address,
        checkout_city, checkout_full_address,
        status
    FROM attendance 
    ORDER BY check_in_time DESC 
    LIMIT 5
''').fetchall()

print("=" * 80)
print("RECENT ATTENDANCE RECORDS")
print("=" * 80)

for record in records:
    print(f"\n📋 Record ID: {record['id']}")
    print(f"   User ID: {record['user_id']}")
    print(f"   Check In: {record['check_in_time']}")
    print(f"   Check Out: {record['check_out_time']}")
    print(f"\n   CHECK-IN LOCATION:")
    print(f"   ├─ Latitude: {record['checkin_latitude']}")
    print(f"   ├─ Longitude: {record['checkin_longitude']}")
    print(f"   ├─ City: {record['city']}")
    print(f"   └─ Full Address: {record['full_address']}")
    print(f"\n   CHECK-OUT LOCATION:")
    print(f"   ├─ Latitude: {record['checkout_latitude']}")
    print(f"   ├─ Longitude: {record['checkout_longitude']}")
    print(f"   ├─ City: {record['checkout_city']}")
    print(f"   └─ Full Address: {record['checkout_full_address']}")
    print(f"\n   Status: {record['status']}")
    print("-" * 80)

conn.close()

print("\n✅ Database check complete!")
print("\n💡 Tips:")
print("   - If lat/lon show as 'None' or '0.0', location wasn't captured")
print("   - If city shows 'Vellore' but coordinates are correct, it's a geocoding issue")
print("   - If coordinates show Vellore area (12.9-13.2°N, 78.9-79.3°E), GPS is pointing there")
print("   - Avadi coordinates should be around: 13.11°N, 80.10°E")