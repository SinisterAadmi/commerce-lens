import pandas as pd
import plotly.express as px

COLORS = ["#0D9488", "#4564D8", "#F59E0B", "#EC7188", "#8B5CF6"]

def style(fig):
    fig.update_layout(template="plotly_white", font=dict(family="Arial", color="#142C43"),
                      margin=dict(l=15,r=15,t=25,b=20), height=355,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      legend_title_text="", colorway=COLORS)
    return fig

def build_charts(df, frequency="Month", group="Category", bins=30):
    rule = {"Day":"D", "Week":"W-MON", "Month":"MS"}[frequency]
    trend = df.set_index("Date").resample(rule).Revenue.sum().reset_index()
    sales = df.groupby(group, as_index=False).agg(Revenue=("Revenue","sum"), Profit=("Profit","sum")).nlargest(15,"Revenue").sort_values("Revenue")
    payments = df.groupby("Payment Method")["Order ID"].nunique().reset_index(name="Orders")
    mapped = df.dropna(subset=["Latitude","Longitude"]).groupby(["City","State","Latitude","Longitude"],as_index=False).agg(Orders=("Order ID","nunique"), Revenue=("Revenue","sum"))
    sample = df.sample(min(len(df),5000), random_state=42)
    heat = df.pivot_table(index="Weekday",columns="Month",values="Revenue",aggfunc="sum",fill_value=0).reindex(range(7),fill_value=0)
    heat.index = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    values = df.groupby("Order ID",as_index=False).Revenue.sum()
    tree = df.groupby(["Category","Subcategory"],as_index=False).Revenue.sum()
    figures = {
        "Revenue over time": px.line(trend,x="Date",y="Revenue",markers=True,color_discrete_sequence=COLORS),
        "Sales by category" : px.bar(sales,x="Revenue",y=group,orientation="h",hover_data=["Profit"],color_discrete_sequence=COLORS),
        "Payment mix": px.pie(payments,names="Payment Method",values="Orders",hole=.62,color_discrete_sequence=COLORS),
        "Discount vs profit": px.scatter(sample,x="Discount",y="Profit",color="Category",hover_data=["Product","Revenue"],opacity=.55,color_discrete_sequence=COLORS),
        "Sales calendar": px.imshow(heat,aspect="auto",color_continuous_scale="Teal",labels=dict(x="Month",y="Day of week",color="Revenue (₹)")),
        "Order value distribution": px.histogram(values,x="Revenue",nbins=bins,color_discrete_sequence=COLORS,labels={"Revenue":"Order value (₹)"}),
    }
    if not mapped.empty:
        figures["Orders across India"] = px.scatter_map(mapped,lat="Latitude",lon="Longitude",size="Orders",color="Revenue",hover_name="City",hover_data={"State":True,"Orders":True,"Latitude":False,"Longitude":False},zoom=3.2,center={"lat":22,"lon":79},map_style="carto-positron",size_max=42,color_continuous_scale="Teal")
    if tree.Revenue.sum() > 0:
        figures["Category hierarchy"] = px.treemap(tree[tree.Revenue>0],path=["Category","Subcategory"],values="Revenue",color="Category",color_discrete_sequence=COLORS)
    figures["Revenue over time"].update_traces(line_width=3)
    figures["Discount vs profit"].update_xaxes(tickformat=".0%")
    figures["Order value distribution"].update_yaxes(title="Number of orders")
    return {name:style(fig) for name,fig in figures.items()}
