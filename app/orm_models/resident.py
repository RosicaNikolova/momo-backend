from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database_config import Base


class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # optional, for anonymized data
    room_number = Column(String, nullable=True)

    # new line: connect to InBedDaily table
    inbed_records = relationship("InBedDaily", back_populates="resident")
