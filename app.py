import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Ambil credentials dari st.secrets
secrets = st.secrets["google_service_account"]

# Setup credentials dan client
creds = Credentials.from_service_account_info(secrets, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(creds)

# Buka spreadsheet dan worksheet
SPREADSHEET_NAME = "stock_gudang"
sheet = client.open(SPREADSHEET_NAME)
invoice_sheet = sheet.worksheet("invoice")

# UI Input
baris = st.number_input("Masukkan baris yang ingin diubah (misal: 2)", min_value=2)
nilai_baru = st.number_input("Masukkan nilai baru untuk kolom 'sisa'", step=1)

if st.button("Coba Update Kolom 'sisa' di baris tersebut"):
    try:
        kolom_sisa = 5  # kolom ke-5 = kolom E
        sebelum = invoice_sheet.cell(baris, kolom_sisa).value
        st.write(f"Isi sebelum: {sebelum}")

        # Update pakai metode stabil
        invoice_sheet.update(f"E{baris}", [[nilai_baru]])

        sesudah = invoice_sheet.cell(baris, kolom_sisa).value
        st.success(f"Update berhasil. Isi sesudah: {sesudah}")

    except Exception as e:
        st.error(f"Gagal update: {e}")

