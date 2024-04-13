# main.py
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from sqlalchemy.orm import Session
from models import Account, Base, Destination
from database import SessionLocal, engine
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Annotated
import json
import requests

app = FastAPI()

# Create all tables defined in your models
Base.metadata.create_all(bind=engine)


class AccountCreate(BaseModel):
    email: str
    account_name: str
    account_id: str
    app_secret_token: str
    website: str = None


class AccountDB(BaseModel):
    id: int
    email: str
    account_name: str
    account_id: str
    app_secret_token: str
    website: str


class DestinationCreate(BaseModel):
    url: str
    http_method: str
    headers: Dict[str, str]


class DestinationDB(BaseModel):
    id: int
    account_id: int
    url: str
    http_method: str
    headers: Dict[str, str]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/accounts/")
def create_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    try:
        account = Account(**account_data.dict())
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/{account_id}", response_model=AccountDB)
def read_account(account_id: int, db: Session = Depends(get_db)):
    db_account = db.query(Account).get(account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    print(db_account)
    return AccountDB(**db_account.__dict__)


@app.put("/accounts/{account_id}", response_model=AccountDB)
def update_account(
    account_id: int, account_data: AccountCreate, db: Session = Depends(get_db)
):
    try:
        db_account = db.query(Account).get(account_id)
        if db_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        for key, value in account_data.dict().items():
            setattr(db_account, key, value)
        db.commit()
        db.refresh(db_account)
        return AccountDB(**db_account.__dict__)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


# Delete Account
@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    try:
        db_account = db.query(Account).get(account_id)
        if db_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        db.delete(db_account)
        db.commit()
        return {"message": "Account deleted successfully"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/accounts/{account_id}/destinations/", response_model=DestinationDB)
def create_destination_for_account(
    account_id: int, destination_data: DestinationCreate, db: Session = Depends(get_db)
):
    try:
        db_account = db.query(Account).get(account_id)
        if db_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        print(destination_data.dict())
        db_destination = Destination(**destination_data.dict(), account_id=account_id)
        db.add(db_destination)
        db.commit()
        db.refresh(db_destination)
        return DestinationDB(**db_destination.__dict__)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/accounts/{account_id}/destinations/", response_model=List[DestinationDB])
def read_all_destinations(account_id: int, db: Session = Depends(get_db)):
    try:
        db_destinations = (
            db.query(Destination).filter(Destination.account_id == account_id).all()
        )
        if not db_destinations:
            raise HTTPException(
                status_code=404, detail="No destinations found for this account"
            )
        return [
            DestinationDB(**db_destination.__dict__)
            for db_destination in db_destinations
        ]

    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


# Read Destination
@app.get(
    "/accounts/{account_id}/destinations/{destination_id}", response_model=DestinationDB
)
def read_destination(
    account_id: int, destination_id: int, db: Session = Depends(get_db)
):
    try:
        db_destination = (
            db.query(Destination)
            .filter(
                Destination.id == destination_id, Destination.account_id == account_id
            )
            .first()
        )
        if db_destination is None:
            raise HTTPException(status_code=404, detail="Destination not found")
        return DestinationDB(**db_destination.__dict__)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


# Update Destination
@app.put(
    "/accounts/{account_id}/destinations/{destination_id}", response_model=DestinationDB
)
def update_destination(
    account_id: int,
    destination_id: int,
    destination_data: DestinationCreate,
    db: Session = Depends(get_db),
):
    try:
        db_destination = (
            db.query(Destination)
            .filter(
                Destination.id == destination_id, Destination.account_id == account_id
            )
            .first()
        )
        if db_destination is None:
            raise HTTPException(status_code=404, detail="Destination not found")
        for key, value in destination_data.dict().items():
            setattr(db_destination, key, value)
        db.commit()
        db.refresh(db_destination)
        return DestinationDB(**db_destination.__dict__)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


# Delete Destination
@app.delete("/accounts/{account_id}/destinations/{destination_id}")
def delete_destination(
    account_id: int, destination_id: int, db: Session = Depends(get_db)
):
    try:
        db_destination = (
            db.query(Destination)
            .filter(
                Destination.id == destination_id, Destination.account_id == account_id
            )
            .first()
        )
        if db_destination is None:
            raise HTTPException(status_code=404, detail="Destination not found")
        db.delete(db_destination)
        db.commit()
        return {"message": "Destination deleted successfully"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


class IncomingData(BaseModel):
    data: Dict[str, Any]


# API endpoint to receive data
@app.post("/server/incoming_data")
def receive_data(
    request: Request,
    incoming_data: IncomingData,
    token: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
):

    try:
        if token is None:
            raise HTTPException(status_code=401, detail="Unauthenticated")

        # Query the database to find the account by token
        account = db.query(Account).filter(Account.app_secret_token == token).first()
        if account is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Query the database to find destinations for the account
        account_destinations = (
            db.query(Destination).filter(Destination.account_id == account.id).all()
        )

        if not account_destinations:
            raise HTTPException(
                status_code=404, detail="No destinations found for this account"
            )

        # Check if the request method is GET and the data is JSON
        if incoming_data.data is None:
            raise HTTPException(status_code=400, detail="Invalid Data")
        data = incoming_data.data
        for destination in account_destinations:
            if destination.http_method.lower() == "get":
                requests.get(destination.url, params=data, headers=destination.headers)
            elif destination.http_method.lower() == "post":
                requests.post(destination.url, data=data, headers=destination.headers)
        return {"message": "Data received and sent to destinations successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
