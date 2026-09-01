from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
class LoginData(BaseModel):
    username: str
    password: str
from database import Base, engine, SessionLocal
from fastapi.staticfiles import StaticFiles
from models import Department, Employee, Card, Admin , TransferRequest
from fastapi import UploadFile, File
import pandas as pd
from openpyxl import load_workbook 

app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory="."),
    name="static"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return FileResponse("login.html")

@app.get("/indexx.html")
def index_page():
    return FileResponse("indexx.html")

@app.get("/test-database")
def test_database():
    try:
        with engine.connect():
            return {
                "message": "تم الاتصال بقاعدة البيانات بنجاح"
            }

    except Exception as error:
        return {
            "message": "فشل الاتصال بقاعدة البيانات",
            "error": str(error)
        }
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class DepartmentCreate(BaseModel):
    department_name: str
class EmployeeCreate(BaseModel):
    name: str
    employee_number: str
    department: str
    basic_salary: int = 0
    housing: int = 0
    transport: int = 0
    total_salary: int = 0
class CardCreate(BaseModel):
    employee_id: int
    name: str
    employee_number: str
    department: str
    month: str
    basic_salary: int = 0
    housing: int = 0
    transport: int = 0
    discount: int = 0
    advance: int = 0
    total_salary: int = 0
    net_salary: int = 0

@app.get("/departments")
def get_departments(
    admin_department_id: int | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if admin_department_id is None:
        raise HTTPException(
            status_code=401,
            detail="يجب تسجيل الدخول أولاً"
        )

    departments = db.query(Department).filter(
        Department.id != admin_department_id
    ).all()

    return [
        {
            "id": department.id,
            "department_name": department.department_name
        }
        for department in departments
    ]

@app.post("/departments")
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db)
):
    department_name = department.department_name.strip()

    if department_name == "":
        raise HTTPException(
            status_code=400,
            detail="اسم القسم مطلوب"
        )

    existing_department = db.query(Department).filter(
        Department.department_name == department_name
    ).first()

    if existing_department:
        raise HTTPException(
            status_code=400,
            detail="القسم موجود مسبقًا"
        )

    new_department = Department(
        department_name=department_name
    )

    db.add(new_department)

    try:
        db.commit()
        db.refresh(new_department)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="القسم موجود مسبقًا"
        )

    return {
        "id": new_department.id,
        "department_name": new_department.department_name
    }


@app.delete("/departments/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="القسم غير موجود"
        )

    db.delete(department)
    db.commit()

    return {
        "message": "تم حذف القسم بنجاح"
    }

@app.get("/employees")
def get_employees(
    admin_department_id: int | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if admin_department_id is None:
        raise HTTPException(
            status_code=401,
            detail="يجب تسجيل الدخول أولاً"
        )

    department = db.query(Department).filter(
        Department.id == admin_department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="القسم غير موجود"
        )

    employees = db.query(Employee).filter(
        Employee.department == department.department_name
    ).all()

    return [
        {
            "id": employee.id,
            "name": employee.name,
            "employee_number": employee.employee_number,
            "department": employee.department,
            "basic_salary": employee.basic_salary,
            "housing": employee.housing,
            "transport": employee.transport,
            "total_salary": employee.total_salary
        }
        for employee in employees
    ]

@app.get("/employees/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="الموظف غير موجود"
        )

    return {
        "id": employee.id,
        "name": employee.name,
        "employee_number": employee.employee_number,
        "department": employee.department,
        "basic_salary": employee.basic_salary,
        "housing": employee.housing,
        "transport": employee.transport,
        "total_salary": employee.total_salary
    }


@app.post("/employees")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    name = employee.name.strip()
    employee_number = employee.employee_number.strip()
    department = employee.department.strip()

    if name == "":
        raise HTTPException(
            status_code=400,
            detail="اسم الموظف مطلوب"
        )

    if employee_number == "":
        raise HTTPException(
            status_code=400,
            detail="الرقم الوظيفي مطلوب"
        )

    if department == "":
        raise HTTPException(
            status_code=400,
            detail="القسم مطلوب"
        )

    existing_employee = db.query(Employee).filter(
        Employee.employee_number == employee_number
    ).first()

    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="الرقم الوظيفي مستخدم مسبقًا"
        )

    total_salary = (
        employee.basic_salary
        + employee.housing
        + employee.transport
    )

    new_employee = Employee(
        name=name,
        employee_number=employee_number,
        department=department,
        basic_salary=employee.basic_salary,
        housing=employee.housing,
        transport=employee.transport,
        total_salary=total_salary
    )

    db.add(new_employee)

    try:
        db.commit()
        db.refresh(new_employee)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="تعذر إضافة الموظف"
        )

    return {
        "id": new_employee.id,
        "name": new_employee.name,
        "employee_number": new_employee.employee_number,
        "department": new_employee.department,
        "basic_salary": new_employee.basic_salary,
        "housing": new_employee.housing,
        "transport": new_employee.transport,
        "total_salary": new_employee.total_salary
    }


