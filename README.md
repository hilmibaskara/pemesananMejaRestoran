# Reservation Microservice README

**Nama:** Hilmi Baskara Radanto\
**NIM:** [Your Student ID]

Microservice ini dikembangkan sebagai bagian dari pemenuhan tugas kuliah II3160 Teknologi Sistem Terintegrasi.

## Overview

Microservice ini dibangun menggunakan FastAPI dan memungkinkan pengguna untuk mengelola reservasi dan status meja di sebuah restoran. Microservice ini menyediakan berbagai endpoints untuk melakukan operasi terkait reservasi dan meja. Layanan ini memuat data dari file JSON yang memungkinkan pengguna dapat berinteraksi dengannya melalui permintaan HTTP.

## Endpoints

### Get All Reservations

- **Endpoint:** `/reservations`
- **HTTP Method:** GET
- **Description:** Dapatkan daftar semua reservasi yang ada.


### Get Reservation by ID

- **Endpoint:** `/reservations/{reservation_id}`
- **HTTP Method:** GET
- **Description:** Dapatkan detail reservasi berdasarkan ID uniknya.


### Create a New Reservation

- **Endpoint:** `/reservations`
- **HTTP Method:** POST
- **Description:** Buat reservasi baru dengan menyediakan nama pemesan, ID meja, jam mulai, dan durasi. Ini akan secara otomatis menghasilkan ID unik untuk reservasi.


### Get Table Status

- **Endpoint:** `/tables/{id_table}/status`
- **HTTP Method:** GET
- **Deskripsi:** Dapatkan status meja untuk ID meja tertentu dan jam mulai yang ditentukan.




### Update Reservation

- **Endpoint:** `/reservation/{id_reservation}`
- **HTTP Method:** PUT
- **Deskripsi:** Perbarui reservasi yang berdasarkan menentukan ID-nya. Pengguna dapat mengubah nama pemesan, ID meja, jam mulai, dan durasinya.


### Delete Reservation

- **Endpoint:** `/reservations/{id_reservation}`
- **HTTP Method:** DELETE
- **Deskripsi:** Hapus reservasi berdasarkan ID-nya.


### Add Tables

- **Endpoint:** `/tables`
- **HTTP Method:** POST
- **Deskripsi:** Menambah jumlah meja yang tersedia

### Reduce Tables

- **Endpoint:** `/tables`
- **HTTP Method:** DELETE
- **Deskripsi:** Mengurangi jumlah meja yang tersedia


## Usage

### Local
1. Clone repositori ini.

2. Buka terminal cmd sesuai dengan folder repositori

3. Ketik python -m venv [nama virtual environment] untuk membuka virtual environment

4. Akses ke virtual environment dengan cara ketik [nama virtual enviroment]\Scripts\activate

5. Install library FastAPI dan uvicorn dengan 
``
pip install fastapi uvicorn
``\
6. Jalankan server FastAPI dengan menggunakan `uvicorn meja:app --port 8000 --reload`.

7. Akses dokumentasi API pada IP localhost yang disediakan di terminal dengan port 8000

### Online

Akses langsung ke dokumentasi API pada
[http://20.198.196.252/docs](http://20.198.196.252/docs) untuk menguji endpoints dan memahami cara penggunaan microservice secara langsung.

## Data Files

Microservice ini memuat data dari file JSON yang bernama `tables.json` dan `reservations.json`. Pastikan untuk menjaga file-file ini dengan data yang valid.

## Notes

- Ensure that your Docker and network configurations are properly set up to avoid network issues when running the service in a container.

- This README is provided as a template. Replace the placeholders in square brackets with your actual information.

Feel free to customize this README according to your specific needs. It provides an overview of your microservice, describes its endpoints, explains how to use it, and highlights important considerations.
