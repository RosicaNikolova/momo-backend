import pandas as pd
from sqlalchemy.orm import Session

from app.database_config import SessionLocal
from app.orm_models.inbed_daily import InBedDaily

# Paths to your CSV files (adjust names if needed)
FILE_TIME_IN_BED = "app/data/timeinbed.csv"
FILE_ACTIVITY_IN_BED = "app/data/activityinbed.csv"
FILE_TIMES_OUT_BED = "app/data/timesoutofbed.csv"

# Insert into the database
db: Session = SessionLocal()

# Insert resident
# resident_name = "John Doe"
# room_number = "100"

# new_resident = Resident(name=resident_name, room_number=room_number)
# db.add(new_resident)
# db.commit()
# db.refresh(new_resident)
# resident_id = new_resident.id
# print(f"Created new resident '{resident_name}' with ID {resident_id} ")

# Load all CSVs with correct date parsing
time_in_bed = pd.read_csv(
    FILE_TIME_IN_BED, parse_dates=[0], dayfirst=True, skipinitialspace=True, decimal="."
)
activity = pd.read_csv(
    FILE_ACTIVITY_IN_BED,
    parse_dates=[0],
    dayfirst=True,
    skipinitialspace=True,
    decimal=".",
)
times_out = pd.read_csv(FILE_TIMES_OUT_BED, parse_dates=[0], dayfirst=True)

# Rename columns after reading
time_in_bed.columns = ["date", "time_in_bed"]
activity.columns = ["date", "at_rest", "low_activity", "high_activity"]
times_out.columns = ["date", "times_out_bed_night", "times_out_bed_day"]

# Merge all CSVs on 'date'
merged = time_in_bed.merge(activity, on="date").merge(times_out, on="date")

# Convert date column to datetime
merged["date"] = pd.to_datetime(merged["date"], errors="coerce").dt.date


print(merged.dtypes)
print(merged.head())
print(merged.iloc[0].to_dict())

print("Merged data preview:")
print(merged.head())


for _, row in merged.iterrows():
    record = InBedDaily(
        date=row["date"],
        time_in_bed=row["time_in_bed"],
        at_rest=row["at_rest"],
        low_activity=row["low_activity"],
        high_activity=row["high_activity"],
        times_out_bed_night=row["times_out_bed_night"],
        times_out_bed_day=row["times_out_bed_day"],
        resident_id=1,  # assume this data belongs to resident with ID=1
    )
    db.add(record)

db.commit()
db.close()

print("Data imported successfully into 'inbed_daily' table.")
