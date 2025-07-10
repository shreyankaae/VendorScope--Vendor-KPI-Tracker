import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="Vendor Dashboard", layout="wide")
st.title("📊 Vendor Performance Dashboard")

# KPI calculation function
def calculate_kpis(po_df, gr_df, invoice_df, return_df):
    gr_df['Delivery_Date'] = pd.to_datetime(gr_df['Delivery_Date'])
    gr_df['Expected_Delivery'] = pd.to_datetime(gr_df['Expected_Delivery'])
    gr_df['PO_Date'] = pd.to_datetime(gr_df['PO_Date'])

    gr_df['On_Time'] = gr_df['Delivery_Date'] <= gr_df['Expected_Delivery']
    gr_df['Delivery_Delay'] = (gr_df['Delivery_Date'] - gr_df['Expected_Delivery']).dt.days
    gr_df['PO_Cycle_Days'] = (gr_df['Delivery_Date'] - gr_df['PO_Date']).dt.days

    kpi1 = gr_df.groupby('Vendor')['On_Time'].mean().mul(100).reset_index(name='On_Time_Delivery_%')
    invoice_df['Invoice_Accuracy'] = abs(invoice_df['Invoice_Amount'] - invoice_df['PO_Amount']) <= 0.05 * invoice_df['PO_Amount']
    kpi2 = invoice_df.groupby('Vendor')['Invoice_Accuracy'].mean().mul(100).reset_index(name='Invoice_Accuracy_%')

    return_counts = return_df.groupby('Vendor')['Return_ID'].count()
    po_counts = po_df.groupby('Vendor')['PO_ID'].count()
    return_rate = return_counts.div(po_counts).fillna(0).mul(100).reset_index(name='Return_Rate_%')

    kpi4 = po_df.groupby('Vendor')['Item'].nunique().reset_index(name='Items_Supplied')
    kpi5 = po_df.groupby('Vendor')['PO_Amount'].sum().reset_index(name='Total_Spend')
    delay = gr_df.groupby('Vendor')['Delivery_Delay'].mean().reset_index(name='Avg_Delivery_Delay')
    cycle = gr_df.groupby('Vendor')['PO_Cycle_Days'].mean().reset_index(name='PO_Cycle_Days')

    df = kpi1.merge(kpi2, on='Vendor', how='outer') \
             .merge(return_rate, on='Vendor', how='outer') \
             .merge(kpi4, on='Vendor', how='outer') \
             .merge(kpi5, on='Vendor', how='outer') \
             .merge(delay, on='Vendor', how='outer') \
             .merge(cycle, on='Vendor', how='outer')
    return df

# Add score
def add_score(df):
    score_df = df.copy()
    score_df[['Return_Rate_%', 'Avg_Delivery_Delay', 'PO_Cycle_Days']] = \
        score_df[['Return_Rate_%', 'Avg_Delivery_Delay', 'PO_Cycle_Days']].max() - \
        score_df[['Return_Rate_%', 'Avg_Delivery_Delay', 'PO_Cycle_Days']]
    scoring_cols = ['On_Time_Delivery_%', 'Invoice_Accuracy_%', 'Return_Rate_%',
                    'Avg_Delivery_Delay', 'PO_Cycle_Days', 'Total_Spend']
    score_df['Vendor_Score'] = MinMaxScaler().fit_transform(score_df[scoring_cols]).mean(axis=1)
    return score_df

# Main Upload Block
uploaded_file = st.file_uploader("📤 Upload Excel File (with PO, GR, Invoices, Returns)", type=["xlsx"])

