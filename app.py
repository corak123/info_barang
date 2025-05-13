import streamlit as st
from sheets_helper import get_barang_dari_invoice, tambah_barang_keluar_validated, tambah_barang_masuk, invoice_sudah_ada

st.title("📦 Info Barang")

with st.form("form_barang_masuk"):
    st.subheader("Tambah Barang Masuk (Invoice Baru)")

    invoice_id = st.text_input("Nomor Invoice")
    nama_barang = st.text_input("Nama Barang")
    kode_barang = st.text_input("Kode Barang")
    jumlah = st.number_input("Jumlah Masuk", min_value=1)
    tanggal = st.date_input("Tanggal Masuk")
    keterangan = st.text_area("Keterangan")

    submitted = st.form_submit_button("Tambah Barang Masuk")

    if submitted:
        if not invoice_id.strip() or not nama_barang.strip() or not kode_barang.strip():
            st.error("Nomor Invoice, Nama Barang, dan Kode Barang wajib diisi.")
        elif invoice_sudah_ada(invoice_id, kode_barang):
            st.error("Nomor Invoice sudah digunakan. Gunakan invoice yang berbeda.")
        else:
            hasil = tambah_barang_masuk(
                invoice_id=invoice_id,
                nama_barang=nama_barang,
                kode_barang=kode_barang,
                jumlah=jumlah,
                tanggal=str(tanggal),
                keterangan=keterangan
            )
            if "berhasil" in hasil.lower():
                st.success("Barang berhasil masuk.")
            else:
                st.error(hasil)


# --- Form 1: Cek Invoice ---
with st.form("form_cek_invoice"):
    invoice_id = st.text_input("Masukkan Nomor Invoice").strip()
    cek_ditekan = st.form_submit_button("Cek Invoice")

barang_list = []
selected = None

if cek_ditekan and invoice_id:
    barang_list = get_barang_dari_invoice(invoice_id)

    if not barang_list:
        st.error("Invoice tidak ditemukan atau tidak ada barang tersedia.")
    else:
        st.success("Invoice valid, silakan isi form barang keluar.")

