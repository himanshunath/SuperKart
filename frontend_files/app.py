import os

import pandas as pd
import requests
import streamlit as st

# Backend address: container name on the shared Docker network (override with BACKEND_URL)
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="centered")
st.title("🛒 SuperKart Sales Forecast")
st.write("Forecast the revenue a product will generate in a given store.")

tab_single, tab_batch = st.tabs(["Single prediction", "Batch prediction"])

# ------------------------- Online (single) inference -------------------------
with tab_single:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_id_char = st.selectbox("Product category code", ["FD", "DR", "NC"],
                                       help="FD = food, DR = drinks, NC = non-consumables")
        product_type_category = st.selectbox("Product type category", ["Perishables", "Non Perishables"])
        sugar = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
    with col2:
        weight = st.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.1)
        mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=147.0, step=1.0)
        area = st.number_input("Allocated display area (ratio)", min_value=0.0, max_value=1.0,
                               value=0.056, step=0.001, format="%.3f")

    st.subheader("Store details")
    col3, col4 = st.columns(2)
    with col3:
        store_type = st.selectbox("Store type", ["Supermarket Type2", "Supermarket Type1",
                                                 "Departmental Store", "Food Mart"])
        store_size = st.selectbox("Store size", ["Medium", "High", "Small"])
    with col4:
        city_type = st.selectbox("City tier", ["Tier 2", "Tier 1", "Tier 3"])
        store_age = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)

    payload = {
        "Product_Weight": weight,
        "Product_Sugar_Content": sugar,
        "Product_Allocated_Area": area,
        "Product_MRP": mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": city_type,
        "Store_Type": store_type,
        "Product_Id_char": product_id_char,
        "Store_Age_Years": int(store_age),
        "Product_Type_Category": product_type_category,
    }

    if st.button("Predict sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted Sales"]
                st.success(f"Forecasted sales revenue: **{prediction:,.2f}**")
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

# ------------------------------ Batch inference ------------------------------
with tab_batch:
    st.write("Upload a CSV with the columns: Product_Weight, Product_Sugar_Content, "
             "Product_Allocated_Area, Product_MRP, Store_Size, Store_Location_City_Type, "
             "Store_Type, Product_Id_char, Store_Age_Years, Product_Type_Category.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.dataframe(batch_df.head())

        if st.button("Predict batch", type="primary"):
            try:
                uploaded_file.seek(0)
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                         files={"file": uploaded_file.getvalue()}, timeout=60)
                if response.status_code == 200:
                    preds = response.json()
                    batch_df["Predicted_Sales"] = [preds[str(i)] for i in range(len(batch_df))]
                    st.success(f"Predicted {len(batch_df)} rows. "
                               f"Total forecasted revenue: {batch_df['Predicted_Sales'].sum():,.2f}")
                    st.dataframe(batch_df)
                    st.download_button("Download predictions",
                                       batch_df.to_csv(index=False).encode("utf-8"),
                                       "superkart_predictions.csv", "text/csv")
                else:
                    st.error(f"API error {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
