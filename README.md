# 🛰️ Pharos Bot Auto Tx

Bot otomatis untuk melakukan transaksi di jaringan **Testnet Pharos**.
Mendukung fitur:

* **Wrap PHRS**
* **Swap antar token**
* **Transfer PHRS**
* **Simulasi LP Mint**

**Dibuat oleh:** Ajoika\_Feb @CTeam

---

## 📂 Struktur Project

* `pharos.py` – Main script bot transaksi.
* `.env` – Menyimpan kunci privat dan token JWT (jangan dibagikan!).
* `requirements.txt` – Daftar dependensi Python.
* `logs.txt` dan `tx_log.txt` – File log aktivitas transaksi.

---

## 💻 Persiapan Instalasi di Windows

Ikuti langkah-langkah berikut dengan teliti.

### 1️⃣ Siapkan Python

1. Unduh **Python 3.10 atau lebih baru** dari [python.org](https://www.python.org/downloads/).
2. Saat instalasi, **centang**:

   * *Add Python to PATH*
   * *Install pip*

Verifikasi instalasi:

```powershell
python --version
pip --version
```

---

### 2️⃣ Buat Folder Project

Misalnya:

```
C:\PharosBot
```

Salin semua file berikut ke dalam folder tersebut:

* `pharos.py`
* `.env`
* `requirements.txt`

---

### 3️⃣ Buat Virtual Environment (Opsional tetapi disarankan)

Buka **Command Prompt** dan jalankan:

```powershell
cd C:\PharosBot
python -m venv venv
```

Aktifkan environment:

```powershell
venv\Scripts\activate
```

Jika berhasil, prompt akan berubah menjadi `(venv)`.

---

### 4️⃣ Install Dependensi

Pastikan berada di folder project, lalu jalankan:

```powershell
pip install -r requirements.txt
```

Jika muncul error `Microsoft Visual C++ Build Tools`, instal dari:
[https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

---

## 🔑 Konfigurasi .env

Buka file `.env` dan isi sesuai data kamu:

```
PRIVATE_KEY_1=0xYourPrivateKeyHere
JWT=YourJWTTokenHere
```

**PERINGATAN:** Jangan pernah membagikan kunci privat kepada siapa pun!

---

## 🚀 Menjalankan Bot

Untuk memulai bot:

1. Aktifkan virtual environment (jika digunakan).
2. Jalankan perintah berikut:

```powershell
python pharos.py
```

Bot akan:

* Menampilkan antarmuka terminal interaktif.
* Menjalankan siklus transaksi secara otomatis.

---

## 🛑 Menghentikan Bot

Tekan tombol:

```
Q
```

di jendela terminal untuk menghentikan bot dengan aman.

---

## 📋 Log Aktivitas

* Semua transaksi dicatat otomatis di file `tx_log.txt`.
* Log ringkas dapat dilihat langsung di terminal saat bot berjalan.

---

## 🧩 Dependensi

Sudah didefinisikan di `requirements.txt`:

```
web3
requests
python-dotenv
random-user-agent
rich
```

---

## ⚠️ Disclaimer

* Proyek ini hanya untuk testing di **Testnet Pharos**.
* Jangan gunakan untuk transaksi mainnet.
* Penggunaan sepenuhnya menjadi tanggung jawab Anda.
* Selalu lindungi kunci privat Anda.

---

## ✨ Kredit

Dibuat oleh **Ajoika\_Feb @CTeam**.
Join DC : [Ajoika_Feb](https://discord.gg/KzVBHKf9ck)