@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="الموظف غير موجود"
        )

    duplicate_employee = db.query(Employee).filter(
        Employee.employee_number
        == employee_data.employee_number.strip(),
        Employee.id != employee_id
    ).first()

    if duplicate_employee:
        raise HTTPException(
            status_code=400,
            detail="الرقم الوظيفي مستخدم لموظف آخر"
        )

    employee.name = employee_data.name.strip()
    employee.employee_number = (
        employee_data.employee_number.strip()
    )
    employee.department = employee_data.department.strip()
    employee.basic_salary = employee_data.basic_salary
    employee.housing = employee_data.housing
    employee.transport = employee_data.transport
    employee.total_salary = (
        employee_data.basic_salary
        + employee_data.housing
        + employee_data.transport
    )

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="تعذر تعديل الموظف"
        )

    return {
        "id": employee.id,
        "name": employee.name,
        "employee_number": employee.employee_number,
        "department": employee.department,
        "basic_salary": employee.basic_salary,
        "housing": employee.housing,
        "transport": employee.transport,
        "total_salary": employee.total_salary
    }


@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="الموظف غير موجود"
        )

    db.delete(employee)
    db.commit()

    return {
        "message": "تم حذف الموظف بنجاح"
    }

@app.get("/cards")
def get_cards(
    db: Session = Depends(get_db)
):
    cards = db.query(Card).all()

    return [
        {
            "id": card.id,
            "employee_id": card.employee_id,
            "name": card.name,
            "employee_number": card.employee_number,
            "department": card.department,
            "month": card.month,
            "basic_salary": card.basic_salary,
            "housing": card.housing,
            "transport": card.transport,
            "discount": card.discount,
            "advance": card.advance,
            "total_salary": card.total_salary,
            "net_salary": card.net_salary
        }
        for card in cards
    ]


@app.get("/cards/{card_id}")
def get_card(
    card_id: int,
    db: Session = Depends(get_db)
):
    card = db.query(Card).filter(
        Card.id == card_id
    ).first()

    if card is None:
        raise HTTPException(
            status_code=404,
            detail="الكارت غير موجود"
        )

    return {
        "id": card.id,
        "employee_id": card.employee_id,
        "name": card.name,
        "employee_number": card.employee_number,
        "department": card.department,
        "month": card.month,
        "basic_salary": card.basic_salary,
        "housing": card.housing,
        "transport": card.transport,
        "discount": card.discount,
        "advance": card.advance,
        "total_salary": card.total_salary,
        "net_salary": card.net_salary
    }


