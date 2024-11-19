from fastapi import FastAPI,Depends,HTTPException,status
from contextlib import asynccontextmanager
from .db import create_table
from .image_routes import router2
from .rout import router
# from .kafka import kafka_consumer
from fastapi.routing import APIRoute
# import asyncio
# from typing import Annotated
# import httpx
# from fastapi.security import OAuth2PasswordBearer


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"
# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     print("Received token:", token)  # Debug print
#     if token is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     url = "http://user_service:8000/get_user"  # URL to the user service
#     headers = {"Authorization": f"Bearer {token}"}
#     print("Sending request to user service with headers:", headers)

#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers)
    
#     print("Request headers:", headers)
#     print("Response status code:", response.status_code)  # Debug print

#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("Response body:", response.text)  # Print response body for debugging
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifspan event is started")
    print("table creating....")
    create_table()
    print("creating table succesfully")
    # task = asyncio.create_task(kafka_consumer('product_topic','broker:19092'))
    # task2 = asyncio.create_task(kafka_consumer("product_image",'broker:19092'))
    yield    
app = FastAPI(lifespan=lifespan,
               title="FastAPI  Product Service",
               description="This is a FastAPI Service",
               version="0.0.1",
               generate_unique_id_function=custom_generate_unique_id
)
@app.get("/",tags=["Product Service Routs"])
async def root():
    return {"message": "welcome to the product Service"}

app.include_router(router=router,tags=["Prodcut All Api"])
app.include_router(router=router2,tags=["Images All Api "])

# Adding new user in Repo to add code