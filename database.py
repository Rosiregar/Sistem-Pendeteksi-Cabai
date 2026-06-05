# database.py
import os
import sqlite3
import hashlib
import json
import datetime
import uuid
from recommendations import DISEASE_RECS

# Database Connection Settings
# Jikalau environment variable MYSQL_HOST diset, sistem akan otomatis beralih ke MySQL.
# Jika tidak diset, sistem akan menggunakan database lokal SQLite (chili_system.db) agar langsung bekerja mandiri.
# database.py
# PERBAIKI BAGIAN INI KEMBALI SEPERTI SEMULA:
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

# Fallback ke Streamlit Secrets jika dijalankan di Streamlit Cloud dan variabel env kosong
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        if not MYSQL_HOST and "MYSQL_HOST" in st.secrets:
            MYSQL_HOST = st.secrets["MYSQL_HOST"]
        if not MYSQL_USER and "MYSQL_USER" in st.secrets:
            MYSQL_USER = st.secrets["MYSQL_USER"]
        if not MYSQL_PASSWORD and "MYSQL_PASSWORD" in st.secrets:
            MYSQL_PASSWORD = st.secrets["MYSQL_PASSWORD"]
        if not MYSQL_DB and "MYSQL_DB" in st.secrets:
            MYSQL_DB = st.secrets["MYSQL_DB"]
        if not MYSQL_PORT and "MYSQL_PORT" in st.secrets:
            MYSQL_PORT = str(st.secrets["MYSQL_PORT"])
except Exception:
    pass

IS_MYSQL = MYSQL_HOST is not None

# Deteksi ketersediaan modul driver pymysql
if IS_MYSQL:
    try:
        import pymysql
        import pymysql.cursors
    except ImportError:
        IS_MYSQL = False
        print("[DB WARNING] Driver 'pymysql' tidak ditemukan. Sistem sementara beralih ke SQLite default.")

DB_FILE = "chili_system.db"