@app.post("/cards")
def create_card(
    card: CardCreate,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(
        Employee.id == card.employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="الموظف غير موجود"
        )

    existing_card = db.query(Card).filter(
        Card.employee_id == card.employee_id,
        Card.month == card.month
    ).first()

    if existing_card:
        raise HTTPException(
            status_code=400,
            detail="يوجد كارت لهذا الموظف في هذا الشهر"
        )

    total_salary = (
        card.basic_salary
        + card.housing
        + card.transport
    )

    net_salary = (
        total_salary
        - card.discount
        - card.advance
    )

    new_card = Card(
        employee_id=employee.id,
        name=employee.name,
        employee_number=employee.employee_number,
        department=employee.department,
        month=card.month,
        basic_salary=card.basic_salary,
        housing=card.housing,
        transport=card.transport,
        discount=card.discount,
        advance=card.advance,
        total_salary=total_salary,
        net_salary=net_salary
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    return {
        "id": new_card.id,
        "employee_id": new_card.employee_id,
        "name": new_card.name,
        "employee_number": new_card.employee_number,
        "department": new_card.department,
        "month": new_card.month,
        "basic_salary": new_card.basic_salary,
        "housing": new_card.housing,
        "transport": new_card.transport,
        "discount": new_card.discount,
        "advance": new_card.advance,
        "total_salary": new_card.total_salary,
        "net_salary": new_card.net_salary
    }


@app.put("/cards/{card_id}")
def update_card(
    card_id: int,
    card_data: CardCreate,
    db: Session = Depends(get_db)
):
    card = db.query(Card).filter(
        Card.id == card_id
    ).first()

    if card is None:
        raise HTTPException(
            status_code=404,
            detail="الكارت غير موجود"
        )

    employee = db.query(Employee).filter(
        Employee.id == card_data.employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="الموظف غير موجود"
        )

    duplicate_card = db.query(Card).filter(
        Card.employee_id == card_data.employee_id,
        Card.month == card_data.month,
        Card.id != card_id
    ).first()

    if duplicate_card:
        raise HTTPException(
            status_code=400,
            detail="يوجد كارت آخر لهذا الموظف في هذا الشهر"
        )

    total_salary = (
        card_data.basic_salary
        + card_data.housing
        + card_data.transport
    )

    net_salary = (
        total_salary
        - card_data.discount
        - card_data.advance
    )

    card.employee_id = employee.id
    card.name = employee.name
    card.employee_number = employee.employee_number
    card.department = employee.department
    card.month = card_data.month
    card.basic_salary = card_data.basic_salary
    card.housing = card_data.housing
    card.transport = card_data.transport
    card.discount = card_data.discount
    card.advance = card_data.advance
    card.total_salary = total_salary
    card.net_salary = net_salary

    db.commit()
    db.refresh(card)

    return {
        "id": card.id,
        "employee_id": card.employee_id,
        "name": card.name,
        "employee_number": card.employee_number,
        "department": card.department,
        "month": card.month,
        "basic_salary": card.basic_salary,
        "housing": card.housing,
        "transport": card.transport,
        "discount": card.discount,
        "advance": card.advance,
        "total_salary": card.total_salary,
        "net_salary": card.net_salary
    }


@app.delete("/cards/{card_id}")
def delete_card(
    card_id: int,
    db: Session = Depends(get_db)
):
    card = db.query(Card).filter(
        Card.id == card_id
    ).first()

    if card is None:
        raise HTTPException(
            status_code=404,
            detail="الكارت غير موجود"
        )

    db.delete(card)
    db.commit()

    return {
        "message": "تم حذف الكارت بنجاح"
    }
@app.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    df = pd.read_excel(file.file)

    for _, row in df.iterrows():

        card = db.query(Card).filter(
            Card.employee_number == row["employee_number"]
        ).first()

        if card:
            card.advance = row["advance"]
            card.discount = row["discount"]

            card.net_salary = (
                card.total_salary
                - card.advance
                - card.discount
            )

    db.commit()

    return {"message": "تم رفع الملف بنجاح"}

@app.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    df = pd.read_excel(file.file) 
    for _, row in df.iterrows():
        card = db.query(Card).filter(
            Card.employee_number == str(row["employee_number"])
        ).first()

    if card:
        card.basic_salary = int(row["basic_salary"])
        card.housing = int(row["housing"])
        card.transport = int(row["transport"])
        card.advance = int(row["advance"])
        card.discount = int(row["discount"])
        
        card.total_salary = (
        card.basic_salary
        + card.housing
        + card.transport
    )
        card.net_salary = (
        card.total_salary
        - card.advance
        - card.discount
    )
    db.commit()

    return {
        "message": "تم رفع الملف بنجاح"
    }
@app.get("/export-payroll")
def export_payroll(db: Session = Depends(get_db)):

    workbook = load_workbook("payroll_template.xlsx")
    sheet = workbook.active

    cards = db.query(Card).all()

    row = 2

    for card in cards:
        employee = db.query(Employee).filter(
            Employee.employee_number == card.employee_number
        ).first()

        sheet[f"A{row}"] = card.employee_number
        sheet[f"B{row}"] = card.name
        sheet[f"C{row}"] = card.basic_salary
        sheet[f"D{row}"] = card.housing
        sheet[f"E{row}"] = card.transport
        sheet[f"F{row}"] = card.advance
        sheet[f"G{row}"] = card.discount
        sheet[f"H{row}"] = card.total_salary
        sheet[f"I{row}"] = card.net_salary

        row += 1

    workbook.save("payroll_result.xlsx")

    return FileResponse(
        "payroll_result.xlsx",
        filename="payroll_result.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@app.post("/login")
def login(
    data: LoginData,
    response: Response,
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(
        Admin.username == data.username,
        Admin.password == data.password
    ).first()

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    response.set_cookie(
        key="admin_department_id",
        value=str(admin.department_id),
        httponly=True,
        samesite="lax"
    )

    return {
        "success": True,
        "admin_id": admin.id,
        "username": admin.username,
        "department_id": admin.department_id
    }
class TransferCreate(BaseModel):
    employee_id: int
    to_department_id: int
    requested_by: int


@app.post("/transfer-requests")
def create_transfer_request(
    data: TransferCreate,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == data.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    from_department = db.query(Department).filter(
        Department.department_name == employee.department
    ).first()

    if not from_department:
        raise HTTPException(
            status_code=404,
            detail="Current department not found"
        )

    request = TransferRequest(
        employee_id=employee.id,
        from_department_id=from_department.id,
        to_department_id=data.to_department_id,
        requested_by=data.requested_by,
        status="pending"
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return {
        "message": "Transfer request sent successfully"
    }
@app.get("/transfer-requests/pending/{department_id}")
def get_pending_transfer_requests(
    department_id: int,
    db: Session = Depends(get_db)
):
    requests = db.query(TransferRequest).filter(
        TransferRequest.to_department_id == department_id,
        TransferRequest.status == "pending"
    ).all()

    result = []

    for request in requests:
        employee = db.query(Employee).filter(
            Employee.id == request.employee_id
        ).first()

        from_department = db.query(Department).filter(
            Department.id == request.from_department_id
        ).first()

        to_department = db.query(Department).filter(
            Department.id == request.to_department_id
        ).first()

        result.append({
            "id": request.id,
            "employee_id": request.employee_id,
            "employee_name": employee.name if employee else "",
            "from_department": (
                from_department.department_name
                if from_department else ""
            ),
            "to_department": (
                to_department.department_name
                if to_department else ""
            ),
            "status": request.status
        })

    return result


@app.put("/transfer-requests/{request_id}/approve")
def approve_transfer_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    transfer_request = db.query(TransferRequest).filter(
        TransferRequest.id == request_id
    ).first()

    if not transfer_request:
        raise HTTPException(
            status_code=404,
            detail="Transfer request not found"
        )

    employee = db.query(Employee).filter(
        Employee.id == transfer_request.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    to_department = db.query(Department).filter(
        Department.id == transfer_request.to_department_id
    ).first()

    if not to_department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    employee.department = to_department.department_name
    transfer_request.status = "approved"

    db.commit()

    return {
        "message": "Transfer request approved successfully"
    }
@app.put("/transfer-requests/{request_id}/reject")
def reject_transfer_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    transfer_request = db.query(TransferRequest).filter(
        TransferRequest.id == request_id
    ).first()

    if not transfer_request:
        raise HTTPException(
            status_code=404,
            detail="Transfer request not found"
        )

    transfer_request.status = "rejected"

    db.commit()

    return {
        "message": "Transfer request rejected successfully"
    }