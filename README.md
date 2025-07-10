**VendorScope** is a Streamlit-based dashboard app designed to analyze and visualize vendor performance using procurement data. The app helps organizations monitor key performance indicators (KPIs) such as delivery timelines, invoice accuracy, return rates, and spend distribution to make data-driven purchasing decisions.


## Features

-  **KPI Calculation**: Automatically calculates vendor metrics from PO - Purchase Orders, GR- Good Receipt, Invoice, and Return data.
-  **Visualizations**:
  - Radar chart for performance of each vendor using drop down
  - Heatmap of KPIs
  - Line trends of delivery delays
  - Bubble chart for accuracy vs timeliness
  - Box plots and bar charts for spend & returns
-  **Vendor Leaderboard**: Ranks vendors based on a composite score.
-  **PDF Report Generation**: Export all visualizations and insights to a downloadable report.
-  **CSV Export**: Download complete KPI report as a CSV file.

---

##  Data Requirements

Upload an Excel file with the following sheets:

- `PO`: Purchase Orders (columns: PO_ID, Vendor, Item, PO_Amount, PO_Date)
- `GR`: Goods Receipts (columns: PO_ID, Vendor, Delivery_Date, Expected_Delivery, PO_Date)
- `Invoices`: Invoices (columns: PO_ID, Vendor, PO_Amount, Invoice_Amount)
- `Returns`: Returns (columns: Return_ID, Vendor, Item)

---

## ⚙️ How to Run

You can run this project locally:

```bash
# 1. Clone the repo
git clone https://github.com/your-username/VendorScope-Vendor-KPI-Tracker.git
cd VendorScope-Vendor-KPI-Tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run main.py

