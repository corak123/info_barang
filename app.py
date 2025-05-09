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
        elif invoice_sudah_ada(invoice_id):
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


# Form input barang keluar
with st.form("form_barang_keluar"):
    st.subheader("Barang Keluar (Dari Invoice yang Ada)")

    invoice_id = st.text_input("Masukkan Nomor Invoice (Barang Masuk)")

    barang_list = []
    selected = None

    if invoice_id.strip():
        barang_list = get_barang_dari_invoice(invoice_id)

    if barang_list:
        barang_nama_list = [f'{b["nama_barang"]} ({b["kode_barang"]}) - sisa: {b["sisa"]}' for b in barang_list]
        pilihan_barang = st.selectbox("Pilih Barang", barang_nama_list)
        selected = barang_list[barang_nama_list.index(pilihan_barang)]
        jumlah_keluar = st.number_input("Jumlah Keluar", min_value=1, max_value=int(selected["sisa"]))
    else:
        #st.warning("Tidak ada barang dari invoice ini atau semua barang sudah habis.")
        jumlah_keluar = 0  # Default saja

    sj_id = st.text_input("Nomor Surat Jalan")
    so = st.text_input("SO")
    po = st.text_input("PO")
    tgl_sj = st.date_input("Tanggal SJ")
    keterangan = st.text_area("Keterangan")

    submitted = st.form_submit_button("Keluarkan Barang")

    if submitted:
        if not invoice_id.strip() or not selected:
            st.error("Invoice tidak valid atau tidak ada barang tersisa.")
        elif jumlah_keluar <= 0:
            st.error("Jumlah keluar harus lebih dari 0.")
        else:
            hasil = tambah_barang_keluar_validated(
                sj_id=sj_id,
                invoice_id=invoice_id,
                so=so,
                po=po,
                nama_barang=selected["nama_barang"],
                kode_barang=selected["kode_barang"],
                jumlah_keluar=int(jumlah_keluar),
                tgl_sj=str(tgl_sj),
                keterangan=keterangan
            )
            if "berhasil" in hasil.lower():
                st.success("Barang berhasil dikeluarkan.")
            else:
                st.error(hasil)


