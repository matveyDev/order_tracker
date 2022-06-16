from core.database.db import Base

from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, Date


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, index=True, unique=True, autoincrement=True)
    order_number = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)
    delivery_expected = Column(Date, nullable=False)

    def __repr__(self) -> str:
        return f'<Order {self.id}>'

    def delivery_expired(self) -> bool:
        date_now = datetime.date(datetime.now())
        if date_now > self.delivery_expected:
            return True
        else:
            return False

    def get_values(self) -> list:
        data = [
            self.id,
            self.order_number,
            self.price,
            self.delivery_expected
        ]
        return data
