# encoding: utf-8
"""
Created on Saturdy Aug 24 11:04:04 2024

@author: BDU-CARP RESEARCH TEAM, PI (Tesfahun Kasie)
"""
import time
import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="BDU-CARP Research Team - Drought Risk Analysis",
    page_icon=":ambulance:",
    layout="wide",
    initial_sidebar_state="expanded"
)


#Page header
hd1, hd2 = st.columns((0.07,1)) 

hd1, hd2 = st.columns((0.2, 1))
hd1.image('index.png', width=100)
hd2.title('Drought-related Yield Loss Estimates for Amhara Region, Ethiopia')
hd2.markdown(" **tel:** +251 934 97 6251 **| website:** https://www.bdu.edu.et **| email:** tesfahun.asmamaw@bdu.edu.et")

alt.themes.enable("dark")

st.sidebar.title('About')
with st.sidebar.expander("Click here for page overview"):
    st.info("This dashboard was built to share [BDU-CARP resaerch findings](https://hats.arizona.edu/baseline-probabilistic-climate-risk-assessment-information-foundation-scaling-smallholder) with the general DRM community and help users to explore drought risk analysis outputs produced by the BDU-CARP research team for Amhara region, Ethiopia. Drought-related yield losses on six important risk metrics are reported at three levels: (1) Insurance zones which are newly defined using an ML cluster algorithm; (2) Livelihood zones as defined by [FEWS NET](https://fews.net/east-africa/ethiopia/livelihood-zone-map/january-2018); and (3) Administrative zones of Amhara region. Users can select their preferred reporting level from the sidebar and explore each of the risk metrics. This is our attept to satisfy the interests of multiple actors operating at different scales of DRM decision making. Note that yield losses are estimated based on the vulnerability curve we established for each insurance zone using a regression model of yield as a function of growing season precipitation anomally. FAO-WaPOR biomass production dataset was used for yield and CHIRIPS dataset for precipitation. Figures shown in the first row of the page are based on relative losses in percent. Absolute losses in KgDM/ha are also shown in the bar graph at the end of the page in addition to the map in the sidebar to visualize its spatial distribution.")


gdf_file_path = 'rmetric_gdf.shp'
@st.cache_data
def read_gdf(file_path):
    gdf = gpd.read_file(file_path)
    gdf['Exposure'] = gdf.loss_abs.div(gdf.loss_rel)
    #gdf['Yield loss (%)'] = gdf.loss_rel.clip(lower=0.0, upper=1.0)
    return gdf

uais_gdf = read_gdf(gdf_file_path)
uais_gdf['Yield loss (%)'] = uais_gdf.loss_rel.clip(lower=0.0, upper=1.0)

# sidebars - choosing reporting levels and risk metrics type 
reporting_levels = uais_gdf.LReport.unique()
metric_types = uais_gdf.l_metric.unique()
reporting_level = st.sidebar.selectbox('Select a Reporting Level', reporting_levels)
metric_type = st.sidebar.selectbox('Select a Risk Metric', metric_types)

# dataframes for selected sidebar items
selected_RL_gdf = uais_gdf[uais_gdf.LReport==reporting_level]
selected_ML_gdf = selected_RL_gdf[selected_RL_gdf.l_metric==metric_type]


fig, ax = plt.subplots(1, 1)
selected_ML_gdf.plot(column='loss_abs', ax=ax, edgecolor='w', cmap='Reds', figsize=(8, 8), legend=True)
plt.title('Absolute loss [KgDM/ha]')
gdf_plot = st.sidebar.pyplot(fig)

# Dashboard Main Panel
col = st.columns((2, 4, 2.5), gap='medium')
selected_ML_gdf_sorted = selected_ML_gdf[['Zone-ID', 'l_metric', 'Exposure']].sort_values('Exposure', ascending=False)

with col[0]:
    st.markdown('#### Exposure')
    st.dataframe(selected_ML_gdf_sorted, 
                 column_order=("Zone-ID", "Exposure"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "Zone-ID": st.column_config.TextColumn(
                        "Zone-ID",
                    ),
                    "Exposure": st.column_config.ProgressColumn(
                        "Yield [KgDM/ha]",
                        format="%.2f",
                        min_value=0,
                        max_value=max(selected_ML_gdf_sorted.Exposure),
                     )}
                )


with col[1]:
    st.markdown('#### Yield Loss Relative to Exposure')
    fig, ax = plt.subplots(1, 1)
    selected_ML_gdf.plot(column='Yield loss (%)', ax=ax, edgecolor='w', cmap='Reds', figsize=(8, 8), legend=True)
    gdf_plot = st.pyplot(fig)

    
# Top zones sorted by descending order of yield loss
selected_ML_gdf_sorted = selected_ML_gdf[['Zone-ID', 'l_metric', 'loss_rel', 'Yield loss (%)']].sort_values('Yield loss (%)', ascending=False)

with col[2]:
    st.markdown('#### Top Zones')
    st.dataframe(selected_ML_gdf_sorted, 
                 column_order=("Zone-ID", "Yield loss (%)"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "Zone-ID": st.column_config.TextColumn(
                        "Zone-ID",
                    ),
                    "Yield loss (%)": st.column_config.ProgressColumn(
                        "Yield Loss [%]",
                        format="%.2f",
                        min_value=0,
                        max_value=max(selected_ML_gdf_sorted['loss_rel']),
                     )}
                 )

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Loss metric", titleFontSize=18, titlePadding=15, titleFontWeight=900,
                                              labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(title=reporting_level, titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color(f'max({input_color}):Q',
                        legend=None,
                        scale=alt.Scale(scheme=input_color_theme)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
    ).properties(width=900, height=300
                ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    ) 
    return heatmap

heatmap1 = make_heatmap(selected_RL_gdf[['Zone-ID', 'l_metric', 'loss_abs', 'Yield loss (%)']], 'l_metric', 'Zone-ID', 'Yield loss (%)', 'oranges')

st.altair_chart(heatmap1, use_container_width=True)


#Bar graph by risk metrics
bar_gr = px.bar(selected_RL_gdf, x='Zone-ID', y='loss_abs', barmode='relative', color='l_metric', title="Yield Loss [KgDM/ha]")
st.plotly_chart(bar_gr)
#bar_gr = px.bar(selected_RL_gdf, x='Zone-ID', y='Yield loss (%)', barmode='overlay', color='l_metric')
#st.plotly_chart(bar_gr)

# Contact Form

with st.expander("Contact us"):
    with st.form(key='contact', clear_on_submit=True):
        
        email = st.text_input('Contact Email')
        st.text_area("Query","Please specify your request or general comment here")  
        
        submit_button = st.form_submit_button(label='Send Information')
