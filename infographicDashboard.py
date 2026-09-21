import io
import math
import csv
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. ตั้งค่าการแสดงผลของ Streamlit
# ==========================================
st.set_page_config(
    page_title="Condo Mortgage Dashboard",
    page_icon="🏢",
    layout="wide"
)

INPUT_FILE = "condo.txt"
OUTPUT_FILE = "condo_output.csv"
ANNUAL_INTEREST_RATE = 0.0525  # อัตราดอกเบี้ย 5.25% ต่อปี

# ข้อมูลตัวอย่างเริ่มต้นตามโจทย์ทั้ง 5 คน
DEFAULT_DATA = [
    ["นายสมชาย ใจดี", 1000000, 5],
    ["นางสาวสุภาวดี มีสุข", 2000000, 10],
    ["นายวิทยา รุ่งเรือง", 3000000, 15],
    ["นายสมชาย ใจดี", 4000000, 20],
    ["นายธนกร มั่นคง", 5000000, 25]
]

# ==========================================
# 2. ฟังก์ชันจัดการไฟล์และคำนวณทางการเงิน
# ==========================================
def ensure_input_file():
    """สร้างไฟล์ condo.txt อัตโนมัติหากยังไม่มีในโฟลเดอร์"""
    if not os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ชื่อลูกค้า", "จำนวนเงินต้น", "จำนวนปีที่ผ่อน"])
            writer.writerows(DEFAULT_DATA)

def calculate_loan(principal, years, rate=ANNUAL_INTEREST_RATE):
    """คำนวณผ่อนต่อเดือน ยอดชำระรวม และดอกเบี้ยรวมด้วยสูตร Annuity"""
    monthly_rate = rate / 12
    total_months = years * 12
    
    # สูตรคำนวณค่างวดผ่อนต่อเดือน
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**total_months) / ((1 + monthly_rate)**total_months - 1)
    total_payment = monthly_payment * total_months
    total_interest = total_payment - principal
    
    return monthly_payment, total_payment, total_interest

def load_and_process_data():
    """อ่าน condo.txt นำมาคำนวณ และสร้าง DataFrame"""
    ensure_input_file()
    
    try:
        df = pd.read_csv(INPUT_FILE, header=None, names=["ชื่อลูกค้า", "จำนวนเงินต้น", "จำนวนปีที่ผ่อน"])
        if not str(df.iloc[0]["จำนวนเงินต้น"]).replace('.', '', 1).isdigit():
            df = pd.read_csv(INPUT_FILE)
            df.columns = ["ชื่อลูกค้า", "จำนวนเงินต้น", "จำนวนปีที่ผ่อน"]
    except Exception:
        df = pd.DataFrame(DEFAULT_DATA, columns=["ชื่อลูกค้า", "จำนวนเงินต้น", "จำนวนปีที่ผ่อน"])

    # แปลงชนิดข้อมูลตัวเลข
    df["จำนวนเงินต้น"] = pd.to_numeric(df["จำนวนเงินต้น"], errors='coerce')
    df["จำนวนปีที่ผ่อน"] = pd.to_numeric(df["จำนวนปีที่ผ่อน"], errors='coerce')

    # คำนวณแต่ละรายการ
    monthly_list, total_list, interest_list = [], [], []
    for _, row in df.iterrows():
        m_pmt, t_pmt, t_int = calculate_loan(row["จำนวนเงินต้น"], int(row["จำนวนปีที่ผ่อน"]))
        monthly_list.append(round(m_pmt, 2))
        total_list.append(round(t_pmt, 2))
        interest_list.append(round(t_int, 2))

    df["ผ่อนต่อเดือน"] = monthly_list
    df["ดอกเบี้ยรวม"] = interest_list
    df["ยอดชำระรวม"] = total_list

    # บันทึกลง condo_output.csv อัตโนมัติ
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    return df

# ==========================================
# 3. โหลดและประมวลผลข้อมูล
# ==========================================
df = load_and_process_data()

# ==========================================
# 4. ส่วนแสดงผลบน STREAMLIT DASHBOARD
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
col1.metric("จำนวนลูกค้าทั้งหมด", f"{total_customers} คน")
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
    # กราฟแท่งเปรียบเทียบเงินต้นและดอกเบี้ยรวม
    fig_bar = px.bar(
        df, 
        x="ชื่อลูกค้า", 
        y=["จำนวนเงินต้น", "ดอกเบี้ยรวม"],
        title="เปรียบเทียบสัดส่วนเงินต้นและดอกเบี้ยรวมของลูกค้าแต่ละราย",
        labels={"value": "จำนวนเงิน (บาท)", "variable": "องค์ประกอบภาระหนี้"},
        barmode="stack",
        color_discrete_sequence=["#1976D2", "#FF7043"]
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    # กราฟเส้นแสดงยอดผ่อนต่อเดือนตามจำนวนปี
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
    # กราฟวงกลมแสดงสัดส่วนเงินต้นรวม vs ดอกเบี้ยรวมทั้งหมด
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

# จัดรูปแบบการแสดงผลตัวเลขในตาราง
formatted_df = df.copy()
formatted_df["จำนวนเงินต้น"] = formatted_df["จำนวนเงินต้น"].map("฿{:,.2f}".format)
formatted_df["ผ่อนต่อเดือน"] = formatted_df["ผ่อนต่อเดือน"].map("฿{:,.2f}".format)
formatted_df["ดอกเบี้ยรวม"] = formatted_df["ดอกเบี้ยรวม"].map("฿{:,.2f}".format)
formatted_df["ยอดชำระรวม"] = formatted_df["ยอดชำระรวม"].map("฿{:,.2f}".format)

st.dataframe(formatted_df, use_container_width=True)

# ปุ่มดาวน์โหลดไฟล์ CSV
csv_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
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
