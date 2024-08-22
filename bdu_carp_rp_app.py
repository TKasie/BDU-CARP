import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

# page configuration
st.set_page_config(
    page_title="BDU CARP Loss Map",
    page_icon="random",
    layout="wide",
    initial_sidebar_state="expanded")
alt.themes.enable("dark")

st.title('BDU-CARP RESEARCH OUTPUTS: Drought-related Yield Loss Estimates')
st.sidebar.title('About')
st.sidebar.info('Explore one of the four key risk analysis outputs of the BDU-CARP research team')


gdf_file_path = 'data/rmetric_gdf.shp'
@st.cache_data
def read_gdf(file_path):
    gdf = gpd.read_file(file_path)
    gdf['Exposure'] = gdf.loss_abs.div(gdf.loss_rel)
    return gdf

uais_gdf = read_gdf(gdf_file_path)

# sidebars - choosing reporting levels and risk metrics type
reporting_levels = uais_gdf.LReport.unique()
metric_types = uais_gdf.l_metric.unique()
reporting_level = st.sidebar.selectbox('Select a Reporting Level', reporting_levels)
metric_type = st.sidebar.selectbox('Select a Risk Metric', metric_types)

# dataframes for selected sidebar items
selected_RL_gdf = uais_gdf[uais_gdf.LReport==reporting_level]
selected_ML_gdf = selected_RL_gdf[selected_RL_gdf.l_metric==metric_type]

fig, ax = plt.subplots(1, 1)
selected_ML_gdf.plot(column='loss_rel', ax=ax, cmap='Reds', figsize=(8, 8))
stats = st.sidebar.pyplot(fig)

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
    st.markdown('    #### Loss map')
    stats = st.pyplot(fig)
    
selected_ML_gdf_sorted = selected_ML_gdf[['Zone-ID', 'l_metric', 'loss_rel']].sort_values('loss_rel', ascending=False)


with col[2]:
    st.markdown('#### Top Zones')
    st.dataframe(selected_ML_gdf_sorted, 
                 column_order=("Zone-ID", "loss_rel"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "Zone-ID": st.column_config.TextColumn(
                        "Zone-ID",
                    ),
                    "loss_rel": st.column_config.ProgressColumn(
                        "Yield Loss [%]",
                        format="%.2f",
                        min_value=0,
                        max_value=max(selected_ML_gdf_sorted.loss_rel),
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

heatmap = make_heatmap(selected_RL_gdf[['Zone-ID', 'l_metric', 'loss_rel']], 'l_metric', 'Zone-ID', 'loss_rel', 'oranges')
st.altair_chart(heatmap, use_container_width=True)