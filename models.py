from sqlalchemy import Column, Integer, String
from database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    department_name = Column(
        String(100),
        unique=True,
        nullable=False
    )


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    employee_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    department = Column(String(100), nullable=False)
    basic_salary = Column(Integer, default=0)
    housing = Column(Integer, default=0)
    transport = Column(Integer, default=0)
    total_salary = Column(Integer, default=0)


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    employee_number = Column(
        String(50),
        nullable=False
    )

    department = Column(
        String(100),
        nullable=False
    )

    month = Column(
        String(20),
        nullable=False
    )

    basic_salary = Column(Integer, default=0)
    housing = Column(Integer, default=0)
    transport = Column(Integer, default=0)
    discount = Column(Integer, default=0)
    advance = Column(Integer, default=0)
    total_salary = Column(Integer, default=0)
    net_salary = Column(Integer, default=0)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    department_id = Column(Integer)


class TransferRequest(Base):
    __tablename__ = "transfer_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False)
    from_department_id = Column(Integer, nullable=False)
    to_department_id = Column(Integer, nullable=False)
    requested_by = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")