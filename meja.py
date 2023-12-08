from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
from typing import Annotated
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import requests
from models.model import RecommendationReq, Reservation, Table, Token, TokenData, User, UserInDB, Consultation

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "hilmi": {
        "username": "hilmi",
        "full_name": "hilmi BR",
        "email": "hilmibr@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    }
}

with open("tables.json", "r") as read_file:
    data_tables = json.load(read_file)
with open("reservations.json", "r") as read_file:
    data_reservations = json.load(read_file)
with open("user_reservasi.json","r") as read_file:
	user_reservasi = json.load(read_file)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

saved_password= None

bevbuddy_url = 'https://bevbuddy--uj4gj7u.thankfulbush-47818fd3.southeastasia.azurecontainerapps.io/'

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    for user in user_reservasi['user_reservasi']:
        if user['username'] == username:
           user_dict = {
                "id_user" : user['id_user'],
                "username" :  user['username'],
                "full_name": user['full_name'],
                "email" : user['email'],
                "role" : user['role'],
                "hashed_password": user['hashed_password'],
                "password" : ""
           }
           return UserInDB(**user_dict)
    return None



def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/register", tags=['User'])
async def register_user(data: User):
    global bevbuddy_url

    dataUser_found = False
    
    for user in user_reservasi['user_reservasi']:
        if user['username'] == data.username:
            dataUser_found = True
            return f"User {user['id_user']} dengan username {user['username']} telah terdaftar."

    if not dataUser_found:
        i = len(user_reservasi['user_reservasi']) + 1
        result = {
            "id_user": i,
            "username" : data.username,
            "full_name" : data.full_name,
            "email": data.email,
            "role": data.role,
            "hashed_password": get_password_hash(data.password)
        }
        user_reservasi['user_reservasi'].append(result)
        with open("user_reservasi.json", "w") as write_file:
            json.dump(user_reservasi, write_file)

        # Register ke API BevBuddy
        register_url = bevbuddy_url + 'register'
        register_data_string = {
            "username": data.username,
            "fullname": data.full_name,
            "email": data.email,
            "password": data.password,
            "role": "customer",
            "token": "string"
        }

        response = requests.post(register_url, data=json.dumps(register_data_string))

        return response.json()

    raise HTTPException(
        status_code=404, detail=f'User not found'
    )

@app.post("/token", response_model=Token, tags=['User'])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
    global saved_password
    user = authenticate_user(form_data.username, form_data.password)
    saved_password=form_data.password
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User, tags=['User'])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user, saved_password


# @app.get("/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[User, Depends(get_current_active_user)]
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]

def table_to_true(tables, id_table_input, hourstart_input, duration_input):
        duration_input_ctr = 0
        for row in tables:
            if (row["id_table"] == id_table_input):
                if (row["hourstart"] == hourstart_input):
                    row["status"] = True
                    duration_input_ctr += 1
            if (duration_input_ctr > 0):
                row["status"] = True
                if (duration_input_ctr == duration_input):
                    break
                duration_input_ctr += 1

def table_to_false(tables, id_table_input, hourstart_input, duration_input):
        duration_input_ctr = 0
        for row in tables:
            if (row["id_table"] == id_table_input):
                if (row["hourstart"] == hourstart_input):
                    row["status"] = False
                    duration_input_ctr += 1
            if (duration_input_ctr > 0):
                row["status"] = False
                if (duration_input_ctr == duration_input):
                    break
                duration_input_ctr += 1

def check_table_status(tables, id_table_input, hourstart_input):
    if (hourstart_input < 8 or hourstart_input > 21):
        raise HTTPException(status_code=400, detail=f"Invalid starthour: {hourstart_input}") 
    else:
        if (id_table_input < 1 or id_table_input > max(tables, key=lambda x: x['id_table'])['id_table']):
            raise HTTPException(status_code=404, detail=f"Table with id_table {id_table_input} not found")
        else: 
            for row in tables:
                if (row["id_table"] == id_table_input):
                    if (row["hourstart"] == hourstart_input):
                        return row["status"]

