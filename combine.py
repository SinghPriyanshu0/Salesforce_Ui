import streamlit as st
import pandas as pd
import requests
from Backend import get_connection
from snowflake.connector.errors import ProgrammingError

# -------------------- Styling --------------------
st.markdown("""
    <style>
    @font-face {
        font-family: 'Salesforce Sans';
        src: url('https://a.sfdcstatic.com/shared/fonts/sans/SalesforceSans-Regular.woff2') format('woff2');
    }
    * {
        font-family: 'Salesforce Sans', sans-serif !important;
    }
    html, body, .main {
        background-color: #f4f6f9;
        color: #2e2e2e;
    }
    h1, h2, h3 {
        color: #16325c;
        font-weight: 500;
    }
    .stTextInput>div>div>input,
    .stTextArea>div>textarea,
    .stSelectbox>div>div>div>div {
        background-color: #ffffff;
        border: 1px solid #d8dde6;
        border-radius: 4px;
        padding: 10px;
        color: #2e2e2e;
    }
    .stButton>button {
        background-color: #0070d2;
        color: white;
        font-weight: 500;
        padding: 10px 20px;
        border-radius: 4px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #005fb2;
    }
    .dataframe th, .dataframe td {
        border: 1px solid #d8dde6;
        padding: 10px;
        text-align: left;
    }
    .dataframe th {
        background-color: #f1f2f6;
        color: #16325c;
        font-weight: 600;
    }
    .dataframe tr:nth-child(even) {
        background-color: #f9fafc;
    }
    .dataframe tr:hover {
        background-color: #e3e8f3;
    }
.dataframe td {
    color: #2e2e2e;
    max-width: 200px;
    white-space: nowrap;         /* Prevent line breaks */
    overflow: hidden;            /* Hide overflow text */
    text-overflow: ellipsis;     /* Add ... at the end */
    vertical-align: top;
}
    .dataframe td {
        color: #2e2e2e;
    }
    #MainMenu, header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -------------------- Title & Input --------------------
st.markdown("<h1 style='font-size: 20px;'>Smart Search</h1>", unsafe_allow_html=True)
email_input = st.text_input("📧 Enter Email", placeholder="example@domain.com")
phone_input = st.text_input("📞 Enter Phone Number", placeholder="123-456-7890")

# -------------------- Combined Search --------------------
def combined_search():
    RECORDS_API = "https://sf-api-3.onrender.com/search"
    ORDER_API = "https://sf-api-3.onrender.com/search_order"

    def fetch_records(email, phone):
        try:
            res = requests.post(RECORDS_API, json={"email": email, "phone": phone})
            return res.json() if res.status_code == 200 else None
        except:
            st.error("⚠️ Could not connect to the records API.")
            return None

    def fetch_orders(email):
        try:
            res = requests.get(ORDERS_API, params={"email": email})
            return res.json() if res.status_code == 200 else None
        except:
            st.error("⚠️ Could not connect to the orders API.")
            return None

    with st.spinner("🔍 Searching records..."):
        record_data = fetch_records(email_input, phone_input)
        order_data = fetch_orders(email_input)

        # -------------------- Contact Section --------------------
        contact_df_list = []
        unified_id = None

        if record_data:
            for table in record_data:
                rows = table["rows"]
                table_name = table["table_name"]
                if rows:
                    df = pd.DataFrame(rows)
                    df.columns = [col.lower() for col in df.columns]
                    df["source_table"] = table_name
                    if "unified_id" in df.columns and not unified_id:
                        unified_id = df["unified_id"].iloc[0]
                    df["unified_id"] = unified_id
                    contact_df_list.append(df)

        st.markdown("<h2 style='font-size: 18px; margin-top: 30px;'>📇 Contact Records</h2>", unsafe_allow_html=True)

        if contact_df_list:
            contact_df = pd.concat(contact_df_list, ignore_index=True)
            display_df = contact_df[["unified_id", "firstname", "lastname", "source_table"]].fillna("")
            display_df = display_df.rename(columns={"unified_id": "Unified ID","firstname": "First Name","lastname": "Last Name","source_table": "Source Table"})
            st.markdown("<div class='dataframe'>" + display_df.to_html(classes="dataframe", index=False) + "</div>", unsafe_allow_html=True)
        else:
            st.info("No contact records found.")

        # -------------------- Orders Section --------------------
        order_df_list = []

        if order_data:
            for table_name, rows in order_data.items():
                if rows:
                    df = pd.DataFrame(rows)
                    df.columns = [col.lower() for col in df.columns]
                    df["source_table"] = table_name
                    order_df_list.append(df)

        st.markdown("<h2 style='font-size: 18px; margin-top: 30px;'>📦 Order Records</h2>", unsafe_allow_html=True)

        if order_df_list:
            order_df = pd.concat(order_df_list, ignore_index=True)
            try:
                
                display_order_df = order_df[["source_table", "order_number", "order_date", "order_amount", "email", "mobilephone", "description"]]
                display_order_df = display_order_df.rename(columns={
    "source_table": "Source Table",
    "order_number": "Order Number",
    "order_date": "Order Date",
    "order_amount": "Order Amount",
    "email": "Email",
    "mobilephone": "Phone Number",
    "description": "Description"
})
                st.markdown("<div class='dataframe'>" + display_order_df.to_html(classes="dataframe", index=False) + "</div>", unsafe_allow_html=True)
            except KeyError:
                st.error("Missing required columns in one or more order sources.")
        else:
            st.info("No order records found.")


# -------------------- Auto Search --------------------
if email_input and phone_input:
    combined_search()
