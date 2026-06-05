"""DIEF-MO Encoder - Streamlit interface.

Run with:  streamlit run app.py
"""
import io

import pandas as pd
import streamlit as st

from dief_mo import db
from dief_mo.encoder import decode_id

st.set_page_config(page_title="DIEF-MO Encoder", page_icon="🔬", layout="wide")
db.init_db()

st.sidebar.title("🔬 DIEF-MO")
page = st.sidebar.radio(
    "Navigation",
    ["Registration", "Generate ID", "Batch import", "History"],
)

# ----------------------------------------------------------------- Registration
if page == "Registration":
    st.header("Registration")
    tab_area, tab_matrix, tab_exp = st.tabs(["Areas", "Matrices", "Experiments"])

    with tab_area:
        with st.form("form_area", clear_on_submit=True):
            code = st.text_input("Area code (e.g. PRO)")
            name = st.text_input("Name")
            desc = st.text_input("Description", "")
            if st.form_submit_button("Save area") and code and name:
                db.add_area(code, name, desc)
                st.success(f"Area '{code}' saved.")
        st.dataframe(pd.DataFrame(db.list_table("areas")), use_container_width=True)

    with tab_matrix:
        with st.form("form_matrix", clear_on_submit=True):
            code = st.text_input("Matrix code (e.g. M001)")
            name = st.text_input("Name")
            mtype = st.text_input("Matrix type", "")
            if st.form_submit_button("Save matrix") and code and name:
                db.add_matrix(code, name, mtype)
                st.success(f"Matrix '{code}' saved.")
        st.dataframe(pd.DataFrame(db.list_table("matrices")), use_container_width=True)

    with tab_exp:
        with st.form("form_exp", clear_on_submit=True):
            code = st.text_input("Experiment code (e.g. E001)")
            name = st.text_input("Name")
            activity = st.selectbox("Activity type", ["EXP (experimental)", "LIT (literature)"])
            if st.form_submit_button("Save experiment") and code and name:
                db.add_experiment(code, name, activity.split()[0])
                st.success(f"Experiment '{code}' saved.")
        st.dataframe(pd.DataFrame(db.list_table("experiments")), use_container_width=True)

# ------------------------------------------------------------------ Generate ID
elif page == "Generate ID":
    st.header("Generate a DIEF-MO identifier")
    experiments = db.list_table("experiments")
    areas = db.list_table("areas")
    matrices = db.list_table("matrices")

    if not (experiments and areas and matrices):
        st.warning("Register at least one experiment, one area and one matrix first.")
    else:
        col1, col2, col3 = st.columns(3)
        exp = col1.selectbox("Experiment", [e["code"] for e in experiments])
        area = col2.selectbox("Area", [a["code"] for a in areas])
        matrix = col3.selectbox("Matrix", [m["code"] for m in matrices])
        if st.button("Generate ID"):
            dief_id = db.create_assay(exp, area, matrix)
            st.success(f"Generated ID: {dief_id}")
            st.json(decode_id(dief_id))

# --------------------------------------------------------------- Batch import
elif page == "Batch import":
    st.header("Batch import (Excel)")
    st.caption("The file must contain the columns: experiment_code, area_code, matrix_code")
    file = st.file_uploader("Upload an Excel file (.xlsx)", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        st.dataframe(df, use_container_width=True)
        required = ["experiment_code", "area_code", "matrix_code"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
        elif st.button("Generate IDs"):
            df["dief_id"] = [
                db.create_assay(r["experiment_code"], r["area_code"], r["matrix_code"])
                for _, r in df.iterrows()
            ]
            st.dataframe(df, use_container_width=True)
            buf = io.BytesIO()
            df.to_excel(buf, index=False)
            st.download_button(
                "Download result", buf.getvalue(), file_name="dief_output.xlsx"
            )

# -------------------------------------------------------------------- History
elif page == "History":
    st.header("Generated IDs history")
    assays = db.list_assays()
    if assays:
        st.dataframe(pd.DataFrame(assays), use_container_width=True)
    else:
        st.info("No IDs generated yet.")
