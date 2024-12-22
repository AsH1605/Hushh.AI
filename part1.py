from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
import logging
from typing import List, Optional
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class User(BaseModel):
    name: str
    email: EmailStr

class Order(BaseModel):
    user_id: int
    product_name: str
    quantity: int

async def handle_database_error(error: Exception):
    logger.error(f"Database error: {str(error)}")
    if "duplicate key value violates unique constraint" in str(error):
        raise HTTPException(status_code=400, detail="Email already exists.")
    if "foreign key violation" in str(error):
        raise HTTPException(status_code=400, detail="Invalid user ID.")
    raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/users/", response_model=User)
async def create_user(user: User):
    logger.debug(f"Creating user: {user}")
    try:
        response = supabase.table("users").insert({"name": user.name, "email": user.email}).execute()
        logger.debug(f"Supabase response: {response}")
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create user.")
        return response.data[0]
    except Exception as e:
        await handle_database_error(e)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    logger.debug(f"Fetching user with ID: {user_id}")
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        logger.debug(f"Supabase response: {response}")
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        await handle_database_error(e)

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    logger.debug(f"Updating user with ID: {user_id} - Data: {user}")
    try:
        response = supabase.table("users").update({"name": user.name, "email": user.email}).eq("id", user_id).execute()
        logger.debug(f"Supabase response: {response}")
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        await handle_database_error(e)

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    logger.debug(f"Deleting user with ID: {user_id}")
    try:
        response = supabase.table("users").delete().eq("id", user_id).execute()
        logger.debug(f"Supabase response: {response}")
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deleted successfully"}
    except Exception as e:
        await handle_database_error(e)

@app.post("/orders/", response_model=Order)
async def create_order(order: Order):
    logger.debug(f"Creating order: {order}")
    try:
        response = supabase.table("orders").insert({
            "user_id": order.user_id,
            "product_name": order.product_name,
            "quantity": order.quantity
        }).execute()
        logger.debug(f"Supabase response: {response}")
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create order.")
        return response.data[0]
    except Exception as e:
        await handle_database_error(e)

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    logger.debug(f"Fetching order with ID: {order_id}")
    try:
        response = supabase.table("orders").select("*").eq("id", order_id).execute()
        logger.debug(f"Supabase response: {response}")
        if not response.data:
            raise HTTPException(status_code=404, detail="Order not found")
        return response.data[0]
    except Exception as e:
        await handle_database_error(e)

@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, order: Order):
    logger.debug(f"Updating order with ID: {order_id} - Data: {order}")
    try:
        response = supabase.table("orders").update({
            "product_name": order.product_name,
            "quantity": order.quantity
        }).eq("id", order_id).execute()
        logger.debug(f"Supabase response: {response}")
        if not response.data:
            raise HTTPException(status_code=404, detail="Order not found")
        return response.data[0]
    except Exception as e:
        await handle_database_error(e)

@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    logger.debug(f"Deleting order with ID: {order_id}")
    try:
        response = supabase.table("orders").delete().eq("id", order_id).execute()
        logger.debug(f"Supabase response: {response}")
        if not response.data:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"detail": "Order deleted successfully"}
    except Exception as e:
        await handle_database_error(e)
