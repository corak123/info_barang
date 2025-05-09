import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Ambil credentials dari st.secrets
secrets = st.secrets["google_service_account"]

# Buat credentials object
creds = Credentials.from_service_account_info(secrets, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

# Inisialisasi client
client = gspread.authorize(creds)

# Buka spreadsheet
SPREADSHEET_NAME = "stock_gudang"
sheet = client.open(SPREADSHEET_NAME)
invoice_sheet = sheet.worksheet("invoice")
barang_keluar_sheet = sheet.worksheet("keluar")

def get_barang_dari_invoice(invoice_id):
    data = invoice_sheet.get_all_records()
    return [
        row for row in data
        if row["invoice_id"].strip().lower() == invoice_id.strip().lower() and int(row["sisa"]) > 0
    ]
    st.write("DEBUG - invoice_id:", invoice_id)
    st.write("DEBUG - Barang ditemukan:", barang_list)


def invoice_sudah_ada(invoice_id, kode_barang):
    data = invoice_sheet.get_all_records()
    return any(row["invoice_id"] == invoice_id and row["kode_barang"] == kode_barang for row in data)


def tambah_barang_masuk(invoice_id, nama_barang, kode_barang, jumlah, tanggal, keterangan):
    try:
        invoice_sheet = sheet.worksheet("invoice")
        row = [
            invoice_id,
            nama_barang,
            kode_barang,
            jumlah,
            jumlah,  # sisa = jumlah saat pertama kali masuk
            tanggal,
            keterangan
        ]
        invoice_sheet.append_row(row)
        return f"Barang {nama_barang} berhasil ditambahkan ke invoice {invoice_id}."
    except Exception as e:
        return f"Gagal menambahkan barang: {e}"

def tambah_barang_keluar_validated(sj_id, invoice_id, so, po, nama_barang, kode_barang, jumlah_keluar, tgl_sj, keterangan):
    data = invoice_sheet.get_all_records()

    for idx, row in enumerate(data):
        if row["invoice_id"] == invoice_id and row["kode_barang"] == kode_barang:
            sisa = int(row["sisa"])
            if jumlah_keluar > sisa:
                return f"Jumlah keluar melebihi sisa stok ({sisa})"
            else:
                # Kurangi sisa di invoice
                invoice_sheet.update_cell(idx+2, 5, sisa - jumlah_keluar)  # Kolom E = sisa
                # Tambahkan data ke sheet barang_keluar
                barang_keluar_sheet.append_row([
                    sj_id, invoice_id, so, po, nama_barang, kode_barang,
                    jumlah_keluar, tgl_sj, keterangan
                ])
                return "Barang berhasil dikeluarkan."

    return "Data invoice atau kode barang tidak ditemukan."
