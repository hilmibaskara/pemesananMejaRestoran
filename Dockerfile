FROM python:3.11

ADD app.py .

COPY . /pemesananMejaRestoran
WORKDIR /pemesananMejaRestoran

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD [ "python", "main.py" ]