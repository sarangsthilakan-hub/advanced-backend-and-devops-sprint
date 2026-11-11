from sqlalchemy import Integer, String,Float, Column, create_engine, DateTime, ForeignKey, func, Date
from sqlalchemy.orm import Session, declarative_base, session
from datetime import datetime, date, timedelta


DB_PATH = "./warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()


class Dispatches(Base):
    __tablename__ = "Dispatches"
    dispatch_batch_id = Column(Integer,primary_key=True)
    dispatch_destination = Column(String)
    dispatch_vehicle = Column(String)
    dispatch_status = Column(String)
    dispatch_date = Column(Date, nullable =True)

class Packages(Base):
    __tablename__ = "Packages"
    package_id = Column(Integer, primary_key=True)
    package_name = Column(String)
    package_destination = Column(String)
    package_weight = Column(Float)
    package_arrival_date = Column(Date)
    package_status = Column(String)
    package_batch_id = Column(Integer,ForeignKey("Dispatches.dispatch_batch_id"), nullable=True)

Base.metadata.create_all(engine)


def register_a_package(package_name,package_destination,package_weight,package_arrival_date,package_status="pending_dispatch"):
    session = Session(engine)
    statuses = ["dispatching","pending_dispatch"]
    status = package_status
    if status is not None:
        status = status.lower()
    if status not in statuses:
        session.close()
        return {"code": 422, "msg": "Invalid Status"}
    if package_name and package_destination and package_weight and package_arrival_date and package_status:
        package = Packages(package_name=package_name, package_destination=package_destination,
                           package_weight=package_weight, package_arrival_date=package_arrival_date,
                           package_status=package_status)
        session.add(package)
        response = {
            "package_name": package.package_name,
            "package_destination": package.package_destination,
            "package_weight": package.package_weight,
            "package_arrival_date": package.package_arrival_date,
            "package_status": package.package_status
        }
        session.commit()
        session.close()
        return {"code": 200, "package": response}
    else:
        session.close()
        return {"code": 422, "msg": "Missing or Empty field"}

def get_a_package(package_id):
    session = Session(engine)
    package = session.get(Packages, package_id)
    if package is None:
        session.close()
        return {"code": 404, "msg":"Package not Found"}
    response = {
        "package_id":package.package_id,
        "package_name": package.package_name,
        "package_destination": package.package_destination,
        "package_weight": package.package_weight,
        "package_arrival_date": package.package_arrival_date,
        "package_status": package.package_status
    }
    session.close()
    return {"package": response, "code": 200}

def delete_a_package(package_id):
    session = Session(engine)
    package = session.get(Packages,package_id)

    if package is None:
        session.close()
        return {"code": 404, "msg":"Package not Found"}

    if package.package_status and package.package_status.lower() == "dispatched":
        session.close()
        return {"code":422 ,"msg":"Package already dispatched"}

    session.delete(package)
    session.commit()
    session.close()
    return {"code":200, "package":"Package Deleted Successfully"}


def all_package_filter(package_destination=None,package_status=None,package_arrival_date=None):
    session = Session(engine)
    packages = session.query(Packages)
    if package_destination:
        packages = packages.filter(Packages.package_destination == package_destination)
    if package_status:
        packages = packages.filter(Packages.package_status == package_status)
    if package_arrival_date:
        packages = packages.filter(Packages.package_arrival_date == package_arrival_date)

    packages = packages.all()

    response = []
    for package in packages:
        response.append({
            "package_id": package.package_id,
            "package_name": package.package_name,
            "package_destination": package.package_destination,
            "package_weight": package.package_weight,
            "package_arrival_date": package.package_arrival_date,
            "package_status": package.package_status
        })
        session.close()
    return response




