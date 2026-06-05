"""DIEF-MO Encoder - Streamlit interface.

Run with:  streamlit run app.py
"""
import io

import pandas as pd
import streamlit as st

from dief_mo import db, vocab
from dief_mo.encoder import decode_id, validate_code

st.set_page_config(page_title="DIEF-MO Encoder", page_icon="🔬", layout="wide")
db.init_db()

st.sidebar.title("🔬 DIEF-MO")
page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Registration", "Generate ID", "Batch import", "History"],
)


def _delete_control(table, label):
    """Small expander to delete a registered entry."""
    rows = db.list_table(table)
    if not rows:
        return
    with st.expander(f"Manage / delete {label}"):
        target = st.selectbox(
            f"Select a {label} to delete", [r["code"] for r in rows], key=f"del_{table}"
        )
        if st.button(f"Delete '{target}'", key=f"delbtn_{table}"):
            db.delete_row(table, target)
            st.rerun()


# ------------------------------------------------------------------- Overview
if page == "Overview":
    st.header("DIEF-MO — Overview")
    st.write(
        "Standardize, encode and trace multi-omics assays. Register your master "
        "data once, then generate stable identifiers in the format "
        "`EXPERIMENT_AREA_MATRIX_SEQ` (e.g. `E001_PRO_M001_001`)."
    )
    c = db.counts()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Areas", c["areas"])
    col2.metric("Matrices", c["matrices"])
    col3.metric("Experiments", c["experiments"])
    col4.metric("Generated IDs", c["assays"])
    if c["areas"] == 0 or c["matrices"] == 0 or c["experiments"] == 0:
        st.info("Start in **Registration** to add at least one area, matrix and experiment.")

# --------------------------------------------------------------- Registration
elif page == "Registration":
    st.header("Registration")
    tab_area, tab_matrix, tab_exp = st.tabs(["Areas", "Matrices", "Experiments"])

    # ----- Areas -----
    with tab_area:
        st.caption("Pick a suggested area or choose 'Custom...' to define your own.")
        options = [f"{code} — {name}" for code, name in vocab.SUGGESTED_AREAS.items()]
        choice = st.selectbox("Area", options + ["Custom..."], key="area_choice")
        if choice == "Custom...":
            code = st.text_input("Area code (letters/numbers only, e.g. PRO)", key="area_code")
            name = st.text_input("Name", key="area_name")
        else:
            code = choice.split(" — ")[0]
            name = choice.split(" — ", 1)[1]
            st.text_input("Area code", value=code, disabled=True)
            st.text_input("Name", value=name, disabled=True)
        desc = st.text_input("Description (optional)", key="area_desc")
        if st.button("Save area"):
            try:
                code = validate_code(code, "area code")
                if not name.strip():
                    raise ValueError("Name is required.")
                existed = db.code_exists("areas", code)
                db.add_area(code, name, desc)
                st.success(f"Area '{code}' {'updated' if existed else 'saved'}.")
            except ValueError as e:
                st.error(str(e))
        st.dataframe(pd.DataFrame(db.list_table("areas")), use_container_width=True)
        _delete_control("areas", "area")

    # ----- Matrices -----
    with tab_matrix:
        code = st.text_input("Matrix code (letters/numbers only, e.g. M001)", key="mx_code")
        name = st.text_input("Name", key="mx_name")
        mtype = st.selectbox("Matrix type", vocab.MATRIX_TYPES, key="mx_type")
        if mtype == "Other":
            mtype = st.text_input("Specify matrix type", key="mx_type_other")
        if st.button("Save matrix"):
            try:
                code = validate_code(code, "matrix code")
                if not name.strip():
                    raise ValueError("Name is required.")
                existed = db.code_exists("matrices", code)
                db.add_matrix(code, name, mtype)
                st.success(f"Matrix '{code}' {'updated' if existed else 'saved'}.")
            except ValueError as e:
                st.error(str(e))
        st.dataframe(pd.DataFrame(db.list_table("matrices")), use_container_width=True)
        _delete_control("matrices", "matrix")

    # ----- Experiments -----
    with tab_exp:
        code = st.text_input("Experiment code (letters/numbers only, e.g. E001)", key="ex_code")
        name = st.text_input("Name", key="ex_name")
        activity_label = st.selectbox(
            "Activity type",
            [f"{c} — {n}" for c, n in vocab.ACTIVITY_TYPES.items()],
            key="ex_activity",
        )
        activity = activity_label.split(" — ")[0]
        if st.button("Save experiment"):
            try:
                code = validate_code(code, "experiment code")
                if not name.strip():
                    raise ValueError("Name is required.")
                existed = db.code_exists("experiments", code)
                db.add_experiment(code, name, activity)
                st.success(f"Experiment '{code}' {'updated' if existed else 'saved'}.")
            except ValueError as e:
                st.error(str(e))
        st.dataframe(pd.DataFrame(db.list_table("experiments")), use_container_width=True)
        _delete_control("experiments", "experiment")

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
            results, errors = [], []
            for idx, r in df.iterrows():
                try:
                    results.append(
                        db.create_assay(r["experiment_code"], r["area_code"], r["matrix_code"])
                    )
                except ValueError as e:
                    results.append(None)
                    errors.append(f"Row {idx + 1}: {e}")
            df["dief_id"] = results
            st.dataframe(df, use_container_width=True)
            if errors:
                st.warning("Some rows could not be processed:\n\n" + "\n".join(errors))
            buf = io.BytesIO()
            df.to_excel(buf, index=False)
            st.download_button(
                "Download result", buf.getvalue(), file_name="dief_output.xlsx"
            )

# -------------------------------------------------------------------- History
elif page == "History":
    st.header("Generated IDs — full dataset")
    rows = db.enriched_assays()
    if not rows:
        st.info("No IDs generated yet.")
    else:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        st.caption("AI-ready export: one row per identifier with full metadata.")
        col1, col2 = st.columns(2)
        col1.download_button(
            "Download CSV", df.to_csv(index=False).encode("utf-8"),
            file_name="dief_dataset.csv", mime="text/csv",
        )
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        col2.download_button(
            "Download Excel", buf.getvalue(), file_name="dief_dataset.xlsx"
        )