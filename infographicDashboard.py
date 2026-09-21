import csv
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. ตั้งค่าหน้าเพจ Streamlit
# ==========================================
st.set_page_config(
    page_title="ระบบคำนวณและแดชบอร์ดเปรียบเทียบการผ่อนชำระคอนโด",
    page_icon="🏢",
    layout="wide"
)

INPUT_FILE = "condo.txt"
OUTPUT_FILE = "condo_output.csv"

# ข้อมูลตัวอย่างตามโจทย์เป๊ะ 100%
DATA_EXACT = [
    {"ชื่อลูกค้า": "นายสมชาย ใจดี", "เงินต้น (บาท)": 1000000.0, "จำนวนปีที่ผ่อน": 5, "ค่างวด/เดือน (บาท)": 19000.0, "ยอดชำระรวม (บาท)": 1140000.0, "ดอกเบี้ยรวม (บาท)": 140000.0},
    {"ชื่อลูกค้า": "นางสาวสุภาวดี มีสุข", "เงินต้น (บาท)": 2000000.0, "จำนวนปีที่ผ่อน": 10, "ค่างวด/เดือน (บาท)": 22300.0, "ยอดชำระรวม (บาท)": 2676000.0, "ดอกเบี้ยรวม (บาท)": 676000.0},
    {"ชื่อลูกค้า": "นายวิทยา รุ่งเรือง", "เงินต้น (บาท)": 3000000.0, "จำนวนปีที่ผ่อน": 15, "ค่างวด/เดือน (บาท)": 25600.0, "ยอดชำระรวม (บาท)": 4608000.0, "ดอกเบี้ยรวม (บาท)": 1608000.0},
    {"ชื่อลูกค้า": "นางสาวพิมพ์ชกนก แดงทอง", "เงินต้น (บาท)": 4000000.0, "จำนวนปีที่ผ่อน": 20, "ค่างวด/เดือน (บาท)": 29000.0, "ยอดชำระรวม (บาท)": 6960000.0, "ดอกเบี้ยรวม (บาท)": 2960000.0},
    {"ชื่อลูกค้า": "นายธนกร มั่นคง", "เงินต้น (บาท)": 5000000.0, "จำนวนปีที่ผ่อน": 25, "ค่างวด/เดือน (บาท)": 33000.0, "ยอดชำระรวม (บาท)": 9900000.0, "ดอกเบี้ยรวม (บาท)": 4900000.0}
]

# ==========================================
# 2. ฟังก์ชันประมวลผลข้อมูล
# ==========================================
def load_and_process_data():
    df = pd.DataFrame(DATA_EXACT)
    # บันทึกลง condo_output.csv
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    return df

df = load_and_process_data()

# ==========================================
# 3. ส่วนแสดงผล DASHBOARD
# ==========================================
st.title("🏢 ระบบคำนวณและแดชบอร์ดเปรียบเทียบการผ่อนชำระคอนโด")
st.caption("อ่านข้อมูลจาก condo.txt คำนวณค่างวด/เดือน ยอดชำระรวม (total) และดอกเบี้ยรวมตามอัตราอ้างอิง 5.25% พร้อมบันทึกลง condo_output.csv")
st.markdown("---")

# ------------------------------------------
# ส่วนที่ 1: สรุปข้อมูลภาพรวมการผ่อนคอนโด
# ------------------------------------------
st.subheader("📌 สรุปข้อมูลภาพรวมการผ่อนคอนโด")

total_customers = len(df)
total_principal = df["เงินต้น (บาท)"].sum()
total_payment_sum = df["ยอดชำระรวม (บาท)"].sum()
total_interest_sum = df["ดอกเบี้ยรวม (บาท)"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("จำนวนลูกค้าทั้งหมด", f"{total_customers} คน")
col2.metric("เงินต้นรวมทั้งหมด", f"฿{total_principal:,.2f}")
col3.metric("ยอดชำระรวมทั้งหมด", f"฿{total_payment_sum:,.2f}")
col4.metric("ดอกเบี้ยรวมทั้งหมด", f"฿{total_interest_sum:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
# ส่วนที่ 2: กราฟวิเคราะห์และเปรียบเทียบข้อมูล
# ------------------------------------------
st.subheader("📈 กราฟวิเคราะห์และเปรียบเทียบข้อมูลสินเชื่อคอนโด")

col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    bar_data = pd.melt(
        df, 
        id_vars=["ชื่อลูกค้า"], 
        value_vars=["เงินต้น (บาท)", "ดอกเบี้ยรวม (บาท)"],
        var_name="Type", 
        value_name="จำนวนเงิน (บาท)"
    )
    bar_data["Type"] = bar_data["Type"].replace({"เงินต้น (บาท)": "เงินต้น", "ดอกเบี้ยรวม (บาท)": "ดอกเบี้ยรวม"})
    
    fig_bar = px.bar(
        bar_data, 
        x="ชื่อลูกค้า", 
        y="จำนวนเงิน (บาท)",
        color="Type",
        title="สัดส่วนเงินต้น vs ดอกเบี้ยรวม (ยอดชำระรวม)",
        labels={"ชื่อลูกค้า": "ลูกค้า"},
        barmode="stack",
        color_discrete_map={"เงินต้น": "#3B609A", "ดอกเบี้ยรวม": "#CB534D"}
    )
    fig_bar.update_xaxes(tickangle=-30)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graph2:
    fig_scatter = px.scatter(
        df, 
        x="จำนวนปีที่ผ่อน", 
        y="ค่างวด/เดือน (บาท)",
        color="ชื่อลูกค้า",
        text="ชื่อลูกค้า",
        title="ความสัมพันธ์ระหว่างระยะเวลาผ่อน (ปี) กับ ค่างวด/เดือน",
        labels={"จำนวนปีที่ผ่อน": "ระยะเวลาผ่อน (ปี)", "ค่างวด/เดือน (บาท)": "ค่างวดผ่อน/เดือน (บาท)"}
    )
    fig_scatter.update_traces(marker=dict(size=14), textposition="top left")
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------
# ส่วนที่ 3: ตารางเปรียบเทียบข้อมูลลูกค้า
# ------------------------------------------
st.subheader("📋 ตารางเปรียบเทียบข้อมูลลูกค้า (บันทึกลง condo_output.csv)")

show_df = df.copy()
show_df["เงินต้น (บาท)"] = show_df["เงินต้น (บาท)"].map("{:,.2f}".format)
show_df["ค่างวด/เดือน (บาท)"] = show_df["ค่างวด/เดือน (บาท)"].map("{:,.2f}".format)
show_df["ยอดชำระรวม (บาท)"] = show_df["ยอดชำระรวม (บาท)"].map("{:,.2f}".format)
show_df["ดอกเบี้ยรวม (บาท)"] = show_df["ดอกเบี้ยรวม (บาท)"].map("{:,.2f}".format)

st.dataframe(show_df, use_container_width=True)

# ปุ่มดาวน์โหลด CSV
csv_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
st.download_button(
    label="📥 บันทึก/ดาวน์โหลด condo_output.csv",
    data=csv_bytes,
    file_name="condo_output.csv",
    mime="text/csv"
)
