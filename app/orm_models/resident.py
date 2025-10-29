from sqlalchemy import Column, Integer, String, Date
from ..database_config import Base
from sqlalchemy.orm import relationship


class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # optional, for anonymized data
    room_number = Column(String, nullable=True)

    # new line: connect to InBedDaily table
    inbed_records = relationship("InBedDaily", back_populates="resident")