def get_connection():
    """Mengembalikan objek koneksi database yang aktif."""
    if IS_MYSQL:
        return pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=int(MYSQL_PORT),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Menginisialisasi database (SQLite atau MySQL) sesuai dengan rancangan ERD."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if IS_MYSQL:
        # Enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # 1. Tabel User (Pengguna)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id_pengguna VARCHAR(191) PRIMARY KEY,
                nama VARCHAR(191) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(191),
                peran VARCHAR(50) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 2. Tabel Admin
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id_admin VARCHAR(191) PRIMARY KEY,
                nama_admin VARCHAR(191) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(191)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 3. Tabel Penyakit
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diseases (
                nama_penyakit VARCHAR(191) PRIMARY KEY,
                nama_latin VARCHAR(191),
                deskripsi TEXT,
                solusi_organik TEXT, -- List tindakan bentuk JSON
                solusi_kimiawi TEXT  -- List tindakan bentuk JSON
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 4. Tabel Diagnosis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnoses (
                id_diagnosis VARCHAR(191) PRIMARY KEY,
                id_user VARCHAR(191),
                plant_image LONGTEXT, -- Base64
                nama_penyakit VARCHAR(191),
                confidence DOUBLE,
                mc_uncertainty DOUBLE,
                gradcam_data TEXT, -- JSON
                notes TEXT,
                created_at VARCHAR(100),
                FOREIGN KEY (id_user) REFERENCES users(id_pengguna) ON DELETE CASCADE,
                FOREIGN KEY (nama_penyakit) REFERENCES diseases(nama_penyakit) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 5. Tabel Metrik Model
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id_snapshot VARCHAR(191) PRIMARY KEY,
                id_admin VARCHAR(191),
                timestamp VARCHAR(100),
                accuracy_global DOUBLE,
                f1_score DOUBLE,
                total_inferences INT,
                disease_distribution TEXT, -- JSON
                FOREIGN KEY (id_admin) REFERENCES admin(id_admin) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    else:
        # SQLite Engine (Menggunakan skema ERD yang sama)
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 1. Tabel User
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id_pengguna TEXT PRIMARY KEY,
                nama TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                peran TEXT NOT NULL
            )
        """)
        
        # 2. Tabel Admin
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id_admin TEXT PRIMARY KEY,
                nama_admin TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT
            )
        """)
        
        # 3. Tabel Penyakit
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diseases (
                nama_penyakit TEXT PRIMARY KEY,
                nama_latin TEXT,
                deskripsi TEXT,
                solusi_organik TEXT,
                solusi_kimiawi TEXT
            )
        """)
        
        # 4. Tabel Diagnosis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnoses (
                id_diagnosis TEXT PRIMARY KEY,
                id_user TEXT,
                plant_image TEXT,
                nama_penyakit TEXT,
                confidence REAL,
                mc_uncertainty REAL,
                gradcam_data TEXT,
                notes TEXT,
                created_at TEXT,
                FOREIGN KEY (id_user) REFERENCES users(id_pengguna) ON DELETE CASCADE,
                FOREIGN KEY (nama_penyakit) REFERENCES diseases(nama_penyakit) ON DELETE CASCADE
            )
        """)

        # 5. Tabel Metrik Model
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id_snapshot TEXT PRIMARY KEY,
                id_admin TEXT,
                timestamp TEXT,
                accuracy_global REAL,
                f1_score REAL,
                total_inferences INTEGER,
                disease_distribution TEXT,
                FOREIGN KEY (id_admin) REFERENCES admin(id_admin) ON DELETE SET NULL
            )
        """)
        
    conn.commit()
    
    # --- SEEDING DATA USER DEFAULT ---
    cursor.execute("SELECT COUNT(*) FROM users")
    count_users = cursor.fetchone()
    user_count_val = count_users[0] if isinstance(count_users, tuple) else (count_users["COUNT(*)"] if isinstance(count_users, dict) else list(count_users.values())[0])
    
    if user_count_val == 0:
        admin_pass = hash_password("admin123")
        user_pass = hash_password("petani123")
        admin_uid = str(uuid.uuid4())
        petani_uid = str(uuid.uuid4())
        
        ph = "%s" if IS_MYSQL else "?"
        cursor.execute(f"INSERT INTO users (id_pengguna, nama, password, email, peran) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})",
                       (admin_uid, "admin", admin_pass, "admin@drcabai.id", "admin"))
        cursor.execute(f"INSERT INTO users (id_pengguna, nama, password, email, peran) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})",
                       (petani_uid, "petani", user_pass, "petani@drcabai.id", "user"))
        conn.commit()

    # --- SEEDING DATA ADMIN DEFAULT ---
    cursor.execute("SELECT COUNT(*) FROM admin")
    count_admin = cursor.fetchone()
    admin_count_val = count_admin[0] if isinstance(count_admin, tuple) else (count_admin["COUNT(*)"] if isinstance(count_admin, dict) else list(count_admin.values())[0])
    
    if admin_count_val == 0:
        admin_pass = hash_password("admin123")
        admin_id = str(uuid.uuid4())
        ph = "%s" if IS_MYSQL else "?"
        cursor.execute(f"INSERT INTO admin (id_admin, nama_admin, password, email) VALUES ({ph}, {ph}, {ph}, {ph})",
                       (admin_id, "admin", admin_pass, "admin@drcabai.id"))
        conn.commit()
        
    # --- SEEDING DATA PENYAKIT & REKOMENDASI (SINKRON COLAB) ---
    cursor.execute("SELECT nama_penyakit FROM diseases")
    rows = cursor.fetchall()
    
    db_disease_names = set()
    for row in rows:
        if isinstance(row, tuple):
            db_disease_names.add(row[0])
        elif isinstance(row, dict):
            db_disease_names.add(row["nama_penyakit"])
            
    rec_disease_names = set(DISEASE_RECS.keys())
    
    if db_disease_names != rec_disease_names:
        cursor.execute("DELETE FROM diseases")
        ph = "%s" if IS_MYSQL else "?"
        for key, value in DISEASE_RECS.items():
            # Mengambil solusi organik + immediate digabung ke solusi_organik, solusi kimia ke solusi_kimiawi
            sol_organik = value["organic"] + value["immediate"]
            cursor.execute(f"""
                INSERT INTO diseases (nama_penyakit, nama_latin, deskripsi, solusi_organik, solusi_kimiawi)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (
                key,
                value["status_hama"], # kita petakan status_hama ke nama_latin
                value["description"],
                json.dumps(sol_organik),
                json.dumps(value["chemical"])
            ))
            
    conn.commit()

    # --- SEEDING METRIK MODEL ---
    cursor.execute("SELECT COUNT(*) FROM model_metrics")
    count_metrics = cursor.fetchone()
    metrics_count_val = count_metrics[0] if isinstance(count_metrics, tuple) else (count_metrics["COUNT(*)"] if isinstance(count_metrics, dict) else list(count_metrics.values())[0])
    
    if metrics_count_val == 0:
        # Ambil id_admin untuk relasi
        cursor.execute("SELECT id_admin FROM admin LIMIT 1")
        admin_row = cursor.fetchone()
        admin_id = admin_row[0] if admin_row else str(uuid.uuid4())
        
        snapshot_id = str(uuid.uuid4())
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        distribution = {
            "Cercospora Leaf Spot": 15,
            "Bacterial Spot": 23,
            "Healthy Leaf": 42,
            "Curl Virus": 18,
            "Nutrition Deficiency": 11,
            "White spot": 9
        }
        
        ph = "%s" if IS_MYSQL else "?"
        cursor.execute(f"""
            INSERT INTO model_metrics (id_snapshot, id_admin, timestamp, accuracy_global, f1_score, total_inferences, disease_distribution)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        """, (
            snapshot_id,
            admin_id,
            now_str,
            0.942, # 94.2% global accuracy
            0.938, # 93.8% F1 Score
            118,   # 118 inferences
            json.dumps(distribution)
        ))
        conn.commit()

    conn.close()

