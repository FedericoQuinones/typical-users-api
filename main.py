from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import class_row

from db import pool
from models import User, UserCreate, UserUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open()
    yield
    await pool.close()


app = FastAPI(title="Users API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.0.50:8000", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    async with pool.connection() as conn:
        await conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/users", response_model=list[User])
async def list_users(limit: int = 100, offset: int = 0):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=class_row(User)) as cur:
            await cur.execute(
                "SELECT id, name, email, age, created "
                "FROM users ORDER BY id LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return await cur.fetchall()


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=class_row(User)) as cur:
            await cur.execute(
                "SELECT id, name, email, age, created "
                "FROM users WHERE id = %s",
                (user_id,),
            )
            user = await cur.fetchone()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=User, status_code=201)
async def create_user(data: UserCreate):
    try:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=class_row(User)) as cur:
                await cur.execute(
                    "INSERT INTO users (name, email, age) "
                    "VALUES (%s, %s, %s) "
                    "RETURNING id, name, email, age, created",
                    (data.name, data.email, data.age),
                )
                return await cur.fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Email is already registered")


@app.patch("/users/{user_id}", response_model=User)
async def update_user(user_id: int, data: UserUpdate):
    fields = data.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join(f"{col} = %s" for col in fields)
    values = list(fields.values()) + [user_id]
    try:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=class_row(User)) as cur:
                await cur.execute(
                    f"UPDATE users SET {set_clause} WHERE id = %s "
                    "RETURNING id, name, email, age, created",
                    values,
                )
                user = await cur.fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Email is already registered")
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    async with pool.connection() as conn:
        cur = await conn.execute("DELETE FROM users WHERE id = %s", (user_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
