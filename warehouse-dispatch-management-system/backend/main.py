from datetime import date
from urllib import response

from fastapi import FastAPI, HTTPException, Body, Header
from fastapi.middleware.cors import CORSMiddleware

import functions

app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=["http://localhost:5173"],
                   allow_methods=["*"],
                   allow_headers=["*"])

@app.post("/packages")
def add_package(package_name, package_destination, package_weight, package_arrival_date: date, package_status="pending_dispatch", token = Header(None)): #E3
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.register_a_package(package_name=package_name,package_destination=package_destination,package_weight=package_weight,package_arrival_date=package_arrival_date,package_status=package_status)
    code = response["code"]
    if code == 200:
        return response["package"]
    raise HTTPException(code,detail=response["msg"])
@app.get("/packages/{package_id}")
def get_package(package_id: int):
    response = functions.get_a_package(package_id=package_id)
    code = response["code"]
    if code == 200:
        return response["package"]
    raise HTTPException(code, detail=response["msg"])

@app.delete("/package/{package_id}")
def delete_package(package_id: int,token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.delete_a_package(package_id=package_id)
    code = response["code"]
    if code == 200:
        return response["package"]
    raise HTTPException(code,detail=response["msg"])

@app.get("/filtered_packages")
def package_filter(package_destination=None,package_status=None,package_arrival_date=None, token = Header(None)):
    return functions.all_package_filter(package_destination=package_destination,package_status=package_status,package_arrival_date=package_arrival_date)

@app.patch("/partial_package_update")
def package_update(package_id,token = Header(None),package_name= None, package_destination=None,package_arrival_date=None,package_status=None,package_batch_id=None):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    response = functions.partial_package_update(package_id=package_id,package_name=package_name,package_destination=package_destination,package_arrival_date=package_arrival_date,package_status=package_status,package_batch_id=package_batch_id)
    code = response["code"]
    if code == 200:
        return response["package"]
    raise HTTPException(code, detail=response["msg"])

@app.post("/login")
def login(username:str,password:str):
    tokens = functions.login(username=username,password=password)
    if tokens is None:
        raise HTTPException(status_code=401,detail="Invalid credentials")
    return tokens

@app.post("/refresh")
def refresh(refresh_token):
    username = functions.verify_token(token=refresh_token,token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token")
    access_token = functions.create_token(username=username,token_type="access")
    return {"access_token":access_token}