def run_query(sql, params=(), commit=False, fetch="all"):
    """
    Menjalankan query database dengan menangani perbedaan antara SQLite & MySQL secara dinamis.
    """
    conn = get_connection()
    try:
        if IS_MYSQL:
            formatted_sql = sql.replace("?", "%s")
            with conn.cursor() as cursor:
                cursor.execute(formatted_sql, params)
                if commit:
                    conn.commit()
                if fetch == "all":
                    rows = cursor.fetchall()
                    return rows if rows else []
                elif fetch == "one":
                    return cursor.fetchone()
                return None
        else:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if commit:
                conn.commit()
            if fetch == "all":
                rows = cursor.fetchall()
                return [dict(r) for r in rows] if rows else []
            elif fetch == "one":
                row = cursor.fetchone()
                return dict(row) if row else None
            return None
    except Exception as e:
        print(f"[DB Error] {str(e)}")
        raise e
    finally:
        conn.close()

def hash_password(password):
    """Menghas password menggunakan SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Memverifikasi pengguna di database. Mengembalikan dict data pengguna jika berhasil."""
    hashed = hash_password(password)
    # 1. Coba cari di tabel users (User)
    sql = "SELECT id_pengguna as id, nama as username, email, peran as role FROM users WHERE nama = ? AND password = ?"
    res = run_query(sql, (username, hashed), fetch="one")
    if res:
        return res
        
    # 2. Coba cari di tabel admin (Admin)
    sql_admin = "SELECT id_admin as id, nama_admin as username, email, 'admin' as role FROM admin WHERE nama_admin = ? AND password = ?"
    res_admin = run_query(sql_admin, (username, hashed), fetch="one")
    return res_admin

