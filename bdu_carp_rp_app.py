# encoding: utf-8
"""
Created on Saturdy Aug 24 11:04:04 2024

@author: BDU-CARP RESEARCH TEAM, PI (Tesfahun Kasie)
"""
import time
import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="BDU-CARP Research Team - Drought Risk Analysis",
    page_icon=":rain:",
    layout="wide",
    initial_sidebar_state="expanded"
)


#Page header/ logo
st.logo(image='Horizontal_RGB_294_White.png', icon_image='index2.png')  
st.header('Drought-related Yield Loss Estimates for Amhara Region, Ethiopia')

alt.themes.enable("dark")

st.sidebar.title('About')
with st.sidebar.expander("Click here"):
    st.info("This dashboard was built by the Climate Adaptation Research Program (CARP) study team in the Institute of Disaster Risk Management & Food Security Studies, Bahir Dar University to share research findings on the topic entitled “DROUGHT INSURANCE ZONE MAPPING AND RISK PROFILING IN AMHARA REGION, ETHIOPIA”. CARP promotes a new generation of applied climate adaptation research in Africa with a focus on the impacts and implications for disaster risk reduction policies and strategies. To learn more about our CARP project [visit this page](https://hats.arizona.edu/climate-adaptation-research-program-carp).To give a brief info about our project - PROBLEM: Risk profiling is a foundation to support decision making in risk-informed development investments. Although this is well recognized by several development and DRM related policy documents of Ethiopia, the desired transition towards the production and meaningful utilization of well-translated and applied risk knowledge is largely limited. The current risk profiling exercise primarily tries to satisfy the interests of national governments as if the responsibility to risk is bound to rest on the shoulders of these traditional actors. It overlooks to account risk information needs and interests of the private sector, particularly the insurance market. Enabling and expanding the existing responsibility domains for risk reduction involves the production and communication of risk information that is understandable and usable for different kinds of users. Targeting to address this development challenge, the main GOAL of our project is to identify unique spatial and temporal patterns of drought occurrences, in the study region, that define Unit Area Insurance (UAI) zones and generate detail account of agricultural risk and related yield loss accounting information for each defined UAI. While this is primarily relevant to inform the emerging weather index- and area yield- based insurance markets, it is also part of our goal to make sure that flexibility is built into our risk profiling approach for its aggregation at other risk reduction decision making scales. So that it remains useful to traditional actors such as local governments. The primary hazard that our risk profiling exercise focuses on is drought. DATA used: (1) Climate dataset: CHIRIPS monthly time series total rainfall data, covering 1981-2022 periods; (2) Yield dataset: FAO-WaPOR biomass production data, covering 2009-2022 periods; (3) Other geospatial datasets: FEWS NET Livelihood Zone and administrative boundary shapefiles. METHODS applied: (1) Probabilistic risk assessment methodology, adapted from UNDRR; (2) Generalized Extreme Value Distribution is used to establish a catalogue of drought extreme events; (3) Empirical approach is used to establish the relationship b/n crop-yield and rainfall deficits. Intended IMPACT: We hope to contribute to efforts that aim to promote meaningful applications of risk information and hence to an expanded domain of shared risk responsibility. Drought-related yield losses are reported at three levels: (1) Insurance zones which are defined by clustering pixel locations based on identifiable unique patterns of droughts using an ML cluster algorithm; (2) Livelihood zones are based on unique livelihood patterns of a location as defined by [FEWS NET](https://fews.net/east-africa/ethiopia/livelihood-zone-map/january-2018); and (3) Administrative zones of Amhara region. Users can select their preferred reporting level from the sidebar and explore each of the risk metrics. Maps shown in the second column of the main panel are expressed as relative losses in percent, relative to exposure, shown at the top; as well as absolute losses in KgDM/ha, shown at the bottom, same column. Users can hover over the map to see specific information. Note that the PML refers to Probable Maximum Loss – it represents the maximum yield loss that could be expected over a certain timeframe. The PML is always associated to a return period, for example PML10 is the maximum yield loss that could be expected with a chance of 9.52% each year, or with a chance of 39.35% over a 5-year timeframe or with a chance of 63.21% over a 10-year timeframe; you can use this formula 1-exponent of -t/T where small-t is the timeframe you want to know the chance, capital-T is the return period associated to the PML. (2) AAL refers to Annual Average Loss – represents the expected annual yield loss, averaged over longer timeframe. We followed UNDRR probabilistic risk assessment methodology, definitions and brief descriptions for similar risk related concepts used in this dashboard can be found [here](https://www.preventionweb.net/understanding-disaster-risk). For further details, please drop a message using the address provided at the bottom of the dashboard. All python codes are learned and adapted from the most generous free world data science community. We are particularly grateful for Streamlit Community Cloud and GitHub for the wonderful services we enjoyed. This work was funded by the Climate Adaptation Research Program, which is made possible by the generous support of the American people through the USAID Bureau for Humanitarian Assistance (Award# 720FDA20CA00006). The USAID administers the U.S. foreign assistance program providing economic and humanitarian assistance in more than 80 countries worldwide. The Climate Adaptation Research Program in Africa is coordinated by the Partners for Enhancing Resilience for People Exposed to Risks (PERIPERI-U) Network in the Centre for Collaboration in Africa at Stellenbosch University and the Humanitarian Assistance Technical Support initiative in the Bureau of Applied Research in Anthropology at the University of Arizona.")

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

