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

# def get_barang_dari_invoice(invoice_id):
#     hasil = []
#     data = invoice_sheet.get_all_records()
#     invoice_id = invoice_id.strip().lower()

#     for row in data:
#         if not isinstance(row, dict):
#             continue
#         if "invoice_id" not in row or "sisa" not in row:
#             continue

#         if str(row["invoice_id"]).strip().lower() == invoice_id:
#             try:
#                 if int(row["sisa"]) > 0:
#                     hasil.append(row)
#             except ValueError:
#                 continue

#     return hasil

def get_barang_dari_invoice(invoice_id):
    hasil = []
    data = invoice_sheet.get_all_records()
    invoice_id = invoice_id.strip().lower().lstrip("'")  # Hapus tanda kutip satu dari awal input

    for row in data:
        if not isinstance(row, dict):
            continue
        if "invoice_id" not in row or "sisa" not in row:
            continue

        # Hapus tanda kutip satu dari invoice_id di sheet
        row_invoice = str(row["invoice_id"]).strip().lower().lstrip("'")
        if row_invoice == invoice_id:
            try:
                if int(row["sisa"]) > 0:
                    hasil.append(row)
            except ValueError:
                continue

    return hasil


def invoice_sudah_ada(invoice_id, kode_barang):
    data = invoice_sheet.get_all_records()
    return any(
        row["invoice_id"] == invoice_id and row["kode_barang"] == kode_barang
        for row in data
    )

def update_invoice_status(invoice_id):
    records = invoice_sheet.get_all_records()
    for i, row in enumerate(records, start=2):  # mulai dari baris ke-2
        try:
            sisa = int(row["sisa"])
            status = "selesai" if sisa == 0 else "aktif"
            invoice_sheet.update_cell(i, 8, status)  # kolom ke-8 = kolom H = "status"
        except:
            pass  # biar aman kalau ada nilai kosong atau error


def tambah_barang_masuk(invoice_id, nama_barang, kode_barang, jumlah, tanggal, keterangan):
    try:
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

def tambah_barang_keluar_validated(
    sj_id, invoice_id, so, po, nama_barang, kode_barang,
    jumlah_keluar, tgl_sj, keterangan
):
    data = invoice_sheet.get_all_records()

    for idx, row in enumerate(data):
        if str(row["invoice_id"]).strip() == str(invoice_id).strip() and str(row["kode_barang"]).strip() == str(kode_barang).strip():
            try:
                sisa = int(row["sisa"]) if str(row["sisa"]).strip().isdigit() else 0
                jumlah_keluar = int(jumlah_keluar)
            except ValueError:
                return "Format angka tidak valid."

            if jumlah_keluar > sisa:
                return f"Jumlah keluar melebihi sisa stok ({sisa})"
            else:
                new_sisa = sisa - jumlah_keluar
                baris_di_sheet = idx + 2

                try:
                    invoice_sheet.update(f"E{baris_di_sheet}", [[new_sisa]])
                except Exception as e:
                    return f"Gagal update kolom sisa: {e}"

                try:
                    barang_keluar_sheet.append_row([
                        sj_id, invoice_id, so, po, nama_barang, kode_barang,
                        jumlah_keluar, str(tgl_sj), keterangan
                    ])
                except Exception as e:
                    return f"Update sisa berhasil, tapi gagal menambahkan ke sheet 'keluar': {e}"

                return f"Barang berhasil dikeluarkan. Sisa sekarang: {new_sisa}"

    return "Data barang tidak ditemukan di invoice."

