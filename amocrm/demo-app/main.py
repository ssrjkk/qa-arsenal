"""FastAPI Demo Application for amoCRM."""

import os
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
import psycopg2
from psycopg2.extras import RealDictCursor

from core.config import get_settings


settings = get_settings()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "amocrm"),
    "user": os.getenv("DB_USER", "user"),
    "password": os.getenv("DB_PASSWORD", "pass"),
}


in_memory_contacts = {}
in_memory_companies = {}
in_memory_deals = {}
contact_id_counter = 1
company_id_counter = 1
deal_id_counter = 1


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            company_id INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            website VARCHAR(255),
            phone VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price DECIMAL(12,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            contact_id INTEGER,
            company_id INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    init_db()
    yield


app = FastAPI(
    title="amoCRM API",
    description="Demo API for amoCRM testing framework",
    version="1.0.0",
    lifespan=lifespan,
)


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_id: Optional[int] = None


class ContactResponse(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1)
    website: Optional[str] = None
    phone: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None


class DealCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    contact_id: Optional[int] = None
    company_id: Optional[int] = None


class DealResponse(BaseModel):
    id: int
    name: str
    price: float
    status: str = "pending"
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/contacts")
def get_contacts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    query: Optional[str] = None,
):
    """Get contacts list."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if query:
            cur.execute(
                "SELECT * FROM contacts WHERE name LIKE %s OR email LIKE %s ORDER BY id LIMIT %s OFFSET %s",
                (f"%{query}%", f"%{query}%", per_page, (page - 1) * per_page),
            )
        else:
            cur.execute(
                "SELECT * FROM contacts ORDER BY id LIMIT %s OFFSET %s",
                (per_page, (page - 1) * per_page),
            )

        contacts = cur.fetchall()
        cur.close()
        conn.close()
        return {"contacts": [dict(c) for c in contacts]}
    except Exception:
        if query:
            contacts = [c for c in in_memory_contacts.values() if query.lower() in c["name"].lower()]
        else:
            contacts = list(in_memory_contacts.values())
        return {"contacts": contacts}


@app.post("/api/contacts", status_code=201)
def create_contact(contact: ContactCreate):
    """Create new contact."""
    global contact_id_counter

    contact_data = contact.model_dump()
    contact_data["id"] = contact_id_counter
    contact_data["created_at"] = datetime.utcnow().isoformat()

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contacts (name, email, phone, company_id) VALUES (%s, %s, %s, %s) RETURNING id",
            (contact.name, contact.email, contact.phone, contact.company_id),
        )
        contact_data["id"] = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        in_memory_contacts[contact_id_counter] = contact_data
        contact_id_counter += 1

    return {"contact": contact_data}


@app.get("/api/contacts/{contact_id}")
def get_contact(contact_id: int):
    """Get contact by ID."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cur.fetchone()
        cur.close()
        conn.close()

        if contact:
            return {"contact": dict(contact)}
        raise HTTPException(status_code=404, detail="Contact not found")
    except HTTPException:
        raise
    except Exception:
        contact = in_memory_contacts.get(contact_id)
        if contact:
            return {"contact": contact}
        raise HTTPException(status_code=404, detail="Contact not found")


