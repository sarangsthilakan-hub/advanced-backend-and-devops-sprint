from email.policy import default

from sqlalchemy import Integer, String,Float, Column, create_engine, DateTime, ForeignKey, func, Date
from sqlalchemy.orm import Session, declarative_base, session
from datetime import datetime, date, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


ph = PasswordHasher()


DB_PATH = "./warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")


USERNAME = "Sarang"

PASSWORD = "Sarang8083"
ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY ="SECRET123"
ALGORITHM = "HS256"


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

class Users(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    user_type = Column(String, default = "user")

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

def partial_package_update(package_id,package_name= None, package_destination=None,package_arrival_date=None,package_status=None,package_batch_id=None):
    session = Session(engine)
    package = session.get(Packages,package_id)

    if package is None:
        session.close()
        return {"code": 404, "msg":"Package not Found"}
    if package_name is not None:
        package.package_name = package_name
    if package_destination is not None:
        package.package_destination = package_destination
    if package_arrival_date is not None:
        package.package_arrival_date = package_arrival_date
    if package_status is not None:
        status = package_status.lower()
        valid_statuses = ["received", "ready", "dispatched"]
        if status not in valid_statuses:
            session.close()
            return {"code": 422, "msg": "Invalid Status"}
        package.package_status = status
    if package_batch_id is not None:
        package.package_batch_id = package_batch_id

    session.commit()
    response = {
        "package_id": package.package_id,
        "package_name": package.package_name,
        "package_destination": package.package_destination,
        "package_weight": package.package_weight,
        "package_arrival_date": package.package_arrival_date,
        "package_status": package.package_status,
        "package_batch_id": package.package_batch_id
    }
    session.close()
    return {"code": 200, "package": response}

def verify_login(username, password):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name = username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password,password)
    except VerifyMismatchError:
        session.close()
        return False
    if user.user_type:
        user_type = user.user_type
    else:
        user_type = "user"
    session.close()
    access_token = create_token(username=username, token_type="access",user_type=user_type)
    refresh_token = create_token(username=username, token_type="refresh",user_type=user_type)
    return {"access_token": access_token, "refresh_token": refresh_token}

def create_token(username, token_type,user_type="user"):
    payload = {
        "username": username,
        'token_type': token_type,
        'user_type': user_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRY if token_type == "access" else REFRESH_TOKEN_EXPIRY)  # turnery expression
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token



def verify_token(token,token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return False
    if payload["token_type"] == token_type:
        return payload
    return False


def create_dispatch_batch(dispatch_destination, dispatch_vehicle, dispatch_status="dispatching", dispatch_date=None,
                          package_id=None):
    session = Session(engine)

    batch = Dispatches(
        dispatch_destination=dispatch_destination,
        dispatch_vehicle=dispatch_vehicle,
        dispatch_status=dispatch_status,
        dispatch_date=dispatch_date
    )
    session.add(batch)
    session.commit()

    if package_id is not None:
        package = session.get(Packages, package_id)
        if package:
            package.package_batch_id = batch.dispatch_batch_id
            package.package_status = "dispatched"
            session.commit()

    response = {
        "dispatch_batch_id": batch.dispatch_batch_id,
        "dispatch_destination": batch.dispatch_destination,
        "dispatch_vehicle": batch.dispatch_vehicle,
        "dispatch_status": batch.dispatch_status,
        "dispatch_date": batch.dispatch_date,
        "package_id": package_id
    }
    session.close()
    return {"code": 200, "batch": response}


def get_dispatch_batches(dispatch_destination=None, dispatch_vehicle=None, dispatch_status=None):
    session = Session(engine)
    batches = session.query(Dispatches)

    if dispatch_destination:
        batches = batches.filter(Dispatches.dispatch_destination == dispatch_destination)
    if dispatch_vehicle:
        batches = batches.filter(Dispatches.dispatch_vehicle == dispatch_vehicle)
    if dispatch_status:
        batches = batches.filter(Dispatches.dispatch_status == dispatch_status)

    batches = batches.all()
    response = []
    for b in batches:
        response.append({
            "dispatch_batch_id": b.dispatch_batch_id,
            "dispatch_destination": b.dispatch_destination,
            "dispatch_vehicle": b.dispatch_vehicle,
            "dispatch_status": b.dispatch_status,
            "dispatch_date": b.dispatch_date
        })
    session.close()
    return response


def get_warehouse_analytics():
    session = Session(engine)
    packages = session.query(Packages).all()

    total_packages = len(packages)
    pending_dispatch = 0
    dispatched = 0
    destination_summary = {}

    for package in packages:
        status = package.package_status
        if status == "pending_dispatch":
            pending_dispatch += 1
        elif status == "dispatched":
            dispatched += 1

        dest = package.package_destination
        if dest in destination_summary:
            destination_summary[dest] += 1
        else:
            destination_summary[dest] = 1

    session.close()
    return {
        "total_packages_received": total_packages,
        "total_packages_pending": pending_dispatch,
        "total_packages_dispatched": dispatched,
        "destination_wise_count": destination_summary
    }

#--------- Users -----------

def register_user(user_name:str,password:str,user_type:str="user"):
    session = Session(engine)
    user_exists = session.query(Users).filter_by(user_name=user_name).first()
    if user_exists is not None:
        session.close()
        return False
    session.add(Users(user_name=user_name,password=ph.hash(password),user_type=user_type))
    session.commit()
    session.close()
    return True


