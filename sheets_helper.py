import gspread
from google.oauth2.service_account import Credentials

# Scope yang mencakup Sheets dan Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

# Auth client
client = gspread.authorize(creds)

# Open spreadsheet
SPREADSHEET_NAME = "stock_gudang"
sheet = client.open(SPREADSHEET_NAME)

# Akses worksheet
invoice_sheet = sheet.worksheet("invoice")
keluar_sheet = sheet.worksheet("keluar")

def get_barang_dari_invoice(invoice_id):
    rows = invoice_sheet.get_all_records()
    return [
        row for row in rows
        if row["invoice_id"] == invoice_id and int(row["sisa"]) > 0
    ]

def tambah_barang_keluar_validated(sj_id, invoice_id, so, po, nama_barang, kode_barang, jumlah_keluar, tgl_sj, keterangan):
    rows = invoice_sheet.get_all_records()
    for idx, row in enumerate(rows, start=2):  # header = row 1
        if row["invoice_id"] == invoice_id and row["kode_barang"] == kode_barang:
            sisa = int(row["sisa"])
            if jumlah_keluar > sisa:
                return "Jumlah keluar melebihi sisa stok!"

            # Update sisa di sheet
            invoice_sheet.update_cell(idx, 5, sisa - jumlah_keluar)

            # Tambahkan ke sheet keluar
            keluar_sheet.append_row([
                sj_id, invoice_id, so, po, nama_barang, kode_barang,
                jumlah_keluar, tgl_sj, keterangan
            ])
            return "Barang berhasil dikeluarkan."

    return "Data invoice tidak ditemukan."
