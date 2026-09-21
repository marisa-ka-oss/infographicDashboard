import io
import math
import csv
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. ตั้งค่าหน้าเพจ Streamlit
# ==========================================
st.set_page_config(
    page_title="Condo Mortgage Dashboard",
    page_icon="🏢",
    layout="wide"
)

INPUT_FILE = "condo.txt"
OUTPUT_FILE = "condo_output.csv"

# ข้อมูลตัวอย่าง 5 สัญญา
DATA_EXACT = [
    {"ชื่อลูกค้า": "นายสมชาย ใจดี", "จำนวนเงินต้น": 1000000.0, "จำนวนปีที่ผ่อน": 5, "ผ่อนต่อเดือน": 18985.98, "ยอดชำระรวม": 1139159.03},
    {"ชื่อลูกค้า": "นางสาวสุภาวดี มีสุข", "จำนวนเงินต้น": 2000000.0, "จำนวนปีที่ผ่อน": 10, "ผ่อนต่อเดือน": 21458.34, "ยอดชำระรวม": 2575000.83},
    {"ชื่อลูกค้า": "นายวิทยา รุ่งเรือง", "จำนวนเงินต้น": 3000000.0, "จำนวนปีที่ผ่อน": 15, "ผ่อนต่อเดือน": 24116.33, "ยอดชำระรวม": 4340939.66},
    {"ชื่อลูกค้า": "นายสมชาย ใจดี", "จำนวนเงินต้น": 4000000.0, "จำนวนปีที่ผ่อน": 20, "ผ่อนต่อเดือน": 26953.77, "ยอดชำระรวม": 6468904.00},
    {"ชื่อลูกค้า": "นายธนกร มั่นคง", "จำนวนเงินต้น": 5000000.0, "จำนวนปีที่ผ่อน": 25, "ผ่อนต่อเดือน": 29962.39, "ยอดชำระรวม": 8988715.73}
]

# ==========================================
# 2. ฟังก์ชันประมวลผลข้อมูล
# ==========================================
def load_and_process_data():
    df = pd.DataFrame(DATA_EXACT)
    # คำนวณดอกเบี้ยรวม = ยอดชำระรวม - จำนวนเงินต้น
    df["ดอกเบี้ยรวม"] = df["ยอดชำระรวม"] - df["จำนวนเงินต้น"]
    
    # สร้างคอลัมน์ระบุรายการสัญญาเพื่อป้องกันชื่อซ้ำในกราฟ
    df["ลูกค้า/สัญญา"] = [f"รายการที่ {i+1}: {name}" for i, name in enumerate(df["ชื่อลูกค้า"])]
    
    # เซฟลง condo_output.csv
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    return df

df = load_and_process_data()

# ==========================================
# 3. ส่วนแสดงผลบน STREAMLIT DASHBOARD
# ==========================================
st.title("🏢 Condo Mortgage Analytics Dashboard")
st.caption("ระบบสรุป วิเคราะห์ และเปรียบเทียบข้อมูลสินเชื่อคอนโด (อัตราดอกเบี้ย 5.25% ต่อปี)")
st.markdown("---")

# ------------------------------------------
# ส่วนที่ 1: สรุปข้อมูลภาพรวม (KPI Metrics)
# ------------------------------------------
st.subheader("📊 1. สรุปข้อมูลภาพรวมการผ่อนคอนโด")

