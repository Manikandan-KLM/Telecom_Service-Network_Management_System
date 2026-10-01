from fastapi import FastAPI

from database import Base, engine

from fastapi.middleware.cors import CORSMiddleware

from config import settings


from routes import auth
from routes import user
from routes import customers
from routes import service_plan
from routes import sim_card
from routes import device
from routes import subscription
from routes import usage
from routes import network_tower
from routes import network_equipment
from routes import network_outage
from routes import technician
from routes import support_ticket
from routes import sla
from routes import notification
from routes import dashboard
from routes import report
from routes import audit_log



from utils.exception_handlers import (
    register_exception_handlers
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Telecom Service & Network Management System",
    description="Advanced Telecom Backend API",
    version="1.0.0"
)

origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ],
    allow_headers=[
        "Authorization",
        "Content-Type"
    ]
)

register_exception_handlers(app)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(customers.router)
app.include_router(service_plan.router)
app.include_router(sim_card.router)
app.include_router(device.router)
app.include_router(subscription.router)
app.include_router(usage.router)
app.include_router(network_tower.router)
app.include_router(network_equipment.router)
app.include_router(network_outage.router)
app.include_router(technician.router)
app.include_router(support_ticket.router)
app.include_router(sla.router)
app.include_router(notification.router)
app.include_router(dashboard.router)
app.include_router(report.router)
app.include_router(audit_log.router)



@app.get("/")
def root():

    return {
        "message": "Telecom Service & Network Management API",
        "version": "1.0.0"
    }