# Dashboard Main Panel
col = st.columns((2.5, 4.5, 2.5), gap='medium')
selected_ML_gdf_sorted = selected_ML_gdf[['Zone-ID', 'l_metric', 'Exposure']].sort_values('Exposure', ascending=False)

with col[0]:
    st.markdown('##### Exposure')
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

# dataframe for choropleth map
selected_ML_gdf_loc = selected_ML_gdf.set_index('Zone-ID')

with col[1]:
    st.markdown('##### Yield Loss: Top(%); Bottom(Kg/ha)')
    choropleth = px.choropleth(selected_ML_gdf,
                               geojson = selected_ML_gdf_loc.geometry, 
                               locations = selected_ML_gdf_loc.index, 
                               color = 'Yield loss (%)', 
                               color_continuous_scale="Reds",
                               projection='mercator',
                               range_color=(selected_ML_gdf_loc['Yield loss (%)'].min(),
                                            selected_ML_gdf_loc['Yield loss (%)'].max()),
                               labels={'Yield loss (%)':''})
                                                                                       
    
    choropleth.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, 
                             template='plotly_dark', 
                             height=200,
                             legend=dict(orientation="v", yanchor="bottom", y=0.9, xanchor="right", x=0.5))
    choropleth.update_geos(fitbounds='locations', visible=False)
    st.plotly_chart(choropleth, template='streamlit', use_container_width=True)
    
    choropleth = px.choropleth(selected_ML_gdf,
                               geojson = selected_ML_gdf_loc.geometry, 
                               locations = selected_ML_gdf_loc.index, 
                               color = 'loss_abs', 
                               color_continuous_scale="Reds",
                               projection='mercator',
                               range_color=(selected_ML_gdf_loc.loss_abs.min(),
                                            selected_ML_gdf_loc.loss_abs.max()),
                               labels={'loss_abs':''})
    
    choropleth.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, 
                             template='plotly_dark', 
                             height=200,
                             legend=dict(orientation="v", yanchor="bottom", y=0.9, xanchor="right", x=0.5))
    choropleth.update_geos(fitbounds='locations', visible=False)
    st.plotly_chart(choropleth, template='streamlit', use_container_width=True)

# Top zones sorted by descending order of yield loss
selected_ML_gdf_sorted = selected_ML_gdf[['Zone-ID', 'l_metric', 'loss_rel', 'Yield loss (%)']].sort_values('Yield loss (%)', ascending=False)

with col[2]:
    st.markdown('##### Top Zones')
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


# Top 10 bad/good years by UaI zone
data = pd.read_csv('data_top_bad_good_years_by_uai.csv', index_col=[0])
years_str = data.columns[3:]
uai_code = [i for i in range(15)]