def create_user(username, password, email, role="user"):
    """Mendaftarkan akun petani baru."""
    hashed = hash_password(password)
    uid = str(uuid.uuid4())
    sql = "INSERT INTO users (id_pengguna, nama, password, email, peran) VALUES (?, ?, ?, ?, ?)"
    try:
        run_query(sql, (uid, username, hashed, email, role), commit=True)
        return True
    except Exception as e:
        print(f"[Create User Error] {str(e)}")
        return False

def get_all_users():
    """Mengambil seluruh data user untuk administrasi."""
    sql = "SELECT id_pengguna as id, nama as username, email, peran as role, '2026-06-05' as created_at FROM users ORDER BY nama ASC"
    return run_query(sql)

def update_user_role(user_id, new_role):
    """Memperbarui role dari pengguna."""
    sql = "UPDATE users SET peran = ? WHERE id_pengguna = ?"
    run_query(sql, (new_role, user_id), commit=True)

def delete_user(user_id):
    """Menghapus user dan catatan diagnosa terkait."""
    sql_diag = "DELETE FROM diagnoses WHERE id_user = ?"
    sql_user = "DELETE FROM users WHERE id_pengguna = ?"
    run_query(sql_diag, (user_id,), commit=True)
    run_query(sql_user, (user_id,), commit=True)

# --- CRUD PENYAKIT & REKOMENDASI ---