@app.put("/api/contacts/{contact_id}")
def update_contact(contact_id: int, contact: ContactCreate):
    """Update contact."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        updates = []
        values = []
        if contact.name:
            updates.append("name = %s")
            values.append(contact.name)
        if contact.email:
            updates.append("email = %s")
            values.append(contact.email)
        if contact.phone:
            updates.append("phone = %s")
            values.append(contact.phone)
        if contact.company_id:
            updates.append("company_id = %s")
            values.append(contact.company_id)

        if updates:
            values.append(contact_id)
            cur.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE id = %s", values)
            conn.commit()

        cur.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        updated = cur.fetchone()
        cur.close()
        conn.close()

        if updated:
            return {"contact": dict(updated)}
        raise HTTPException(status_code=404, detail="Contact not found")
    except HTTPException:
        raise
    except Exception:
        if contact_id in in_memory_contacts:
            in_memory_contacts[contact_id].update(contact.model_dump(exclude_unset=True))
            return {"contact": in_memory_contacts[contact_id]}
        raise HTTPException(status_code=404, detail="Contact not found")


@app.delete("/api/contacts/{contact_id}")
def delete_contact(contact_id: int):
    """Delete contact."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
        conn.commit()
        deleted = cur.rowcount > 0
        cur.close()
        conn.close()

        if deleted:
            return {"deleted": True}
        raise HTTPException(status_code=404, detail="Contact not found")
    except HTTPException:
        raise
    except Exception:
        if contact_id in in_memory_contacts:
            del in_memory_contacts[contact_id]
            return {"deleted": True}
        raise HTTPException(status_code=404, detail="Contact not found")


@app.get("/api/companies")
def get_companies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    query: Optional[str] = None,
):
    """Get companies list."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if query:
            cur.execute(
                "SELECT * FROM companies WHERE name LIKE %s OR website LIKE %s ORDER BY id LIMIT %s OFFSET %s",
                (f"%{query}%", f"%{query}%", per_page, (page - 1) * per_page),
            )
        else:
            cur.execute(
                "SELECT * FROM companies ORDER BY id LIMIT %s OFFSET %s",
                (per_page, (page - 1) * per_page),
            )

        companies = cur.fetchall()
        cur.close()
        conn.close()
        return {"companies": [dict(c) for c in companies]}
    except Exception:
        if query:
            companies = [c for c in in_memory_companies.values() if query.lower() in c["name"].lower()]
        else:
            companies = list(in_memory_companies.values())
        return {"companies": companies}


@app.post("/api/companies", status_code=201)
def create_company(company: CompanyCreate):
    """Create new company."""
    global company_id_counter

    company_data = company.model_dump()
    company_data["id"] = company_id_counter
    company_data["created_at"] = datetime.utcnow().isoformat()

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO companies (name, website, phone) VALUES (%s, %s, %s) RETURNING id",
            (company.name, company.website, company.phone),
        )
        company_data["id"] = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        in_memory_companies[company_id_counter] = company_data
        company_id_counter += 1

    return {"company": company_data}


@app.get("/api/companies/{company_id}")
def get_company(company_id: int):
    """Get company by ID."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
        company = cur.fetchone()
        cur.close()
        conn.close()

        if company:
            return {"company": dict(company)}
        raise HTTPException(status_code=404, detail="Company not found")
    except HTTPException:
        raise
    except Exception:
        company = in_memory_companies.get(company_id)
        if company:
            return {"company": company}
        raise HTTPException(status_code=404, detail="Company not found")


@app.put("/api/companies/{company_id}")
def update_company(company_id: int, company: CompanyCreate):
    """Update company."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        updates = []
        values = []
        if company.name:
            updates.append("name = %s")
            values.append(company.name)
        if company.website:
            updates.append("website = %s")
            values.append(company.website)
        if company.phone:
            updates.append("phone = %s")
            values.append(company.phone)

        if updates:
            values.append(company_id)
            cur.execute(f"UPDATE companies SET {', '.join(updates)} WHERE id = %s", values)
            conn.commit()

        cur.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
        updated = cur.fetchone()
        cur.close()
        conn.close()

        if updated:
            return {"company": dict(updated)}
        raise HTTPException(status_code=404, detail="Company not found")
    except HTTPException:
        raise
    except Exception:
        if company_id in in_memory_companies:
            in_memory_companies[company_id].update(company.model_dump(exclude_unset=True))
            return {"company": in_memory_companies[company_id]}
        raise HTTPException(status_code=404, detail="Company not found")


@app.delete("/api/companies/{company_id}")
def delete_company(company_id: int):
    """Delete company."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM companies WHERE id = %s", (company_id,))
        conn.commit()
        deleted = cur.rowcount > 0
        cur.close()
        conn.close()

        if deleted:
            return {"deleted": True}
        raise HTTPException(status_code=404, detail="Company not found")
    except HTTPException:
        raise
    except Exception:
        if company_id in in_memory_companies:
            del in_memory_companies[company_id]
            return {"deleted": True}
        raise HTTPException(status_code=404, detail="Company not found")


