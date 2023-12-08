FROM python:3

ADD meja.py .

COPY . /pemesananMejaRestoran
WORKDIR /pemesananMejaRestoran

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "meja:app", "--host=0.0.0.0", "--port=80"]