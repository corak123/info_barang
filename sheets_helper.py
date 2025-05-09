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
keluar_sheet = sheet.worksheet("keluar")

def get_barang_dari_invoice(invoice_id):
    rows = invoice_sheet.get_all_records()
    return [
        row for row in rows
        if row["invoice_id"] == invoice_id and int(row["sisa"]) > 0
    ]

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
    # Ambil sheet yang relevan
    keluar_sheet = sheet.worksheet("keluar")
    invoice_sheet = sheet.worksheet("invoice")

    # Proses pengurangan stok di sheet 'invoice'
    invoice_data = invoice_sheet.get_all_records()
    
    # Cari invoice berdasarkan ID
    invoice_row = None
    for row in invoice_data:
        if row['invoice_id'] == invoice_id:
            invoice_row = row
            break

    if not invoice_row:
        return "Invoice tidak ditemukan."

    # Cek apakah stok mencukupi
    if invoice_row['sisa'] < jumlah_keluar:
        return "Stok tidak mencukupi."

    # Kurangi stok di invoice
    updated_sisa = invoice_row['sisa'] - jumlah_keluar
    invoice_sheet.update_cell(invoice_row['row'], invoice_row['sisa_column_index'], updated_sisa)

    # Simpan data barang keluar ke sheet 'keluar'
    keluar_data = {
        "sj_id": sj_id,
        "invoice_id": invoice_id,
        "so": so,
        "po": po,
        "nama_barang": nama_barang,
        "kode_barang": kode_barang,
        "jumlah_keluar": jumlah_keluar,
        "tgl_sj": tgl_sj,
        "keterangan": keterangan
    }
    keluar_sheet.append_row(keluar_data.values())

    return f"Barang {nama_barang} ({kode_barang}) sebanyak {jumlah_keluar} berhasil dikeluarkan."