@app.get("/api/deals")
def get_deals(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
):
    """Get deals list."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if status:
            cur.execute(
                "SELECT * FROM deals WHERE status = %s ORDER BY id LIMIT %s OFFSET %s",
                (status, per_page, (page - 1) * per_page),
            )
        else:
            cur.execute(
                "SELECT * FROM deals ORDER BY id LIMIT %s OFFSET %s",
                (per_page, (page - 1) * per_page),
            )

        deals = cur.fetchall()
        cur.close()
        conn.close()
        return {"deals": [dict(d) for d in deals]}
    except Exception:
        if status:
            deals = [d for d in in_memory_deals.values() if d["status"] == status]
        else:
            deals = list(in_memory_deals.values())
        return {"deals": deals}


@app.post("/api/deals", status_code=201)
def create_deal(deal: DealCreate):
    """Create new deal."""
    global deal_id_counter

    deal_data = deal.model_dump()
    deal_data["id"] = deal_id_counter
    deal_data["status"] = "pending"
    deal_data["created_at"] = datetime.utcnow().isoformat()

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO deals (name, price, status, contact_id, company_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (deal.name, deal.price, "pending", deal.contact_id, deal.company_id),
        )
        deal_data["id"] = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        in_memory_deals[deal_id_counter] = deal_data
        deal_id_counter += 1

    return {"deal": deal_data}


@app.get("/api/deals/{deal_id}")
def get_deal(deal_id: int):
    """Get deal by ID."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM deals WHERE id = %s", (deal_id,))
        deal = cur.fetchone()
        cur.close()
        conn.close()

        if deal:
            return {"deal": dict(deal)}
        raise HTTPException(status_code=404, detail="Deal not found")
    except HTTPException:
        raise
    except Exception:
        deal = in_memory_deals.get(deal_id)
        if deal:
            return {"deal": deal}
        raise HTTPException(status_code=404, detail="Deal not found")


@app.put("/api/deals/{deal_id}")
def update_deal(deal_id: int, deal: DealCreate):
    """Update deal."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        updates = []
        values = []
        if deal.name:
            updates.append("name = %s")
            values.append(deal.name)
        if deal.price is not None:
            updates.append("price = %s")
            values.append(deal.price)
        if deal.contact_id:
            updates.append("contact_id = %s")
            values.append(deal.contact_id)
        if deal.company_id:
            updates.append("company_id = %s")
            values.append(deal.company_id)

        if updates:
            values.append(deal_id)
            cur.execute(f"UPDATE deals SET {', '.join(updates)} WHERE id = %s", values)
            conn.commit()

        cur.execute("SELECT * FROM deals WHERE id = %s", (deal_id,))
        updated = cur.fetchone()
        cur.close()
        conn.close()

        if updated:
            return {"deal": dict(updated)}
        raise HTTPException(status_code=404, detail="Deal not found")
    except HTTPException:
        raise
    except Exception:
        if deal_id in in_memory_deals:
            in_memory_deals[deal_id].update(deal.model_dump(exclude_unset=True))
            return {"deal": in_memory_deals[deal_id]}
        raise HTTPException(status_code=404, detail="Deal not found")


@app.delete("/api/deals/{deal_id}")
def delete_deal(deal_id: int):
    """Delete deal."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM deals WHERE id = %s", (deal_id,))
        conn.commit()
        deleted = cur.rowcount > 0
        cur.close()
        conn.close()

        if deleted:
            return {"deleted": True}
        raise HTTPException(status_code=404, detail="Deal not found")
    except HTTPException:
        raise
    except Exception:
        if deal_id in in_memory_deals:
            del in_memory_deals[deal_id]
            return {"deleted": True}
        raise HTTPException(status_code=404, detail="Deal not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
