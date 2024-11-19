from fastapi import FastAPI
from .router import user_router  
from .admin_rout import admin_route
from fastapi.routing import APIRoute
from .db import create_table
from .super_admin_rout import super_router
from .superAdminCrud import initialize_super_admin
from .login_rout import router_login
# from .Oauth import get_current_user,super_admin_required
def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"
def lifespan(app: FastAPI):
    print("Application started")
    create_table()
    print("Table created")
    print("Application started")
    initialize_super_admin()
    print("Super Admin created")
    yield

app = FastAPI(
    lifespan=lifespan,
    title="FastAPI user service",
    description="This is a FastAPI Service for managing users",
    version="0.0.1",
    generate_unique_id_function=custom_generate_unique_id
)

@app.get("/", tags=["user Service Routes"])
async def root():
    return {"message": "Welcome to the user service "}


app.include_router(user_router, tags=["users all api"])


app.include_router(admin_route, tags=["users admin api"])

app.include_router(super_router, tags=["super admin api"])  
app.include_router(router_login, tags=["All user Login endpoint"])  



