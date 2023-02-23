from app import schemas
import pytest
import json
from app.oauth2 import settings,SECRET_KEY,ALGORITHM
from jose import JWTError,jwt

def test_root(client):
    res = client.get("/")
    print(res.json().get("message"))
    assert res.status_code == 200
    assert res.json().get("message") == "Welcome to My API"

def test_create_user(client):
    res = client.post("/users",json={"email":"test1@gmail.com","password":"test123"})
    new_user = schemas.UserResponse(**res.json())  
    assert new_user.email == "test1@gmail.com"  
    assert res.status_code == 201


def test_login_user(client,test_user):
    res = client.post("/login",data={"username":test_user["email"],"password":test_user["password"]})  
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,SECRET_KEY, algorithms=[ALGORITHM])    
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == 'bearer'
    assert res.status_code == 200  

@pytest.mark.parametrize("email,password,status_code",[
    ("wrongemail@gmail.com","test123",403),
    ("test1@gmail.com","wrongtest123",403),
    ("wrongtest1@gmail.com","wrongtest123",403),
    (None,"test123",422),
    ("test1@gmail.com",None,422),   
    ])
def test_incorrect_login(client,test_user,email,password,status_code):
    res = client.post("/login",data={"username":email,"password":password}) 
    assert res.status_code == status_code
