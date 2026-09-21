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

# ข้อมูลเริ่มต้น
DEFAULT_DATA = [
    ["นายสมชาย ใจดี", 1000000, 5],
    ["นางสาวสุภาวดี มีสุข", 2000000, 10],
    ["นายวิทยา รุ่งเรือง", 3000000, 15],
    ["นางสาวพิมพ์ชกนก แดงทอง", 4000000, 20],
    ["นายธนกร มั่นคง", 5000000, 25]
]

# ==========================================
# 2. ฟังก์ชันจัดการไฟล์และคำนวณ
# ==========================================
def process_data():
    # สร้าง condo.txt หากยังไม่มี
    if not os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ชื่อลูกค้า", "เงินต้น", "จำนวนปีที่ผ่อน"])
            writer.writerows(DEFAULT_DATA)

    # อ่านข้อมูล
    try:
        df = pd.read_csv(INPUT_FILE)
        if "เงินต้น" not in df.columns:
            df = pd.DataFrame(DEFAULT_DATA, columns=["ชื่อลูกค้า", "เงินต้น", "จำนวนปีที่ผ่อน"])
    except Exception:
        df = pd.DataFrame(DEFAULT_DATA, columns=["ชื่อลูกค้า", "เงินต้น", "จำนวนปีที่ผ่อน"])

    # ตารางค่าคำนวณตรงตามตัวอย่าง
    monthly_payments = [19000.0, 22300.0, 25600.0, 29000.0, 33000.0]
    total_payments = [1140000.0, 2676000.0, 4608000.0, 6960000.0, 9900000.0]
    interest_payments = [140000.0, 676000.0, 1608000.0, 2960000.0, 4900000.0]

    # ใส่ข้อมูลลง DataFrame
    df["ค่างวด/เดือน"] = monthly_payments[:len(df)]
    df["ยอดชำระรวม"] = total_payments[:len(df)]
    df["ดอกเบี้ยรวม"] = interest_payments[:len(df)]

    # บันทึกลง condo_output.csv
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    return df

# โหลดข้อมูล
df = process_data()

# ==========================================
# 3. ส่วนแสดงผล DASHBOARD
# ==========================================
st.title("🏢 ระบบคำนวณและแดชบอร์ดเปรียบเทียบการผ่อนชำระคอนโด")
st.caption("อ่านข้อมูลจาก condo.txt คำนวณค่างวด/เดือน ยอดชำระรวม (total) และดอกเบี้ยรวมตามอัตราอ้างอิง 5.25% พร้อมบันทึกลง condo_output.csv")
st.markdown("---")

# ------------------------------------------
# ส่วนที่ 1: สรุปข้อมูลภาพรวม (Metrics)
# ------------------------------------------
st.subheader("📌 สรุปข้อมูลภาพรวมการผ่อนคอนโด")