# Make a new reservation
@app.post('/reservations', tags=["Pengaturan Reservasi"])
async def create_reservation(reserver_name_input: str, id_table_input: int, hourstart_input: int, duration_input: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    # Generate id_reservation
    reservations = data_reservations["reservations"]
    new_id_reservation = max(reservations, key=lambda x: x['id_reservation'])['id_reservation'] + 1
    # Get table data
    tables = data_tables["tables"]

    temp_hourstart_input = hourstart_input
    for i in range(duration_input):
        table_status = check_table_status(tables, id_table_input, temp_hourstart_input)
        if (table_status == False):
            raise HTTPException(status_code=400, detail="No available tables for the requested time")
        temp_hourstart_input += 1
    
    new_reservation = {
        "id_reservation": new_id_reservation,
        "reserver_name": reserver_name_input,
        "id_user": current_user.id_user,
        "id_table": id_table_input,
        "hourstart": hourstart_input,
        "duration": duration_input
    }

    # update Table table data
    table_to_false(tables, id_table_input, hourstart_input, duration_input)

    # Reservation append
    reservations.append(new_reservation)
    with open("reservations.json", "w") as write_file:
        json.dump(data_reservations, write_file)
    with open("tables.json", "w") as write_file:
        json.dump(data_tables, write_file)

    return new_reservation

# Check table status by id_table and hourstart
@app.get('/tables/{id_table}/status', tags=["Pengaturan Meja"])
async def get_table_status(id_table_input: int, hourstart_input: int):
    tables = data_tables["tables"]

    def table_status(tables, id_table_input, hourstart_input):
        if (hourstart_input < 8 or hourstart_input > 21):
            raise HTTPException(status_code=400, detail=f"Invalid starthour: {hourstart_input}") 
        else:
            if (id_table_input < 1 or id_table_input > 3):
                raise HTTPException(status_code=404, detail=f"Table with id_table {id_table_input} not found")
            else: 
                for row in tables:
                    if (row["id_table"] == id_table_input):
                        if (row["hourstart"] == hourstart_input):
                            return row["status"]
                        
    status = table_status(tables, id_table_input, hourstart_input)
                        
    return status

# Update reservation
@app.put('/reservation/{id_reservation}', tags=["Pengaturan Reservasi"])
async def update_reservation(id_reservation_input: int, new_reserver_name: str, new_id_table: int, new_hourstart: int, new_duration: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    found = False
    idx = 0
    for reservation in data_reservations.get('reservations', []):
        if reservation['id_reservation'] == id_reservation_input:
            found = True
            reservations = data_reservations["reservations"]
            reservation = next((r for r in reservations if r["id_reservation"] == id_reservation_input), None)

            # Ngubah status ketersediaan mejanya dulu yang tadinya false jadi true
            id_table_input = reservation["id_table"]
            hourstart_input = reservation["hourstart"]
            duration_input = reservation["duration"]

            tables = data_tables["tables"]
            table_to_true(tables, id_table_input, hourstart_input, duration_input)

            temp_hourstart_input = hourstart_input
            for i in range(duration_input):
                table_status = check_table_status(tables, id_table_input, temp_hourstart_input)
                if (table_status == False):
                    raise HTTPException(status_code=400, detail="No available tables for the requested time")
                temp_hourstart_input += 1
            
            reservations[idx] = {
                "id_reservation": id_reservation_input,
                "reserver_name": new_reserver_name,
                "id_table": new_id_table,
                "hourstart": new_hourstart,
                "duration": new_duration
            }

            # update Table table data
            table_to_false(tables, new_id_table, new_hourstart, new_duration)

            data_tables["tables"] = tables
            data_reservations["reservations"] = reservations
            with open("tables.json", "w") as write_file:
                json.dump(data_tables, write_file)
            with open("reservations.json", "w") as write_file:
                json.dump(data_reservations, write_file)

            return reservations[idx]
        idx+=1
    if not found:
        raise HTTPException(status_code=404, detail="Reservation not found")

# Delete Reservation
@app.delete('/reservations/{id_reservation}', tags=["Pengaturan Reservasi"])
async def delete_reservation(id_reservation_input: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    reservations = data_reservations["reservations"]
    reservation = next((r for r in reservations if r["id_reservation"] == id_reservation_input), None)

    if reservation is not None:
        id_table_input = reservation["id_table"]
        hourstart_input = reservation["hourstart"]
        duration_input = reservation["duration"]

        tables = data_tables["tables"]
        table_to_true(tables, id_table_input, hourstart_input, duration_input)
        for i, reservation in enumerate(reservations):
            if reservation["id_reservation"] == id_reservation_input:
                deleted_reservation = reservations[i]
                reservations.pop(i)
                data_reservations["reservations"] = reservations
                with open("reservations.json", "w") as write_file:
                    json.dump(data_reservations, write_file)
                return deleted_reservation
    else:
        raise HTTPException(status_code=404, detail="Reservation not found")
    

# Get reservation by username's account
@app.get('/reservations', tags=["Pengaturan Reservasi"])
async def get_reservation_of_username(current_user: Annotated[User, Depends(get_current_active_user)]):
    reservations = data_reservations["reservations"]
    found = False
    user_reservation = []
    for reservation in reservations:
        if (reservation["id_user"] == current_user.id_user):
            user_reservation.append(reservation)
            found = True
    if found:
        return user_reservation
    raise HTTPException(status_code=404, detail="Reservation not found")


# ADMIN ONLY SITUATION
# Get reservation data by ID
@app.get('/reservations/{reservation_id}', tags=["Pengaturan Reservasi"])
async def get_reservation(reservation_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    if (current_user.role != 'admin'):
        return "admin only"
    else:
        found = False
        for reservation in data_reservations.get('reservations', []):
            if reservation['id_reservation'] == reservation_id:
                found = True
                return reservation
        if not found:
            raise HTTPException(status_code=404, detail="Reservation not found")
        
# @app.get('/reservations', tags=["Pengaturan Reservasi"])
# async def get_all_reservations(current_user: Annotated[User, Depends(get_current_active_user)]):
#     if (current_user.role != 'admin'):
#         return "admin only"
#     else:
#         return data_reservations["reservations"]

@app.post('/tables', tags=["Pengaturan Meja"])
def add_table(current_user: Annotated[User, Depends(get_current_active_user)]):
    if (current_user.role != 'admin'):
        return "admin only"
    else:
        tables = data_tables["tables"]
        new_id_table = max(tables, key=lambda x: x['id_table'])['id_table'] + 1
        for i in range(8, 22):
            new_table = {
                    "id_table": new_id_table,
                    "hourstart": i,
                    "status": True
            }
            tables.append(new_table)
        with open("tables.json", "w") as write_file:
            json.dump(data_tables, write_file)
        return tables

@app.delete('/tables', tags=["Pengaturan Meja"])
def reduce_table(current_user: Annotated[User, Depends(get_current_active_user)]):
    if (current_user.role != 'admin'):
        return "admin only"
    else:
        tables = data_tables["tables"]
        reduce_id_table = max(tables, key=lambda x: x['id_table'])['id_table']
        
        new_tables = []
        for row in tables:
            if row["id_table"] != reduce_id_table:
                new_tables.append(row)
            else:
                break

        data_tables["tables"] = new_tables
        # Save the updated data back to the JSON file
        with open("tables.json", "w") as write_file:
            json.dump(data_tables, write_file)

        return data_tables["tables"]

# Get All Menus
@app.get("/integrasi-menu", tags=["Integrasi: Layanan Beverage Buddy"])
async def integrasi_get_menu_all(token: str = Depends(oauth2_scheme)):
    url = 'https://bevbuddy.up.railway.app/menus'
    headers = {
        'accept': 'application/json',
    }

    response = requests.get(url, headers=headers, timeout=10)
    return response.json()

# Get Menu by ID
@app.get("/integrasi-menu-by-id/{id_menu}", tags=["Integrasi: Layanan Beverage Buddy"])
async def integrasi_get_menu_by_id(id_menu: int, token: str = Depends(oauth2_scheme)):
    url = 'https://bevbuddy.up.railway.app/menus' + f'/{id_menu}'
    print(url)
    headers = {
        'accept': 'application/json',
    }

    response = requests.get(url, headers=headers, timeout=10)
    return response.json()

# Get All Nutritions
@app.get("/integrasi-nutrisi", tags=["Integrasi: Layanan Beverage Buddy"])
async def integrasi_get_nutrisi(token: str = Depends(oauth2_scheme)):
    global bevbuddy_url

    url = bevbuddy_url + 'nutritions'
    headers = {
        'accept': 'application/json',
    }

    response = requests.get(url, headers=headers, timeout=10)
    return response.json()

# Get Nutrition by ID
@app.get("/integrasi-nutritions-by-id/{id_nutritions}", tags=["Integrasi: Layanan Beverage Buddy"])
async def integrasi_get_nutritions_by_id(id_nutritions: int, token: str = Depends(oauth2_scheme)):
    global bevbuddy_url

    url = bevbuddy_url + f'/{id_nutritions}'
    print(url)
    headers = {
        'accept': 'application/json',
    }

    response = requests.get(url, headers=headers, timeout=10)
    return response.json()

# Get Recommendation History
@app.get("/integrasi-get-recommendation", tags=["Integrasi: Layanan Beverage Buddy"])
async def integrasi_get_recommendation(token: str = Depends(oauth2_scheme)):
    # login_headers = {
    #     'accept': 'application/json',
    # }
    global bevbuddy_url

    login_url = bevbuddy_url + 'login'
    login_data_string = {
        'username': 'hilmi',
        'password': 'string',
    }

    login_data_json=json.dumps(login_data_string)
    login_response = requests.post(login_url, login_data_json)

    if login_response.status_code == 200:
        # Successful login, return the token
        token = login_response.json().get("token")
        print(token)
    else:
        print("tes")
        # Handle unsuccessful login (you might want to raise an exception or handle it differently)
        login_response.raise_for_status()
        print(login_response.text)

    url = bevbuddy_url + 'recommendations'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + token,
    }

    response = requests.get(url, headers=headers, timeout=10)
    return response.json()

# Create Recommendation
@app.post("/integrasi-create-recommendation", tags=["Integrasi: Layanan Beverage Buddy"])
async def integrasi_detail_me(req: RecommendationReq, current_user: Annotated[User, Depends(get_current_active_user)]):
    global saved_password

    login_url = bevbuddy_url + 'login'
    login_data_string = {
        'username': current_user.username,
        'password': saved_password,
    }

    login_data_json=json.dumps(login_data_string)
    login_response = requests.post(login_url, login_data_json)

    if login_response.status_code == 200:
        # Successful login, return the token
        token = login_response.json().get("token")
        print(token)
    else:
        # Handle unsuccessful login (you might want to raise an exception or handle it differently)
        login_response.raise_for_status()

    url = bevbuddy_url + 'recommendations'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + token,
    }

    body = {
        "activity": req.activity,
        "age": req.age,
        "gender": req.gender,
        "height": req.height,
        "max_rec": req.max_rec,
        "mood": req.mood,
        "weather": req.weather,
        "weight": req.weight
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    return response.json()