if uploaded_file:
    try:
        # Read Sheets
        po_df = pd.read_excel(uploaded_file, sheet_name="PO")
        gr_df = pd.read_excel(uploaded_file, sheet_name="GR")
        invoice_df = pd.read_excel(uploaded_file, sheet_name="Invoices")
        return_df = pd.read_excel(uploaded_file, sheet_name="Returns")

        # Process & Score
        kpis = calculate_kpis(po_df, gr_df, invoice_df, return_df)
        df_with_scores = add_score(kpis)

        # Display Table
        st.subheader("📊 KPI Summary Table")
        st.dataframe(df_with_scores)

        # Leaderboard
        st.subheader("🏆 Vendor Leaderboard")
        fig_leaderboard = px.bar(df_with_scores.sort_values("Vendor_Score", ascending=False),
                                 x="Vendor_Score", y="Vendor", orientation='h', color="Vendor_Score")
        st.plotly_chart(fig_leaderboard, use_container_width=True)

        # Radar Chart
        selected_vendor = st.selectbox("📌 Select Vendor for Radar Chart", df_with_scores['Vendor'])
        kpi_cols = ['On_Time_Delivery_%', 'Invoice_Accuracy_%', 'Return_Rate_%',
                    'Avg_Delivery_Delay', 'PO_Cycle_Days', 'Total_Spend']
        radar_data = df_with_scores[df_with_scores['Vendor'] == selected_vendor][kpi_cols].T.reset_index()
        radar_data.columns = ['KPI', 'Value']
        fig_radar = px.line_polar(radar_data, r='Value', theta='KPI', line_close=True,
                                  title=f"Radar Chart - {selected_vendor}")
        st.plotly_chart(fig_radar, use_container_width=True)

        # Heatmap
        st.subheader("🔥 KPI Heatmap")
        heatmap_data = df_with_scores.set_index('Vendor')[kpi_cols]
        fig_heatmap = px.imshow(heatmap_data, color_continuous_scale='YlGnBu',
                                labels=dict(x="KPI", y="Vendor", color="Value"))
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Trend Line
        trend_df = gr_df.copy()
        trend_df['Week'] = trend_df['Delivery_Date'].dt.to_period('W').dt.start_time
        trend_chart = trend_df.groupby(['Week', 'Vendor'])['Delivery_Delay'].mean().reset_index()
        fig_trend = px.line(trend_chart, x='Week', y='Delivery_Delay', color='Vendor',
                            title='📈 Weekly Avg Delivery Delay by Vendor')
        st.plotly_chart(fig_trend, use_container_width=True)

        # PO Spend Box Plot
        fig_box = px.box(po_df, x='Vendor', y='PO_Amount', points="all",
                         title='💰 PO Spend Distribution by Vendor')
        st.plotly_chart(fig_box, use_container_width=True)

        # Bubble Chart
        fig_scatter = px.scatter(df_with_scores, x='Invoice_Accuracy_%', y='On_Time_Delivery_%',
                                 size='Total_Spend', color='Vendor', hover_name='Vendor',
                                 title='🎯 Invoice Accuracy vs Timeliness (Bubble Size = Spend)', size_max=40)
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Top 5 Vendors
        top_spenders = df_with_scores.sort_values(by='Total_Spend', ascending=False).head(5)
        fig_bar = px.bar(top_spenders, x='Vendor', y='Total_Spend', color='Total_Spend',
                         title='🏅 Top 5 Vendors by Procurement Spend')
        st.plotly_chart(fig_bar, use_container_width=True)

        # Return Rate by Item
        return_rate_item = return_df.groupby('Item')['Return_ID'].count().reset_index(name='Return_Count')
        fig_return_item = px.bar(return_rate_item.sort_values('Return_Count', ascending=False),
                                 x='Item', y='Return_Count', title='📦 Most Returned Items')
        st.plotly_chart(fig_return_item, use_container_width=True)

        # KPI Cards
        st.subheader("📋 Overall KPI Averages")
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg On-Time %", f"{df_with_scores['On_Time_Delivery_%'].mean():.2f}%")
        col2.metric("Avg Invoice Accuracy", f"{df_with_scores['Invoice_Accuracy_%'].mean():.2f}%")
        col3.metric("Avg Return Rate", f"{df_with_scores['Return_Rate_%'].mean():.2f}%")

        # Download CSV
        csv = df_with_scores.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download KPI Report CSV", data=csv,
                           file_name="vendor_kpi_report.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error loading or processing data: {e}")

run = "streamlit run app.py"


