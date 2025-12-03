# app/models/inbed_daily.py
from sqlalchemy import Column, Date, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..database_config import Base


class InBedDaily(Base):
    """
    Represents one day's Bedsense data for a resident.
    All time-related values are stored in seconds.
    """

    __tablename__ = "inbed_daily"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    time_in_bed = Column(Float)  # total time in bed (sec)
    at_rest = Column(Float)  # time lying still (sec)
    low_activity = Column(Float)  # small movements (sec)
    # restlessness / large movements (sec)
    high_activity = Column(Float)
    # how many times out of bed during night
    times_out_bed_night = Column(Integer)
    # how many times out of bed during day
    times_out_bed_day = Column(Integer)

    # Link to resident
    resident_id = Column(Integer, ForeignKey("residents.id"))
    resident = relationship("Resident", back_populates="inbed_records")