total_customers = len(df)
total_principal = df["จำนวนเงินต้น"].sum()
total_payment_sum = df["ยอดชำระรวม"].sum()
total_interest_sum = df["ดอกเบี้ยรวม"].sum()
avg_monthly = df["ผ่อนต่อเดือน"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("จำนวนสัญญา/รายการ", f"{total_customers} รายการ")
col2.metric("วงเงินกู้รวมทั้งหมด", f"฿{total_principal:,.2f}")
col3.metric("ยอดชำระรวมสุทธิ (ต้น+ดอก)", f"฿{total_payment_sum:,.2f}")
col4.metric("เฉลี่ยผ่อน/เดือน/ราย", f"฿{avg_monthly:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
# ส่วนที่ 2: กราฟวิเคราะห์และเปรียบเทียบข้อมูล
# ------------------------------------------
st.subheader("📈 2. กราฟวิเคราะห์และเปรียบเทียบข้อมูลสินเชื่อคอนโด")

tab1, tab2, tab3 = st.tabs(["สัดส่วนเงินต้น vs ดอกเบี้ย", "แนวโน้มการผ่อนต่อเดือน", "สัดส่วนภาระหนี้ภาพรวม"])

with tab1:
    fig_bar = px.bar(
        df, 
        x="ลูกค้า/สัญญา", 
        y=["จำนวนเงินต้น", "ดอกเบี้ยรวม"],
        title="เปรียบเทียบสัดส่วนเงินต้นและดอกเบี้ยรวมของลูกค้าแต่ละสัญญา",
        labels={"value": "จำนวนเงิน (บาท)", "variable": "องค์ประกอบภาระหนี้", "ลูกค้า/สัญญา": "ชื่อลูกค้า / สัญญา"},
        barmode="stack",
        color_discrete_sequence=["#1976D2", "#FF7043"]
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    fig_line = px.line(
        df, 
        x="จำนวนปีที่ผ่อน", 
        y="ผ่อนต่อเดือน",
        text="ชื่อลูกค้า",
        markers=True,
        title="ความสัมพันธ์ระหว่างระยะเวลาผ่อน (ปี) และยอดชำระต่อเดือน",
        labels={"จำนวนปีที่ผ่อน": "ระยะเวลาผ่อน (ปี)", "ผ่อนต่อเดือน": "ยอดผ่อนต่อเดือน (บาท)"}
    )
    fig_line.update_traces(textposition="top center")
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    pie_data = pd.DataFrame({
        "ประเภท": ["เงินต้นรวมทั้งหมด", "ดอกเบี้ยรวมทั้งหมด"],
        "จำนวนเงิน": [total_principal, total_interest_sum]
    })
    fig_pie = px.pie(
        pie_data,
        names="ประเภท",
        values="จำนวนเงิน",
        title="สัดส่วนเงินต้นรวม และดอกเบี้ยรวมทั้งหมดในระบบ",
        color_discrete_sequence=["#2E7D32", "#E53935"]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ------------------------------------------
# ส่วนที่ 3: ตารางเปรียบเทียบข้อมูลลูกค้าและการบันทึก
# ------------------------------------------
st.subheader("📋 3. ตารางเปรียบเทียบข้อมูลลูกค้า ( condo_output.csv )")

# แสดงผลตารางที่มีคอลัมน์ "ดอกเบี้ยรวม" ครบถ้วน
show_df = df[["ชื่อลูกค้า", "จำนวนเงินต้น", "จำนวนปีที่ผ่อน", "ผ่อนต่อเดือน", "ดอกเบี้ยรวม", "ยอดชำระรวม"]].copy()
show_df["จำนวนเงินต้น"] = show_df["จำนวนเงินต้น"].map("{:,.2f}".format)
show_df["ผ่อนต่อเดือน"] = show_df["ผ่อนต่อเดือน"].map("{:,.2f}".format)
show_df["ดอกเบี้ยรวม"] = show_df["ดอกเบี้ยรวม"].map("{:,.2f}".format)
show_df["ยอดชำระรวม"] = show_df["ยอดชำระรวม"].map("{:,.2f}".format)

st.dataframe(show_df, use_container_width=True)

# ปุ่มดาวน์โหลด CSV
csv_bytes = df[["ชื่อลูกค้า", "จำนวนเงินต้น", "จำนวนปีที่ผ่อน", "ผ่อนต่อเดือน", "ดอกเบี้ยรวม", "ยอดชำระรวม"]].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
st.download_button(
    label="📥 บันทึก/ดาวน์โหลด condo_output.csv",
    data=csv_bytes,
    file_name="condo_output.csv",
    mime="text/csv"
)

# ------------------------------------------
# ส่วนที่ 4: สรุปผลรายงานด้วยสถิติพื้นฐาน
# ------------------------------------------
st.markdown("---")
st.subheader("📑 4. รายงานและสรุปผลทางสถิติพื้นฐาน")

max_principal_row = df.loc[df['จำนวนเงินต้น'].idxmax()]
min_principal_row = df.loc[df['จำนวนเงินต้น'].idxmin()]
max_monthly_row = df.loc[df['ผ่อนต่อเดือน'].idxmax()]
min_monthly_row = df.loc[df['ผ่อนต่อเดือน'].idxmin()]

st.markdown(f"""
* **ยอดเงินกู้สูงสุด:** **{max_principal_row['จำนวนเงินต้น']:,.2f} บาท** ({max_principal_row['ชื่อลูกค้า']})
* **ยอดเงินกู้น้อยที่สุด:** **{min_principal_row['จำนวนเงินต้น']:,.2f} บาท** ({min_principal_row['ชื่อลูกค้า']})
* **ค่าเฉลี่ยเงินต้นกู้ยืม (Mean):** **{df['จำนวนเงินต้น'].mean():,.2f} บาท**
* **ค่ามัธยฐานเงินต้น (Median):** **{df['จำนวนเงินต้น'].median():,.2f} บาท**
* **ยอดผ่อนต่อเดือนสูงสุด:** **{max_monthly_row['ผ่อนต่อเดือน']:,.2f} บาท/เดือน** ({max_monthly_row['ชื่อลูกค้า']})
* **ยอดผ่อนต่อเดือนต่ำสุด:** **{min_monthly_row['ผ่อนต่อเดือน']:,.2f} บาท/เดือน** ({min_monthly_row['ชื่อลูกค้า']})
* **สัดส่วนดอกเบี้ยรวมต่อเงินต้นรวมทั้งหมด:** **{((total_interest_sum / total_principal) * 100):.2f}%**
""")
