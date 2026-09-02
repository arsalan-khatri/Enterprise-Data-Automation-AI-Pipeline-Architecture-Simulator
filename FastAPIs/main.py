import os
import sys
import urllib
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- STEP 0: AUTOMATIC DATABASE & TABLES INITIALIZER ---
SERVER_NAME = '.\SQLEXPRESS'
DATABASE_NAME = 'AICustomerSupport'

# 1. Pehle 'master' database se connect kar ke check karein ke target database hai ya nahi
master_params = urllib.parse.quote_plus(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER_NAME};DATABASE=master;Trusted_Connection=yes;")
master_engine = create_engine(f"mssql+pyodbc:///?odbc_connect={master_params}", isolation_level="AUTOCOMMIT")

try:
    with master_engine.connect() as conn:
        db_check = conn.execute(text(f"SELECT name FROM sys.databases WHERE name = '{DATABASE_NAME}'")).fetchone()
        if not db_check:
            conn.execute(text(f"CREATE DATABASE {DATABASE_NAME}"))
            print(f"✅ Database '{DATABASE_NAME}' Successfully Created!")
        else:
            print(f"ℹ️ Database '{DATABASE_NAME}' already exists. Using existing database.")
except Exception as e:
    print(f"⚠️ Database creation check error: {e}")

