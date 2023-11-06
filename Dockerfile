FROM python:3

ADD meja.py .

COPY . /pemesananMejaRestoran
WORKDIR /pemesananMejaRestoran
RUN pip install fastapi uvicorn
CMD ["uvicorn", "meja:app", "--host=0.0.0.0", "--port=80"]