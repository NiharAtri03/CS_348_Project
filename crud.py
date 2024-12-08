from sqlalchemy.orm import Session
from sqlalchemy import text
from db import Event, Ticket, Base, engine
from datetime import datetime

def create_event(db: Session, name: str, date: datetime, time: str, venue_name: str, total_tickets: int, price: float, event_type: str):
    try:
        event = Event(
            name=name,
            date=date,
            time=time,
            venue_name=venue_name,
            total_tickets=total_tickets,
            price=price,
            event_type=event_type
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        db.rollback()
        raise e

def delete_event(db: Session, event_id: int):
    try:
        delete_query = text("DELETE FROM events WHERE id = :event_id")
        db.execute(delete_query, {"event_id": event_id})
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def get_all_events(db: Session):
    try:
        return db.query(Event).all()
    except Exception as e:
        db.rollback()
        raise e

def reset_database():
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise e

def buy_ticket(db: Session, event_id: int, num_tickets: int):
    try:
        event = db.query(Event).filter(Event.id == event_id).first()

        if not event or event.total_tickets <= 0:
            return None

        ticket = Ticket(event_id=event_id, num_tickets=num_tickets)
        db.add(ticket)

        event.total_tickets -= num_tickets
        db.commit()
        db.refresh(ticket)

        return ticket
    except Exception as e:
        db.rollback()
        raise e

def get_available_events(db: Session):
    try:
        sql = text("""
            SELECT e.id, e.name, e.date, e.time, e.venue_name, e.total_tickets, e.price, e.event_type
            FROM events e
            WHERE e.total_tickets > 0
        """)

        result = db.execute(sql)
        events = []

        for row in result:
            event = Event(
                id=row[0],
                name=row[1],
                date=row[2],
                time=row[3],
                venue_name=row[4],
                total_tickets=row[5],
                price=row[6],
                event_type=row[7]
            )
            events.append(event)

        return events
    except Exception as e:
        db.rollback()
        raise e

def update_event(db: Session, event_id: int, name: str, date: datetime, time: str,
                venue_name: str, total_tickets: int, price: float, event_type: str):
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            event.name = name
            event.date = date
            event.time = time
            event.venue_name = venue_name
            event.total_tickets = total_tickets
            event.price = price
            event.event_type = event_type
            db.commit()
            db.refresh(event)
        return event
    except Exception as e:
        db.rollback()
        raise e
