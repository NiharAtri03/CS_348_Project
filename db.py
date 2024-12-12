from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, isolation_level="SERIALIZABLE")
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(DateTime)
    time = Column(String)
    venue_name = Column(String)
    total_tickets = Column(Integer)
    price = Column(Float)
    event_type = Column(String)

    __table_args__ = (
        Index('idx_event_id', 'id'),
        Index('idx_event_total_tickets', 'total_tickets'),
        Index("ix_events_date", date)
    )

    tickets = relationship("Ticket", back_populates="event")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    num_tickets = Column(Integer)

    event = relationship("Event", back_populates="tickets")


Base.metadata.create_all(bind=engine)
