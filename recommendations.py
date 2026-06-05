# recommendations.py
# Default database seed for chili diseases and recommendations matching Colab training

DISEASE_RECS = {
    "Cercospora Leaf Spot": {
        "status_hama": "Penyakit Jamur (Cercospora capsici)",
        "danger_level": "Sedang",
        "description": "Terbentuk bercak bulat kecil berwarna cokelat dengan pusat abu-abu keputihan pada permukaan daun. Daun yang terinfeksi parah dapat menguning dan rontok sebelum waktunya, menghambat pertumbuhan tanaman.",
        "organic": [
            "Semprotkan ekstrak daun mimba atau air rebusan bawang putih secara rutin.",
            "Gunakan fungisida hayati berbasis agen pengendali Trichoderma harzianum."
        ],
        "immediate": [
            "Cabut dan musnahkan daun cabai yang menunjukkan gejala bercak agar spora tidak terbawa angin ke tanaman lain.",
            "Atur jarak tanam agar kelembaban mikro di sekitar kanopi daun tidak terlalu basah."
        ],
        "chemical": [
            "Semprotkan fungisida kontak berbahan aktif tembaga hidroksida atau mankozeb sesuai dosis anjuran ketika tingkat serangan melebihi ambang batas."
        ]
    },
    "Bacterial Spot": {
        "status_hama": "Penyakit Bakteri (Xanthomonas campestris)",
        "danger_level": "Tinggi",
        "description": "Bercak kecil basah berwarna cokelat gelap atau kehitaman dengan lingkaran kuning di sekelilingnya (halo). Penyakit berkembang pesat dalam kondisi cuaca hangat, basah, dan hujan deras berangin.",
        "organic": [
            "Aplikasi bakterisida nabati atau semprotan air rebusan daun sirih merah.",
            "Gunakan pupuk kalsium untuk mendongkrak ketahanan jaringan dinding sel daun."
        ],
        "immediate": [
            "Lakukan isolasi dengan memotong cabang terinfeksi dan jangan melakukan pemangkasan saat kondisi daun sedang basah (menghindari penularan bakteri melalui air).",
            "Hindari sistem penyiraman overhead (semprot atas) yang memicu cipratan bakteri."
        ],
        "chemical": [
            "Gunakan bakterisida berbahan aktif streptomisin sulfat atau tembaga oksi-klorida dengan penyemprotan halus merata."
        ]
    },
    "Healthy Leaf": {
        "status_hama": "Kondisi Sehat (Optimal)",
        "danger_level": "Aman",
        "description": "Helaian daun berwarna hijau segar homogen, tekstur kenyal (turgor optimal), pori stomata berfungsi normal, dan bebas dari bekas gigitan hama ataupun bercak patogen.",
        "organic": [
            "Pertahankan aplikasi biostimulan organik cair atau pupuk kandang matang berkala.",
            "Lakukan penyemprotan pelindung dengan agen hayati Bacillus subtilis sebagai imunisasi daun."
        ],
        "immediate": [
            "Lakukan pemantauan visual berkala minimal 2 hari sekali untuk deteksi dini gejala patogen.",
            "Pangkas daun tua paling bawah yang menyentuh tanah secara berkala."
        ],
        "chemical": [
            "Tidak diperlukan zat kimia sintetik (pestisida/fungisida). Pertahankan budidaya bebas residu kimia."
        ]
    },
    "Curl Virus": {
        "status_hama": "Infeksi Virus Keriting (Begomovirus)",
        "danger_level": "Tinggi",
        "description": "Helaian daun mengerut, melengkung ke atas, berkeriput, dan mengalami kerdil parah dengan warna menguning tidak merata. Penyakit ini disebarkan secara efisien oleh serangga vektor seperti kutu kebul (Bemisia tabaci).",
        "organic": [
            "Pasang perangkap lengket berwarna kuning (yellow sticky trap) di sela-sela bedengan untuk menjebak kutu kebul.",
            "Semprotkan pestisida nabati berbasis bawang putih atau ekstrak tembakau untuk menghalau serangga pembawa virus."
        ],
        "immediate": [
            "Segera cabut tanaman cabai yang menunjukkan gejala keriting kuning parah, bakar di luar area kebun untuk menekan inokulum virus.",
            "Bersihkan gulma di sekitar area lahan agar tidak menjadi sarang pengungsian kutu kebul."
        ],
        "chemical": [
            "Kendalikan populasi kutu kebul pembawa virus menggunakan insektisida sistemik berbahan aktif abamektin, imidakloprid, atau tiodikarb."
        ]
    },
    "Nutrition Deficiency": {
        "status_hama": "Kekurangan Unsur Hara",
        "danger_level": "Sedang",
        "description": "Daun menunjukkan pola klorosis (menguning di antara tulang daun atau di bagian tepi) atau nekrosis akibat kurangnya pasokan unsur hara makro (seperti Nitrogen, Fosfor, Kalium) maupun mikro (Magnesium, Besi, Seng) dalam media tanah.",
        "organic": [
            "Berikan pupuk organik cair (POC) tinggi nitrogen dari urine kelinci fermentasi atau pupuk kascing.",
            "Campurkan pupuk kandang matang kaya kalium dan fosfor alami ke daerah perakaran."
        ],
        "immediate": [
            "Cek tingkat keasaman (pH) tanah menggunakan pH meter; tanah yang terlalu asam memblokir penyerapan unsur nutrisi.",
            "Lakukan penggemburan tanah di sekitar tanaman agar aerasi perakaran pulih."
        ],
        "chemical": [
            "Berikan pupuk daun makro/mikro lengkap (seperti NPK daun, KNO3 merah, atau magnesium sulfat kristal) melalui semprotan daun untuk respon cepat."
        ]
    },
    "White spot": {
        "status_hama": "Penyakit Jamur (Embun Tepung / Oidiopsis capsici)",
        "danger_level": "Sedang",
        "description": "Muncul lapisan tepung putih seperti debu di permukaan atau sisi bawah daun, menyebabkan nekrotis kekuningan. Pada kondisi kering dengan angin kencang, spora menyebar dengan hebat.",
        "organic": [
            "Semprotkan larutan baking soda encer dicampur sedikit sabun organik cair sebagai agen antiseptik alami.",
            "Aplikasikan belerang halus organik secara hati-hati di bawah permukaan daun."
        ],
        "immediate": [
            "Pangkas segera bagian daun bawah yang tertutupi tepung putih tebal agar tidak menyebar ke daun bagian atas.",
            "Lakukan penyemprotan air di pagi hari untuk membilas spora kering."
        ],
        "chemical": [
            "Aplikasikan fungisida sistemik berbahan aktif propikonazol atau triadimefon jika tingkat penularan sudah tinggi."
        ]
    }
}
