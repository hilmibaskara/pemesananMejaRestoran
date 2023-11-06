from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

# Load the existing JSON data
with open("tables.json", "r") as read_file:
    data_tables = json.load(read_file)

with open("reservations.json", "r") as read_file:
    data_reservations = json.load(read_file)

app = FastAPI()

class Reservation(BaseModel):
    id_reservation: int
    reserver_name: str
    id_table: int
    hourstart: int
    duration: int

# Pydantic model for Table
class Table(BaseModel):
    id_table: int
    hourstart: int
    status: bool

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
                    
# Get all reservation data
@app.get('/reservations')
async def get_reservations():
    return data_tables["tables"]

# Get reservation data by ID
@app.get('/reservations/{reservation_id}')
async def get_reservation(reservation_id: int):
    found = False
    for reservation in data_reservations.get('reservations', []):
        if reservation['id_reservation'] == reservation_id:
            found = True
            return reservation
    if not found:
        raise HTTPException(status_code=404, detail="Reservation not found")

# Make a new reservation
@app.post('/reservations')
async def create_reservation(reserver_name_input: str, id_table_input: int, hourstart_input: int, duration_input: int):
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
@app.get('/tables/{id_table}/status')
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
@app.put('/reservation/{id_reservation}')
def update_reservation(id_reservation_input: int, new_reserver_name: str, new_id_table: int, new_hourstart: int, new_duration: int):
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
@app.delete('/reservations/{id_reservation}')
def delete_reservation(id_reservation_input: int):
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
    

# Read reservation by Criteria
@app.get('/reservations/{id_reservation}')
def get_reservation(id_reservation: int):
    reservations = data_reservations["reservations"]
    reservation = next((r for r in reservations if r["id_reservation"] == id_reservation), None)
    if reservation:
        return reservation
    raise HTTPException(status_code=404, detail="Reservation not found")

@app.post('/tables')
def add_table():
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

@app.delete('/tables')
def reduce_table():
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