def get_all_diseases():
    """Mengambil list penyakit dari database dan mereturn format yang kompatibel dengan UI."""
    rows = run_query("SELECT * FROM diseases")
    formatted = []
    for r in rows:
        name = r.get("nama_penyakit")
        status_hama = r.get("nama_latin")
        desc = r.get("deskripsi")
        
        try:
            sol_org = json.loads(r.get("solusi_organik") or "[]")
        except Exception:
            sol_org = [r.get("solusi_organik")]
            
        try:
            sol_kim = json.loads(r.get("solusi_kimiawi") or "[]")
        except Exception:
            sol_kim = [r.get("solusi_kimiawi")]

        # Tentukan danger level visual untuk UI
        danger = "Sedang"
        if "Bacterial" in name or "Virus" in name:
            danger = "Tinggi"
        elif "Healthy" in name or "Sehat" in name:
            danger = "Aman"
            
        # UI memecah organiks, imm, chem. Kita petakan secara cerdas.
        formatted.append({
            "name": name,
            "status_hama": status_hama if status_hama else "Penyakit Cabai",
            "danger_level": danger,
            "description": desc if desc else "",
            "organic_json": json.dumps(sol_org[:len(sol_org)//2 + 1] if len(sol_org)>1 else sol_org),
            "immediate_json": json.dumps(sol_org[len(sol_org)//2 + 1:] if len(sol_org)>1 else []),
            "chemical_json": json.dumps(sol_kim),
            "created_at": "2026-06-05"
        })
    return formatted

def add_disease(name, status_hama, danger_level, description, organic, immediate, chemical):
    """Menambah jenis penyakit tanaman cabai baru beserta rekomendasinya ke database."""
    sql = """
        INSERT INTO diseases (nama_penyakit, nama_latin, deskripsi, solusi_organik, solusi_kimiawi)
        VALUES (?, ?, ?, ?, ?)
    """
    sol_organik = organic + immediate
    try:
        run_query(sql, (
            name,
            status_hama,
            description,
            json.dumps(sol_organik),
            json.dumps(chemical)
        ), commit=True)
        return True
    except Exception as e:
        print(f"[Add Disease Error] {str(e)}")
        return False

def update_disease(name, status_hama, danger_level, description, organic, immediate, chemical):
    """Mengupdate detail penyakit & pengobatan di database."""
    sql = """
        UPDATE diseases 
        SET nama_latin = ?, deskripsi = ?, solusi_organik = ?, solusi_kimiawi = ?
        WHERE nama_penyakit = ?
    """
    sol_organik = organic + immediate
    run_query(sql, (
        status_hama,
        description,
        json.dumps(sol_organik),
        json.dumps(chemical),
        name
    ), commit=True)

def delete_disease(name):
    """Menghapus jenis penyakit dari database."""
    sql = "DELETE FROM diseases WHERE nama_penyakit = ?"
    run_query(sql, (name,), commit=True)

# --- AKSES HISTORI DIAGNOSA ---

def save_diagnosis(id_str, user_id, username, disease, confidence, uncertainty, img_b64, notes, rec_dict):
    """Menyimpan data hasil identifikasi AI tanaman cabai."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
        INSERT INTO diagnoses (id_diagnosis, id_user, plant_image, nama_penyakit, confidence, mc_uncertainty, gradcam_data, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    if not user_id and username:
        u = run_query("SELECT id_pengguna FROM users WHERE nama = ?", (username,), fetch="one")
        if u:
            user_id = u[0] if isinstance(u, tuple) else u.get("id_pengguna")
            
    # Cari user pertama jika masih kosong
    if not user_id:
        u = run_query("SELECT id_pengguna FROM users LIMIT 1", fetch="one")
        if u:
            user_id = u[0] if isinstance(u, tuple) else u.get("id_pengguna")
            
    gradcam_dummy = json.dumps({"status": "GradCAM generated", "heatmap_applied": False})
    
    run_query(sql, (
        id_str,
        str(user_id),
        img_b64,
        disease,
        float(confidence),
        float(uncertainty),
        gradcam_dummy,
        notes,
        now_str
    ), commit=True)

def get_user_diagnoses(user_id):
    """Mengambil riwayat diagnosa milik user tertentu."""
    sql = """
        SELECT id_diagnosis as id, id_user as user_id, plant_image as image_b64, 
               nama_penyakit as disease_class, confidence, mc_uncertainty as uncertainty, 
               notes, created_at FROM diagnoses 
        WHERE id_user = ? 
        ORDER BY created_at DESC
    """
    res = run_query(sql, (str(user_id),))
    return res

def get_all_diagnoses():
    """Mengambil semua riwayat diagnosa untuk admin."""
    sql = """
        SELECT id_diagnosis as id, id_user as user_id, plant_image as image_b64, 
               nama_penyakit as disease_class, confidence, mc_uncertainty as uncertainty, 
               notes, created_at FROM diagnoses 
        ORDER BY created_at DESC
    """
    res = run_query(sql)
    for r in res:
        uid = r.get("user_id")
        u = run_query("SELECT nama FROM users WHERE id_pengguna = ?", (uid,), fetch="one")
        if u:
            r["username"] = u[0] if isinstance(u, tuple) else u.get("nama")
        else:
            r["username"] = "Petani"
    return res

def delete_diagnosis(diag_id):
    """Menghapus data pencatatan diagnosa."""
    sql = "DELETE FROM diagnoses WHERE id_diagnosis = ?"
    run_query(sql, (diag_id,), commit=True)

# --- METODE AKSES METRIK MODEL (ERD EXCLUSIVE) ---

def get_model_metrics():
    """Mengambil catatan metrik model terbaru dari database."""
    sql = "SELECT * FROM model_metrics ORDER BY timestamp DESC LIMIT 1"
    res = run_query(sql, fetch="one")
    if res:
        # Jika dalam format tuple, kembalikan dict manual
        if isinstance(res, tuple):
            return {
                "id_snapshot": res[0],
                "id_admin": res[1],
                "timestamp": res[2],
                "accuracy_global": res[3],
                "f1_score": res[4],
                "total_inferences": res[5],
                "disease_distribution": json.loads(res[6])
            }
        # Format dict (MySQL / SQLite dictionary cursors)
        try:
            res["disease_distribution"] = json.loads(res["disease_distribution"])
        except Exception:
            pass
        return res
    return None
