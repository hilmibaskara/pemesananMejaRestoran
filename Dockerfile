FROM python:3.11

ADD app.py .

COPY . /pemesananMejaRestoran
WORKDIR /pemesananMejaRestoran

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

EXPOSE 8080