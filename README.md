# Restaurant Reservation Microservice README

**Nama:** Hilmi Baskara Radanto\
**NIM:** 18221072

Microservice ini dikembangkan sebagai bagian dari pemenuhan tugas kuliah II3160 Teknologi Sistem Terintegrasi.

## Overview

Microservice ini dibangun menggunakan FastAPI dan memungkinkan pengguna untuk mengelola reservasi dan status meja di sebuah restoran dan meminta rekomendasi minuman. Untuk penjelasan selengkapnya dapat mengakses dokumen berikut:

1. Main Report: [https://docs.google.com/document/d/1Hkj6aAAVn8k9mXvN1vbfRwmJCI90XHiNyBd1UiRO_N0/edit#heading=h.xyr06xfjs70h](https://docs.google.com/document/d/1Hkj6aAAVn8k9mXvN1vbfRwmJCI90XHiNyBd1UiRO_N0/edit)
2. API Documentation: [https://docs.google.com/document/d/17fzVj98Wo967b2hH2g6cnxuS655vKm3QZgjIiHM2NXM/edit](https://docs.google.com/document/d/17fzVj98Wo967b2hH2g6cnxuS655vKm3QZgjIiHM2NXM/edit)

Microservice ini merupakan hasil integrasi dari dua layanan, yaitu:

### Layanan Pemesanan meja restoran
Microservice ini merupakan layanan yang memungkinkan customer untuk melakukan reservasi meja restoran dan admin mengelola reservasi serta mengelola meja di suatu restoran. Untuk layanan lama pemesanan meja restoran dapat diakses melalui [http://40.119.238.184/docs](http://40.119.238.184/docs)

### Layanan BevBuddy: Rekomendasi minuman (oleh Fikri Naufal Hamdi 18221096)
Microservice ini dapat memberikan rekomendasi minuman dari suatu kafe atau restoran berdasarkan personalisasi pengguna, seperti berat dan tinggi badan, usia, gender, serta exercise level. Mood serta cuaca juga dapat memengaruhi hasil dari rekomendasi minuman. Oleh karena itu, dengan microservice rekomendasi minuman ini memungkinkan pengguna bisa mendapatkan rekomendasi minuman yang tepat dan sehat. Untuk layanan ini dapat diakses melalui: [https://bevbuddy--c3oinea.thankfulbush-47818fd3.southeastasia.azurecontainerapps.io/docs](https://bevbuddy--c3oinea.thankfulbush-47818fd3.southeastasia.azurecontainerapps.io/docs)

## Usage

### Local
1. Clone repository ini.

2. Buka terminal cmd sesuai dengan folder repositori

3. Ketik `python -m venv env` untuk membuka virtual environment

4. Akses ke virtual environment dengan cara ketik `env\Scripts\activate`

5. Install library FastAPI dan uvicorn dengan `pip install fastapi uvicorn`
6. Jalankan server FastAPI dengan menggunakan `uvicorn main:app --port 8000 --reload`.

7. Akses dokumentasi API pada IP localhost yang disediakan di terminal dengan port 8000

### Online

Akses langsung ke dokumentasi API pada
[http://20.237.14.92/docs](http://20.237.14.92/docs) untuk menguji endpoints dan memahami cara penggunaan microservice secara langsung.