# --- SQL SERVER DATABASE SETUP ---
params = urllib.parse.quote_plus(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;")
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("✅ SQL Database Connected Successfully!")

# 2. Ab check karein ke zaroori tables bane hain ya nahi, agar nahi toh create kar lo
def init_db_tables():
    with engine.begin() as conn:
        # Table 1: Customers
        conn.execute(text("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='customers' and xtype='U')
            CREATE TABLE customers (
                customer_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                phone_number VARCHAR(20),
                customer_type VARCHAR(50)
            )
        """))

        # Agar customers table pehle se maujood hai (purani DB) to phone_number column add kar do
        conn.execute(text("""
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('customers') AND name = 'phone_number')
            ALTER TABLE customers ADD phone_number VARCHAR(20)
        """))

        # Table 2: Products (purchased_orders inhe FK se reference karta hai, isliye pehle banana zaroori hai)
        conn.execute(text("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='products' and xtype='U')
            CREATE TABLE products (
                product_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(150),
                price FLOAT,
                stock INT DEFAULT 100,
                description VARCHAR(300)
            )
        """))

        # Table 3: Purchased Orders — ab har row ek "order line" hai: product_name, quantity aur
        # us line ka calculated total (order_value = quantity * unit_price) sab isi table mein hai.
        # Ek order (same order_id) ke multiple products ho sakte hain, is liye order_id ab unique nahi,
        # PK ek surrogate order_item_id hai.
        conn.execute(text("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='purchased_orders' and xtype='U')
            CREATE TABLE purchased_orders (
                order_item_id INT IDENTITY(1,1) PRIMARY KEY,
                order_id VARCHAR(50),
                customer_id VARCHAR(50) FOREIGN KEY REFERENCES customers(customer_id),
                product_id VARCHAR(50) FOREIGN KEY REFERENCES products(product_id),
                product_name VARCHAR(150),
                quantity INT,
                unit_price FLOAT,
                order_value FLOAT,
                purchase_date DATETIME DEFAULT GETDATE()
            )
        """))

        # Table 4: Complaint Registry
        # order_id ab purchased_orders mein unique nahi (ek order ke multiple product rows ho sakte hain),
        # isliye yahan FK constraint nahi lagai — order_id sirf reference ke liye plain column hai.
        conn.execute(text("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='complaint_registry' and xtype='U')
            CREATE TABLE complaint_registry (
                ticket_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50) FOREIGN KEY REFERENCES customers(customer_id),
                order_id VARCHAR(50),
                status VARCHAR(50) DEFAULT 'Open',
                intent VARCHAR(100),
                department VARCHAR(100),
                ml_priority VARCHAR(50),
                created_at DATETIME DEFAULT GETDATE()
            )
        """))
        
        # Table 5: Complaint Logs
        conn.execute(text("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='complaint_logs' and xtype='U')
            CREATE TABLE complaint_logs (
                log_id INT IDENTITY(1,1) PRIMARY KEY,
                ticket_id VARCHAR(50) FOREIGN KEY REFERENCES complaint_registry(ticket_id),
                sender VARCHAR(50),
                message TEXT,
                sentiment VARCHAR(50),
                timestamp DATETIME DEFAULT GETDATE()
            )
        """))
    print("✅ All Database Tables Verified & Ready!")


def seed_products():
    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM products")).fetchone()[0]
        if count == 0:
            sample_products = [
                ("P-001", "Wireless Earbuds", 4999.0, 50, "Bluetooth 5.0, 20hr battery"),
                ("P-002", "Smart Watch", 8999.0, 30, "Fitness tracking, AMOLED display"),
                ("P-003", "Phone Stand", 799.0, 100, "Adjustable aluminum stand"),
                ("P-004", "Power Bank 20000mAh", 3499.0, 40, "Fast charging, dual USB"),
                ("P-005", "Bluetooth Speaker", 3999.0, 35, "Portable, waterproof"),
                ("P-006", "USB-C Cable Pack", 599.0, 200, "3-pack, 1m braided cables"),
            ]
            for pid, name, price, stock, desc in sample_products:
                conn.execute(text("""
                    INSERT INTO products (product_id, name, price, stock, description)
                    VALUES (:pid, :name, :price, :stock, :desc)
                """), {"pid": pid, "name": name, "price": price, "stock": stock, "desc": desc})
            print("✅ Sample products seeded!")


# Run table initialization
init_db_tables()
seed_products()
# --- SQL SETUP END ---

# 👇 ABSOLUTE PATH SETUP 👇
current_dir = os.path.dirname(os.path.abspath(__file__))
llm_folder_path = os.path.abspath(os.path.join(current_dir, '..', 'llm'))
sys.path.insert(0, llm_folder_path)

# 👇 PATH ADD HONE KE BAAD IMPORT 👇
from schema_llm_pipeline import analyze_customer_ticket

app = FastAPI(
    title="AI Dynamic Helpdesk System",
    description="Enterprise System with Dynamic DB Lookups",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev ke liye; production mein specific origin daalna
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the Trained ML Model AND Encoders
try:
    ml_model = joblib.load("../ml/saved_models/priority_model.pkl")
    encoders = joblib.load("../ml/saved_models/label_encoders.pkl")
    print("✅ ML Model & Encoders Loaded Successfully!")
except Exception as e:
    ml_model = None
    encoders = None
    print(f"⚠️ Warning: Model or Encoders loading failed. Error: {e}")

# 🚀 SCHEMA: Customer sirf 2 cheezein bhejega, ticket_id optional hai!
class TicketRequest(BaseModel):
    customer_id: str
    message: str             
    ticket_id: Optional[str] = None  

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CheckoutRequest(BaseModel):
    customer_name: str
    customer_email: str
    phone_number: str
    customer_type: Optional[str] = "Regular"
    items: list[CartItem]

@app.post("/predict-ticket")
async def predict_ticket(ticket: TicketRequest):
    
    # 🎲 THE MAGIC: Agar ticket_id nahi aayi, toh khud generate kar lo!
    current_ticket_id = ticket.ticket_id if ticket.ticket_id else f"T-{uuid.uuid4().hex[:6].upper()}"
    
    db = SessionLocal()
    try:
        # 🛑 THE GATEKEEPER 1: Check karein customer mojood hai ya nahi!
        check_customer_query = text("SELECT customer_id FROM customers WHERE customer_id = :cid")
        customer_exists = db.execute(check_customer_query, {"cid": ticket.customer_id}).fetchone()
        
        if not customer_exists:
            return {
                "status": "error",
                "message": f"Warning: Customer ID '{ticket.customer_id}' database mein majood nahi hai. Sirf registered customers ticket raise kar sakte hain!"
            }

        # 🛡️ THE GATEKEEPER 2: Duplicate Message Checker (Spam Prevention)
        check_duplicate_query = text("""
            SELECT TOP 1 cl.ticket_id 
            FROM complaint_logs cl
            JOIN complaint_registry cr ON cl.ticket_id = cr.ticket_id
            WHERE cr.customer_id = :cid AND CAST(cl.message AS NVARCHAR(MAX)) = :msg
        """)
        duplicate_exists = db.execute(check_duplicate_query, {
            "cid": ticket.customer_id, 
            "msg": ticket.message
        }).fetchone()
        
        if duplicate_exists:
            return {
                "status": "warning",
                "message": "Aapki yeh complaint pehle hi register ho chuki hai. Hum jald hi aapse raabta karenge!",
                "existing_ticket_id": duplicate_exists[0]
            }

        # ----------------------------------------------------
        # 🔍 STEP 1: DYNAMIC DATABASE LOOKUP
        # ----------------------------------------------------
        
        cust_query = text("SELECT customer_type FROM customers WHERE customer_id = :cid")
        cust_res = db.execute(cust_query, {"cid": ticket.customer_id}).fetchone()
        dynamic_customer_type = cust_res[0] if cust_res else "Regular"
        
        ord_query = text("SELECT SUM(order_value) FROM purchased_orders WHERE customer_id = :cid")
        ord_res = db.execute(ord_query, {"cid": ticket.customer_id}).fetchone()
        dynamic_order_value = ord_res[0] if (ord_res and ord_res[0] is not None) else 0.0
        
        comp_query = text("SELECT COUNT(*) FROM complaint_registry WHERE customer_id = :cid")
        comp_res = db.execute(comp_query, {"cid": ticket.customer_id}).fetchone()
        dynamic_previous_complaints = comp_res[0] if comp_res else 0

        # ----------------------------------------------------
        # 🧠 STEP 2: LLM & ML PROCESSING
        # ----------------------------------------------------
        llm_insights = analyze_customer_ticket(ticket.message)
        sentiment = llm_insights.get("sentiment", "Neutral")
        department = llm_insights.get("category", "Other") 
        intent = llm_insights.get("intent", "General Inquiry")

        if ml_model and encoders:
            input_df = pd.DataFrame([{
                "customer_type": dynamic_customer_type,
                "order_value": dynamic_order_value,
                "previous_complaints": dynamic_previous_complaints,
                "department": department,
                "sentiment": sentiment
            }])
            
            for col in ['customer_type', 'department', 'sentiment']:
                input_df[col] = encoders[col].transform(input_df[col])
            
            prediction = ml_model.predict(input_df)
            final_priority = prediction[0]
        else:
            final_priority = "Model Not Found"

        # 👇 ====== FAILSAFE OVERRIDE ====== 👇
        if department == "Logistics" and intent == "Greeting":
            intent = "Shipping Inquiry"
            sentiment = "Negative"
            final_priority = "High"

        if intent == "Greeting" and department == "Other":
            final_priority = "Low"
        # 👆 ================================ 👆

        # ----------------------------------------------------
        # 🗄️ STEP 3: SAVE TO MASTER & LOGS TABLES
        # ----------------------------------------------------
        
        check_ticket = db.execute(text("SELECT ticket_id FROM complaint_registry WHERE ticket_id = :tid"), {"tid": current_ticket_id}).fetchone()
        
        if not check_ticket:
            ins_master = text("""
                INSERT INTO complaint_registry (ticket_id, customer_id, intent, department, ml_priority) 
                VALUES (:tid, :cid, :intent, :dept, :pri)
            """)
            db.execute(ins_master, {
                "tid": current_ticket_id, "cid": ticket.customer_id, 
                "intent": intent, "dept": department, "pri": final_priority
            })
            
        ins_log = text("""
            INSERT INTO complaint_logs (ticket_id, sender, message, sentiment) 
            VALUES (:tid, 'Customer', :msg, :sent)
        """)
        db.execute(ins_log, {
            "tid": current_ticket_id, "msg": ticket.message, "sent": sentiment
        })

        db.commit() 

        # ----------------------------------------------------
        # 📤 STEP 4: RETURN FINAL JSON
        # ----------------------------------------------------
        return {
            "status": "success",
            "message": "Dynamic Routing Completed & Saved to DB!",
            "ticket_details": {
                "ticket_id": current_ticket_id,
                "customer_id": ticket.customer_id
            },
            "dynamic_data_fetched": {
                "customer_type": dynamic_customer_type,
                "order_value": dynamic_order_value,
                "previous_complaints": dynamic_previous_complaints
            },
            "llm_analysis": {
                "intent": intent,
                "department_assigned": department,
                "sentiment": sentiment
            },
            "ml_decision": {
                "priority": final_priority
            }
        }
        
    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail=f"Processing Error: {str(e)}")
    finally:
        db.close()

@app.get("/products")
async def get_products():
    db = SessionLocal()
    try:
        rows = db.execute(text("SELECT product_id, name, price, stock, description FROM products WHERE stock > 0")).fetchall()
        return {"products": [
            {"product_id": r[0], "name": r[1], "price": r[2], "stock": r[3], "description": r[4]}
            for r in rows
        ]}
    finally:
        db.close()


@app.post("/checkout")
async def checkout(order: CheckoutRequest):
    db = SessionLocal()
    try:
        # Find existing customer by email, else create new
        existing = db.execute(text("SELECT customer_id FROM customers WHERE email = :email"),
                               {"email": order.customer_email}).fetchone()
        if existing:
            customer_id = existing[0]
            # Keep phone number up to date in case it changed
            db.execute(text("UPDATE customers SET phone_number = :phone WHERE customer_id = :cid"),
                       {"phone": order.phone_number, "cid": customer_id})
        else:
            customer_id = f"C-{uuid.uuid4().hex[:6].upper()}"
            db.execute(text("""
                INSERT INTO customers (customer_id, name, email, phone_number, customer_type)
                VALUES (:cid, :name, :email, :phone, :ctype)
            """), {"cid": customer_id, "name": order.customer_name,
                    "email": order.customer_email, "phone": order.phone_number,
                    "ctype": order.customer_type})

        # Calculate order total from live product prices (never trust client price)
        order_value = 0.0
        line_items = []
        for item in order.items:
            prod = db.execute(text("SELECT name, price, stock FROM products WHERE product_id = :pid"),
                               {"pid": item.product_id}).fetchone()
            if not prod:
                raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
            if prod[2] < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {item.product_id}")
            order_value += prod[1] * item.quantity
            line_items.append((item.product_id, prod[0], item.quantity, prod[1]))

        order_id = f"O-{uuid.uuid4().hex[:6].upper()}"

        for pid, pname, qty, unit_price in line_items:
            line_total = unit_price * qty
            db.execute(text("""
                INSERT INTO purchased_orders (order_id, customer_id, product_id, product_name,
                                               quantity, unit_price, order_value)
                VALUES (:oid, :cid, :pid, :pname, :qty, :price, :line_total)
            """), {
                "oid": order_id, "cid": customer_id, "pid": pid, "pname": pname,
                "qty": qty, "price": unit_price, "line_total": line_total
            })
            db.execute(text("UPDATE products SET stock = stock - :qty WHERE product_id = :pid"),
                       {"qty": qty, "pid": pid})

        db.commit()
        return {
            "status": "success",
            "customer_id": customer_id,
            "order_id": order_id,
            "order_value": order_value
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Checkout Error: {str(e)}")
    finally:
        db.close()
