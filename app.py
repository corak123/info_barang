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
barang_keluar_sheet = sheet.worksheet("keluar")

# Form Input
st.header("Debug Append Row ke Sheet 'keluar'")

sj_id = st.text_input("Surat Jalan ID")
invoice_id = st.text_input("Invoice ID")
so = st.text_input("SO")
po = st.text_input("PO")
nama_barang = st.text_input("Nama Barang")
kode_barang = st.text_input("Kode Barang")
jumlah_keluar = st.number_input("Jumlah Keluar", min_value=1)
tgl_sj = st.date_input("Tanggal SJ")
keterangan = st.text_input("Keterangan")

if st.button("Coba Tambahkan ke Sheet 'keluar'"):
    # Ambil semua data invoice
    data = invoice_sheet.get_all_records()

    # Cek apakah data invoice dan kode barang cocok
    ditemukan = False
    for idx, row in enumerate(data):
        if row["invoice_id"] == invoice_id and str(row["kode_barang"]) == str(kode_barang):
            ditemukan = True
            try:
                sisa = int(row["sisa"])
                jumlah_keluar = int(jumlah_keluar)
            except ValueError:
                st.error("Format angka tidak valid.")
                break

            if jumlah_keluar > sisa:
                st.warning(f"Jumlah keluar melebihi sisa stok ({sisa})")
                break
            else:
                new_sisa = sisa - jumlah_keluar
                baris_di_sheet = idx + 2
                try:
                    invoice_sheet.update(f"E{baris_di_sheet}", [[new_sisa]])
                    st.info(f"Sisa berhasil diperbarui di baris {baris_di_sheet} menjadi {new_sisa}.")
                except Exception as e:
                    st.error(f"Gagal update kolom sisa: {e}")
                    break

                # Coba append row
                try:
                    barang_keluar_sheet.append_row([
                        sj_id, invoice_id, so, po, nama_barang, kode_barang,
                        jumlah_keluar, str(tgl_sj), keterangan
                    ])
                    st.success("Data berhasil ditambahkan ke sheet 'keluar'.")
                except Exception as e:
                    st.error(f"Gagal menambahkan ke sheet 'keluar': {e}")
                break

    if not ditemukan:
        st.warning("Data invoice dan kode barang tidak ditemukan.")