st.subheader('Top 10 Bad/Good Years by Insurance Zone')
uai_zone = st.selectbox('Select an Insurance zone code', uai_code)
col1, col2 = st.columns((1, 1))

with col1:
    st.markdown('##### Top 10 Bad Years')
    #uai_zone = st.selectbox('Select an Insurance zone code for bad years', uai_code)
    data_bad = data[data.CWW15==uai_zone][years_str].median().sort_values(ascending=False).reset_index().rename(columns={'index': 'Year', 0:'Rank'})
    st.dataframe(data_bad, 
                 column_order=("Year", "Rank"),
                 hide_index=True,
                 width=None,
                 use_container_width=True,
                 column_config={
                    "Year": st.column_config.TextColumn(
                        "Year",
                    ),
                    "Rank": st.column_config.ProgressColumn(
                        "Rank",
                        format="%.2f",
                        min_value=0,
                        max_value=max(data_bad.Rank),
                     )}
                )


with col2:
    st.markdown('##### Top 10 Good Years')
    #uai_zone = st.selectbox('Select an Insurance zone code for good years', uai_code)
    data_bad = data[data.CWW15==uai_zone][years_str].median().sort_values(ascending=False).reset_index().rename(columns={'index': 'Year', 0:'Rank2'})
    data_good = data_bad.copy()
    data_good['Rank']= 1 - data_bad.Rank2
    data_good = data_good.sort_values('Rank', ascending=False)
    st.dataframe(data_good, 
                 column_order=("Year", "Rank"),
                 hide_index=True,
                 width=None,
                 use_container_width=True,
                 column_config={
                    "Year": st.column_config.TextColumn(
                        "Year",
                    ),
                    "Rank": st.column_config.ProgressColumn(
                        "Rank",
                        format="%.2f",
                        min_value=0,
                        max_value=max(data_good.Rank),
                     )}
                )

st.subheader('Region-level Top 10 Bad/Good Years')
col1, col2 = st.columns((1, 1))
with col1:
    st.markdown('##### Top 10 Bad Years')
    #uai_zone = st.selectbox('Select an Insurance zone code for bad years', uai_code)
    data_bad = data[years_str].median().sort_values(ascending=False).reset_index().rename(columns={'index': 'Year', 0:'Rank'})
    st.dataframe(data_bad, 
                 column_order=("Year", "Rank"),
                 hide_index=True,
                 width=None,
                 use_container_width=True,
                 column_config={
                    "Year": st.column_config.TextColumn(
                        "Year",
                    ),
                    "Rank": st.column_config.ProgressColumn(
                        "Rank",
                        format="%.2f",
                        min_value=0,
                        max_value=max(data_bad.Rank),
                     )}
                )

with col2:
    st.markdown('##### Top 10 Good Years')
    #uai_zone = st.selectbox('Select an Insurance zone code for bad years', uai_code)
    data_bad = data[years_str].median().sort_values(ascending=False).reset_index().rename(columns={'index': 'Year', 0:'Rank2'})
    data_good = data_bad.copy()
    data_good['Rank']= 1 - data_bad.Rank2
    data_good = data_good.sort_values('Rank', ascending=False)
    
    st.dataframe(data_good, 
                 column_order=("Year", "Rank"),
                 hide_index=True,
                 width=None,
                 use_container_width=True,
                 column_config={
                    "Year": st.column_config.TextColumn(
                        "Year",
                    ),
                    "Rank": st.column_config.ProgressColumn(
                        "Rank",
                        format="%.2f",
                        min_value=0,
                        max_value=max(data_good.Rank),
                     )}
                )


st.markdown(" **Institute website:** https://www.bdu.edu.et/idrmfss **| Institute email:** IDRMFSSBDU@gmail.com **| Project PI email:** Tesfahun.Asmamaw@bdu.edu.et **| Outreach focal email:** Mossa.Endris@bdu.edu.et")

# Contact Form

with st.expander("Contact us"):
    with st.form(key='contact', clear_on_submit=True):
        
        email = st.text_input('Contact Email')
        st.text_area("Query","Please specify your request or general comment here")  
        
        submit_button = st.form_submit_button(label='Send Information')
        
