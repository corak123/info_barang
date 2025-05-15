import streamlit as st
from sheets_helper import get_barang_dari_invoice, tambah_barang_keluar_validated, tambah_barang_masuk, invoice_sudah_ada

st.title("📦 Info Barang")

# --- Form Tambah Barang Masuk ---
with st.form("form_barang_masuk"):
    st.subheader("Tambah Barang Masuk (Invoice Baru)")

    invoice_id_masuk = st.text_input("Nomor Invoice (Barang Masuk)")
    nama_barang = st.text_input("Nama Barang")
    kode_barang = st.text_input("Kode Barang")
    jumlah = st.number_input("Jumlah Masuk", min_value=1)
    tanggal = st.date_input("Tanggal Masuk")
    keterangan = st.text_area("Keterangan")

    submitted = st.form_submit_button("Tambah Barang Masuk")

    if submitted:
        if not invoice_id_masuk.strip() or not nama_barang.strip() or not kode_barang.strip():
            st.error("Nomor Invoice, Nama Barang, dan Kode Barang wajib diisi.")
        elif invoice_sudah_ada(invoice_id_masuk, kode_barang):
            st.error("Nomor Invoice sudah digunakan. Gunakan invoice yang berbeda.")
        else:
            hasil = tambah_barang_masuk(
                invoice_id=invoice_id_masuk,
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

# Inisialisasi session state jika belum ada
if "barang_list" not in st.session_state:
    st.session_state.barang_list = []
if "invoice_id" not in st.session_state:
    st.session_state.invoice_id = ""

# Proses setelah klik tombol "Cek Invoice"
if cek_ditekan and invoice_id:
    with st.spinner("Mengecek invoice..."):
        barang_list = get_barang_dari_invoice(invoice_id)

    if not barang_list:
        st.session_state.barang_list = []
        st.error("Invoice tidak ditemukan atau tidak ada barang tersedia.")
    else:
        st.session_state.barang_list = barang_list
        st.session_state.invoice_id = invoice_id
        st.success("Invoice valid, silakan isi form barang keluar.")

# --- Form 2: Barang Keluar (Hanya muncul jika barang_list tidak kosong) ---
barang_list = st.session_state.barang_list
invoice_id = st.session_state.invoice_id

if barang_list:
    with st.form("form_barang_keluar"):
        pilihan = [
            f'{b["nama_barang"]} ({b["kode_barang"]}) - sisa: {b["sisa"]}'
            for b in barang_list
        ]
        pilihan_barang = st.selectbox("Pilih Barang yang Ingin Dikeluarkan", pilihan)

        # Inisialisasi selected berdasarkan pilihan
        try:
            selected = barang_list[pilihan.index(pilihan_barang)]
        except (ValueError, IndexError):
            selected = None

        jumlah_keluar = st.number_input(
            "Jumlah Barang Keluar",
            min_value=1, step=1
        )

        sj_id = st.text_input("Nomor Surat Jalan")
        so = st.text_input("SO")
        po = st.text_input("PO")
        tgl_sj = st.date_input("Tanggal Surat Jalan")
        keterangan = st.text_area("Keterangan")

        submitted = st.form_submit_button("Keluarkan Barang")

        if submitted:
            if not invoice_id or not selected:
                st.error("Invoice tidak valid atau barang tidak dipilih.")
                st.stop()
            elif jumlah_keluar <= 0:
                st.error("Jumlah keluar harus lebih dari 0.")
                st.stop()
            elif jumlah_keluar > int(selected["sisa"]):
                st.error(f"Jumlah keluar melebihi sisa stok ({selected['sisa']}).")
                st.stop()
            else:
                with st.spinner("Memproses pengeluaran barang..."):
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
                        st.success("Barang berhasil dikeluarkan dan sisa di-invoice diperbarui.")
                    else:
                        st.error(hasil)

