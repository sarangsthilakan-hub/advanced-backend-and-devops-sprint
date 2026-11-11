from datetime import date

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

import functions

app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=["http://localhost:5173"],
                   allow_methods=["*"],
                   allow_headers=["*"])

@app.post("/packages")
def add_package(package_name, package_destination, package_weight, package_arrival_date: date, package_status="dispatching"): #E3
    response = functions.register_a_package(package_name=package_name,package_destination=package_destination,package_weight=package_weight,package_arrival_date=package_arrival_date,package_status=package_status)
    code = response["code"]
    if code == 200:
        return response["package"]
    raise HTTPException(code,detail=response["msg"])
@app.get("/packages")
def get_package(package_id):
    response = functions.get_a_package(package_id=package_id)
    code = response["code"]
    if code == 200:
        return response["package"]
    raise HTTPException(code, detail=response["msg"])