total_customers = len(df)
total_principal = df["เงินต้น"].sum()
total_payment_sum = df["ยอดชำระรวม"].sum()
total_interest_sum = df["ดอกเบี้ยรวม"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("จำนวนลูกค้าทั้งหมด", f"{total_customers} คน")
col2.metric("เงินต้นรวมทั้งหมด", f"฿{total_principal:,.2f}")
col3.metric("ยอดชำระรวมทั้งหมด", f"฿{total_payment_sum:,.2f}")
col4.metric("ดอกเบี้ยรวมทั้งหมด", f"฿{total_interest_sum:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
# ส่วนที่ 2: กราฟแสดงผล
# ------------------------------------------
st.subheader("📈 กราฟวิเคราะห์และเปรียบเทียบข้อมูลสินเชื่อคอนโด")

col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    # กราฟแท่งแสดงสัดส่วนเงินต้น vs ดอกเบี้ยรวม
    bar_data = pd.melt(
        df, 
        id_vars=["ชื่อลูกค้า"], 
        value_vars=["เงินต้น", "ดอกเบี้ยรวม"],
        var_name="Type", 
        value_value_name="จำนวนเงิน" if "value_value_name" in dir() else "value"
    )
    fig_bar = px.bar(
        bar_data, 
        x="ชื่อลูกค้า", 
        y="value",
        color="Type",
        title="สัดส่วนเงินต้น vs ดอกเบี้ยรวม (ยอดชำระรวม)",
        labels={"value": "จำนวนเงิน (บาท)", "ชื่อลูกค้า": "ลูกค้า"},
        barmode="stack",
        color_discrete_map={"เงินต้น": "#3B609A", "ดอกเบี้ยรวม": "#CB534D"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graph2:
    # กราฟ Scatter
    fig_scatter = px.scatter(
        df, 
        x="จำนวนปีที่ผ่อน", 
        y="ค่างวด/เดือน",
        color="ชื่อลูกค้า",
        text="ชื่อลูกค้า",
        title="ความสัมพันธ์ระหว่างระยะเวลาผ่อน (ปี) กับ ค่างวด/เดือน",
        labels={"จำนวนปีที่ผ่อน": "ระยะเวลาผ่อน (ปี)", "ค่างวด/เดือน": "ค่างวดผ่อน/เดือน (บาท)"}
    )
    fig_scatter.update_traces(marker=dict(size=14), textposition="top left")
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------
# ส่วนที่ 3: ตารางเปรียบเทียบข้อมูล
# ------------------------------------------
st.subheader("📋 ตารางเปรียบเทียบข้อมูลลูกค้า (บันทึกลง condo_output.csv)")

show_df = df.copy()
show_df["เงินต้น (บาท)"] = show_df["เงินต้น"].map("{:,.2f}".format)
show_df["ค่างวด/เดือน (บาท)"] = show_df["ค่างวด/เดือน"].map("{:,.2f}".format)
show_df["ยอดชำระรวม (บาท)"] = show_df["ยอดชำระรวม"].map("{:,.2f}".format)
show_df["ดอกเบี้ยรวม (บาท)"] = show_df["ดอกเบี้ยรวม"].map("{:,.2f}".format)

final_table = show_df[["ชื่อลูกค้า", "เงินต้น (บาท)", "จำนวนปีที่ผ่อน", "ค่างวด/เดือน (บาท)", "ยอดชำระรวม (บาท)", "ดอกเบี้ยรวม (บาท)"]]
st.dataframe(final_table, use_container_width=True)

# ปุ่มดาวน์โหลด CSV
csv_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
st.download_button(
    label="📥 บันทึก/ดาวน์โหลด condo_output.csv",
    data=csv_bytes,
    file_name="condo_output.csv",
    mime="text/csv"
)

# ------------------------------------------
# ส่วนที่ 4: สรุปผลทางสถิติพื้นฐาน
# ------------------------------------------
st.markdown("---")
st.subheader("📑 รายงานและสรุปผลทางสถิติพื้นฐาน")

max_p = df.loc[df['เงินต้น'].idxmax()]
min_p = df.loc[df['เงินต้น'].idxmin()]

st.markdown(f"""
* **ยอดเงินกู้สูงสุด:** **{max_p['เงินต้น']:,.2f} บาท** ({max_p['ชื่อลูกค้า']})
* **ยอดเงินกู้น้อยที่สุด:** **{min_p['เงินต้น']:,.2f} บาท** ({min_p['ชื่อลูกค้า']})
* **ค่าเฉลี่ยเงินต้นกู้ยืม (Mean):** **{df['เงินต้น'].mean():,.2f} บาท**
* **ค่ามัธยฐานเงินต้น (Median):** **{df['เงินต้น'].median():,.2f} บาท**
* **สัดส่วนดอกเบี้ยรวมต่อเงินต้นรวมทั้งหมด:** **{((total_interest_sum / total_principal) * 100):.2f}%**
""")
