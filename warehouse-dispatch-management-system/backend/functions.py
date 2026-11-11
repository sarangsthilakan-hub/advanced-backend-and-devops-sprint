from sqlalchemy import Integer, String,Float, Column, create_engine, DateTime, ForeignKey, func, Date
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, date, timedelta


DB_PATH = "./warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

class Packages(Base):
    __tablename__ = "Packages"
    package_id = Column(Integer, primary_key=True)
    package_name = Column(String)
    package_destination = Column(String)
    package_weight = Column(Float)
    package_arrival_date = Column(Date)
    package_status = Column(Integer)

Base.metadata.create_all(engine)


def register_a_package(package_name,package_destination,package_weight,package_arrival_date,package_status=None):
    session = Session(engine)
    status = package_status.lower()
    statuses = ["dispatching"]

    if status not in statuses:
        session.close()
        return {"code": 422, "msg": "Invalid Status"}
    if package_name and package_destination and package_weight and package_arrival_date and package_status:
        package = Packages(package_name=package_name, package_destination=package_destination,
                           package_weight=package_weight, package_arrival_date=package_arrival_date,
                           package_status=package_status)
        session.add(package)
        response = {
            "package_name": Packages.package_name,
            "package_destination": Packages.package_destination,
            "package_weight": Packages.package_weight,
            "package_arrival_date": Packages.package_arrival_date,
            "package_status": Packages.package_status
        }
        session.commit()
        session.close()
        return {"code": 200, "package": response}
    else:
        session.close()
        return {"code": 422, "msg": "Missing or Empty field"}

