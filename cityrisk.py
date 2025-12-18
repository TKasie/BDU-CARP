# encoding: utf-8
"""
Created on Wedensday Sep 25 9:04:04 2025

@author: HAWASSA Risk Profiling Team, Team Lead (Tesfahun Kasie)
"""
import time
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="Hawassa Risk Profiling Program",
    page_icon=":rain:",
    layout="wide",
    initial_sidebar_state="expanded"
)


#Page header/ logo
#st.logo(image='BDU-CARP-main/Horizontal_RGB_294_White.png', icon_image='BDU-CARP-main/index2.png')   
st.header('Hawassa Risk Profiling Program')
""
""
alt.themes.enable("dark")

st.sidebar.title('About')
with st.sidebar.expander("Click here"):
    st.info("This dashboard was built to share Hawassa City Risk Assessment Study outputs to facilitate discussion among city stakeholders around how to reduce risk and build resilience. Maps shown in the second column of the main panel are expressed as relative risk index scores, comparing an admin unit to all other admin units of the same level. Users can hover over the map to see specific info.")

# sidebars - choosing reporting levels and risk metrics type 
info_category = ['Hazard & Exposure', 'Social Vulnerability', 'Community Resilience', 'City Risk Index']
info = st.sidebar.selectbox('Select info category', info_category)

# data directories
eigen_data = "data/df_all_eigenvalues.parquet.gzip"
dfrisk_data = "data/df_risk_merged_gdf.shp"
hazarddf_data = "data/streamlit_hazard_df.parquet.gzip"
dim1df_data = "data/df_dim_1_merged.parquet.gzip"
dim2df_data = "data/df_dim_2_merged.parquet.gzip"
dim3df_data = "data/df_dim_3_merged.parquet.gzip"

@st.cache_data
def read_gdf(file_path):
    gdf = gpd.read_file(file_path)
    return gdf

# dataframes for selected sidebar items 'recovery_s', 'shock_ewi_','future_pla'
if info=='Hazard & Exposure':
    hazard_df = pd.read_parquet(hazarddf_data) 
    data_nat = hazard_df[hazard_df.risk_com=='Natural Hazard'].copy()
    data_eday = hazard_df[hazard_df.risk_com=='Everyday Hazard'].copy()
    data_str = hazard_df[hazard_df.risk_com=='Stressor'].copy()

    df_hrisk_top = read_gdf(dfrisk_data).set_index('kebele') 
    df_hrisk_top['kebele2'] = df_hrisk_top.index
    df_eigen_top = pd.read_parquet(eigen_data)
    
    weather_icons = {
        "Climate change": "🌡️",
        "Warning": "🔔",
        "Plan": "📝",
        "Recovery": "🔄",
        "Flooding": "⛈️", 
        "Economic volatility": "📈",
        "Env'tal health prob.": "🔴",
        "Climate change": "🌡️",
        "Crime": "🚨",
    }
    
    cols = st.columns([1.5, 2, 2])
    with cols[0]:
        weather_name = (data_nat.groupby('shock_type')['pop_aff_norm'].mean().sort_values(ascending=False).head(1).reset_index()["shock_type"][0]
                       )
        st.metric(
            "Most common natural hazard",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )
    with cols[1]:
        weather_name = (data_eday.groupby('shock_type')['pop_aff_norm'].mean().sort_values(ascending=False).head(1).reset_index()["shock_type"][0]
                       )
        st.metric(
            "Most common Everyday hazard",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )
    with cols[2]:
        weather_name = (data_str.groupby('shock_type')['pop_aff_norm'].mean().sort_values(ascending=False).head(1).reset_index()["shock_type"][0]
                       )
        st.metric(
            "Most common Stressor",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )
    ""
    ""

    cols = st.columns([1.5, 2, 2])
    with cols[0]:
        weather_name = (data_nat.groupby('shock_type')['imp_sev_norm'].mean().sort_values(ascending=False).head(1).reset_index()["shock_type"][0]
                       )
        st.metric(
            "Most severe natural hazard",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )
    with cols[1]:
        weather_name = (data_eday.groupby('shock_type')['imp_sev_norm'].mean().sort_values(ascending=False).head(1).reset_index()["shock_type"][0]
                       )
        st.metric(
            "Most severe Everyday hazard",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )
    with cols[2]:
        weather_name = (data_str.groupby('shock_type')['imp_sev_norm'].mean().sort_values(ascending=False).head(1).reset_index()["shock_type"][0]
                       )
        st.metric(
            "Most severe Stressor",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )
    ""
    ""

    cols = st.columns(3)
    with cols[0]:
        weather_name = round(df_hrisk_top.recovery_s.mul(100).mean(), 2)
        st.metric(
            "Recovery rate (%)",
            f"{weather_icons['Recovery']} {weather_name}", weather_name-weather_name,
        )

    with cols[1]:
        weather_name = round(df_hrisk_top.shock_ewi_.mul(100).mean(), 2)
        st.metric(
            "EWI coverage (%)",
            f"{weather_icons['Warning']} {weather_name}", weather_name-weather_name,
        )
    with cols[2]:
        weather_name = round(df_hrisk_top.future_pla.mul(100).mean(), 2)
        st.metric(
            "Pop. with Future Plan (%)",
            f"{weather_icons['Plan']} {weather_name}", weather_name-weather_name,
        )
    ""
    ""
    
    cols = st.columns(1)
    with cols[0].container():
        st.markdown('#### Dimension-level Average Hazard & Exposure Index Scores')
        bars = alt.Chart(df_hrisk_top).mark_bar(color='darkred').encode(
            y=alt.Y('HRF:Q').stack('zero').title('Hazard & Exposure (Index Score)'),
            x=alt.X('kebele2:N', sort='-y'),
        )
        text = alt.Chart(df_hrisk_top).mark_text(dy=15, dx=3, color='white', align='center', fontSize=10, fontStyle='Italic',
                                                 fontWeight='bold').encode(
            y=alt.Y('HRF:Q').stack('zero'),
            x=alt.X('kebele2:N', sort='-y'),
            text=alt.Text('HRF:Q', format='.0f')
        )
        bars_text = (bars + text)
        st.altair_chart(bars_text, use_container_width=True)
        
        cols = st.columns((2, 4, 3), gap='medium')
        with cols[0].container():
            "### Top kebeles"
            df = df_hrisk_top.groupby('kebele2')['HRF'].mean().sort_values(ascending=False).reset_index()
            st.dataframe(df)
        with cols[1].container():
            "### Hazard & Exposure Index Scores"
            fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                                locations=df_hrisk_top.index,
                                color = 'HRF', 
                                color_continuous_scale="Reds",
                                projection='mercator',
                                range_color=(df_hrisk_top['HRF'].min(),
                                             df_hrisk_top['HRF'].max()),
                                labels={'HRF':''})
            fig.update_layout(template='plotly_dark')
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig)

        with cols[2].container():
            "### Top driving factors"
            df = df_eigen_top[df_eigen_top.risk_com=='Hazard & Exposure'][['ind_name', 'ind_eigenvalue']]
            st.dataframe(df)
        
        cols = st.columns(1)
        with cols[0].container():
            "### Reported Impact Severity for Natural Hazards"
            df_nat2 = data_nat[data_nat.risk_com=='Natural Hazard'].copy()
            df_nat2 = df_nat2[df_nat2.shock_type!='Subsidence'].copy()
            df_nat2.loc[:, 'total_reported'] = df_nat2.groupby('kebele')['imp_sev_norm_l'].transform('sum')
            df_nat2['keb_share'] = df_nat2['imp_sev_norm_l']/df_nat2['total_reported']
            stacked_chart = alt.Chart(df_nat2).mark_bar().encode(
                x=alt.X('kebele:N').title("Kebele").sort(field="subcity_code", order='ascending'),
                y=alt.Y('keb_share:Q').title(None).scale(domain=[0, 1]),
                color=alt.Color('shock_type:N').title("Natural Hazard"),
                tooltip=['subcity_code', 'kebele', 'shock_type', 'keb_share']
            ).properties(
                width=800,
                height=350, 
                title=alt.Title(
                    text="Reported Impact Severity for Natural Hazards: Hawassa City Risk Assessment Program (2025)",
                    subtitle="Min-Max Normalization was first applied on kebele-hazard level data; Share of scores were then calculated for each hazard, representing their relative importance for a kebele",
                    anchor='start'
                )
            ).configure_axisY(
                domain=True,
                ticks=True,
                offset=10, 
            ).configure_axisX(
                grid=True,
            ).configure_view(
                stroke=None
            )
            st.altair_chart(stacked_chart, use_container_width=True)


            
        cols = st.columns(1)
        with cols[0].container():
            "### Reported Impact Severity for Everyday Hazards"
            df_eday2 = data_eday[data_eday.risk_com=='Everyday Hazard'].copy()
            #df_nat2 = df_nat2[df_nat2.shock_type!='Subsidence'].copy()
            df_eday2.loc[:, 'total_reported'] = df_eday2.groupby('kebele')['imp_sev_norm_l'].transform('sum')
            df_eday2['keb_share'] = df_eday2['imp_sev_norm_l']/df_eday2['total_reported']
            stacked_chart = alt.Chart(df_eday2).mark_bar().encode(
                x=alt.X('kebele:N').title("Kebele").sort(field="subcity_code", order='ascending'),
                y=alt.Y('keb_share:Q').title(None).scale(domain=[0, 1]),
                color=alt.Color('shock_type:N').title("Everyday Hazard"),
                tooltip=['subcity_code', 'kebele', 'shock_type', 'keb_share']
            ).properties(
                width=800,
                height=350, 
                title=alt.Title(
                    text="Reported Impact Severity for Everyday Hazards: Hawassa City Risk Assessment Program (2025)",
                    subtitle="Min-Max Normalization was first applied on kebele-hazard level data; Share of scores were then calculated for each hazard, representing their relative importance for a kebele",
                    anchor='start'
                )
            ).configure_axisY(
                domain=True,
                ticks=True,
                offset=10, 
            ).configure_axisX(
                grid=True,
            ).configure_view(
                stroke=None
            )
            st.altair_chart(stacked_chart, use_container_width=True)


        cols = st.columns(1)
        with cols[0].container():
            "### Reported Impact Severity for Stressors"
            df_str2 = data_str[data_str.risk_com=='Stressor'].copy()
            to_10 = df_str2.groupby('shock_type')['imp_sev_norm'].mean().sort_values(ascending=False).head(10).index.tolist()
            df_str2 = df_str2[df_str2.shock_type.isin(to_10)].copy()
            df_str2.loc[:, 'total_reported'] = df_str2.groupby('kebele')['imp_sev_norm_l'].transform('sum')
            df_str2['keb_share'] = df_str2['imp_sev_norm_l']/df_str2['total_reported']
            stacked_chart = alt.Chart(df_str2).mark_bar().encode(
                x=alt.X('kebele:N').title("Kebele").sort(field="subcity_code", order='ascending'),
                y=alt.Y('keb_share:Q').title(None).scale(domain=[0, 1]),
                color=alt.Color('shock_type:N').title("Stressor"),
                tooltip=['subcity_code', 'kebele', 'shock_type', 'keb_share']
            ).properties(
                width=800,
                height=350, 
                title=alt.Title(
                    text="Reported Impact Severity for Stressors: Hawassa City Risk Assessment Program (2025)",
                    subtitle="Min-Max Normalization was first applied on kebele-hazard level data; Share of scores were then calculated for each hazard, representing their relative importance for a kebele",
                    anchor='start'
                )
            ).configure_axisY(
                domain=True,
                ticks=True,
                offset=10, 
            ).configure_axisX(
                grid=True,
            ).configure_view(
                stroke=None
            )
            st.altair_chart(stacked_chart, use_container_width=True)
            
        cols = st.columns(3)
        
        
        with cols[0].container():
            "#### Reported Prevalence (Natural Hazards)"
            ""
            data_nat3=data_nat.rename(columns={"pop_aff_norm_l":"Prevalence"})
            my_chart = px.sunburst(
                data_nat3,
                path = ['shock_type', 'subcity_name', 'kebele'],
                values = 'Prevalence',
                color='Prevalence', 
                color_continuous_scale='rdbu_r',
            )
            st.plotly_chart(my_chart, use_container_width=True)
        with cols[1].container():
            "#### Reported Prevalence (Everyday Hazards)"
            ""
            data_eday3=data_eday.rename(columns={"pop_aff_norm_l":"Prevalence"})
            my_chart = px.sunburst(
                data_eday3,
                path = ['shock_type', 'subcity_name', 'kebele'],
                values = 'Prevalence',
                color='Prevalence', 
                color_continuous_scale='rdbu_r',
            )
            st.plotly_chart(my_chart, use_container_width=True)
        with cols[2].container():
            "#### Reported Prevalence (Stressors)"
            ""
            data_str3=data_str.rename(columns={"pop_aff_norm_l":"Prevalence"})
            my_chart = px.sunburst(
                data_str3,
                path = ['shock_type', 'subcity_name', 'kebele'],
                values = 'Prevalence',
                color='Prevalence', 
                color_continuous_scale='rdbu_r',
            )
            st.plotly_chart(my_chart, use_container_width=True)

if info=='Social Vulnerability':
    ""
    ""
    df_hrisk_top = gpd.read_file(dfrisk_data).set_index('kebele') 
    df_hrisk_top['kebele2'] = df_hrisk_top.index
    df_eigen_top = pd.read_parquet(eigen_data)
    cols = st.columns(1)
    with cols[0].container():
        st.markdown('#### Dimension-level Average Social Vulnerability Index Scores')
        bars = alt.Chart(df_hrisk_top).mark_bar(color='darkred').encode(
            y=alt.Y('Social Vul:Q').stack('zero').title('Social Vulnerability Index (SoVI)'),
            x=alt.X('kebele2:N', sort='-y'),
        )
        text = alt.Chart(df_hrisk_top).mark_text(dy=15, dx=3, color='white', align='center', fontSize=10, fontStyle='Italic',
                                                 fontWeight='bold').encode(
            y=alt.Y('Social Vul:Q').stack('zero'),
            x=alt.X('kebele2:N', sort='-y'),
            text=alt.Text('Social Vul:Q', format='.0f')
        )
        bars_text = (bars + text)
        st.altair_chart(bars_text, use_container_width=True)
    
    cols = st.columns((2, 4, 3), gap='medium')
    with cols[0].container():
        "### Top kebeles"
        df = df_hrisk_top.groupby('kebele2')['Social Vul'].mean().sort_values(ascending=False).reset_index()
        st.dataframe(df)
    
    with cols[1].container():
        "### Social Vulnerability Index Scores"
        fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                            locations=df_hrisk_top.index,
                            color = 'Social Vul', 
                            color_continuous_scale="Reds",
                            projection='mercator',
                            range_color=(df_hrisk_top['Social Vul'].min(),
                                         df_hrisk_top['Social Vul'].max()),
                            labels={'Social Vul':''})
        fig.update_layout(template='plotly_dark')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
    
    with cols[2].container():
        "### Top driving factors"
        df = df_eigen_top[df_eigen_top.risk_com=='Social Vulnerability'][['ind_name', 'ind_eigenvalue']]
        st.dataframe(df)

if info=='Community Resilience':
    ""
    ""
    df_hrisk_top = gpd.read_file(dfrisk_data).set_index('kebele') 
    df_hrisk_top['kebele2'] = df_hrisk_top.index
    df_eigen_top = pd.read_parquet(eigen_data)
    cols = st.columns(1)
    with cols[0].container():
        st.markdown('#### Dimension-level Average Community Resilience Capacity Index Scores')
        bars = alt.Chart(df_hrisk_top).mark_bar(color='darkred').encode(
            y=alt.Y('Community:Q').stack('zero').title('Community Resilience Index (CoRI)'),
            x=alt.X('kebele2:N', sort='-y'),
        )
        text = alt.Chart(df_hrisk_top).mark_text(dy=15, dx=3, color='white', align='center', fontSize=10, fontStyle='Italic',
                                                 fontWeight='bold').encode(
            y=alt.Y('Community:Q').stack('zero'),
            x=alt.X('kebele2:N', sort='-y'),
            text=alt.Text('Community:Q', format='.0f')
        )
        bars_text = (bars + text)
        st.altair_chart(bars_text, use_container_width=True)

    cols = st.columns(1)
    df_dim3 = pd.read_parquet(dim3df_data)
    df_dim3.loc[:, 'fscore_norm2'] = df_dim3['fscore_norm'].mul(100).round(0)
    df_dim3_a = df_dim3.groupby(['kebele', 'risk_com'])[['fscore_norm2']].mean().reset_index()
    with cols[0].container():
        st.markdown('#### Comparing Resilience Capacity Types')
        bars = alt.Chart(df_dim3_a).mark_bar().encode(
            x=alt.X('sum(fscore_norm2):Q').title('Sum of Index Score').stack('zero'),
            y=alt.Y('kebele:N', sort='-x'),
            color=alt.Color('risk_com').title('Community Resilience')
        )
        text = alt.Chart(df_dim3_a).mark_text(dx=-15, dy=3, color='white', align='center', fontSize=10, fontStyle='Italic',
                                              fontWeight='normal').encode(
            x=alt.X('sum(fscore_norm2):Q').stack('zero'),
            y=alt.Y('kebele:N', sort='-x'),
            detail='risk_com:N',
            text=alt.Text('sum(fscore_norm2):Q', format='.0f')
        )
        bars_text = (bars + text)
        st.altair_chart(bars_text, use_container_width=True)
    
    """
    ### Absorptive Capacity
    """
    cols = st.columns((2, 4, 3), gap='medium')
    with cols[0].container():
        "#### Top kebeles"
        df = df_hrisk_top.groupby('kebele2')['Absorptive'].mean().sort_values(ascending=False).reset_index()
        st.dataframe(df)
    with cols[1].container():
        "#### Absorptive Capacity Index Scores"
        fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                            locations=df_hrisk_top.index,
                            color = 'Absorptive', 
                            color_continuous_scale="Reds",
                            projection='mercator',
                            range_color=(df_hrisk_top['Absorptive'].min(),
                                         df_hrisk_top['Absorptive'].max()),
                            labels={'Absorptive':''})
        fig.update_layout(template='plotly_dark')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
    
    with cols[2].container():
        "#### Top driving factors"
        df = df_eigen_top[df_eigen_top.risk_com=='Absorptive Capacity'][['ind_name', 'ind_eigenvalue']]
        st.dataframe(df)
    """
    ### Adaptive Capacity
    """
    cols = st.columns((2, 4, 3), gap='medium')
    with cols[0].container():
        "#### Top kebeles"
        df = df_hrisk_top.groupby('kebele2')['Adaptive C'].mean().sort_values(ascending=False).reset_index()
        st.dataframe(df)
    
    with cols[1].container():
        "#### Adaptive Capacity Index Scores"
        fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                            locations=df_hrisk_top.index,
                            color = 'Adaptive C', 
                            color_continuous_scale="Reds",
                            projection='mercator',
                            range_color=(df_hrisk_top['Adaptive C'].min(),
                                         df_hrisk_top['Adaptive C'].max()),
                            labels={'Adaptive C':''})
        fig.update_layout(template='plotly_dark')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
    
    with cols[2].container():
        "#### Top driving factors"
        df = df_eigen_top[df_eigen_top.risk_com=='Adaptive Capacity'][['ind_name', 'ind_eigenvalue']]
        st.dataframe(df)
    """
    ### Preventive Capacity
    """
    cols = st.columns((2, 4, 3), gap='medium')
    with cols[0].container():
        "#### Top kebeles"
        df = df_hrisk_top.groupby('kebele2')['Preventive'].mean().sort_values(ascending=False).reset_index()
        st.dataframe(df)
    with cols[1].container():
        "#### Preventive Capacity Index Scores"
        fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                            locations=df_hrisk_top.index,
                            color = 'Preventive', 
                            color_continuous_scale="Reds",
                            projection='mercator',
                            range_color=(df_hrisk_top['Preventive'].min(),
                                         df_hrisk_top['Preventive'].max()),
                            labels={'Preventive':''})
        fig.update_layout(template='plotly_dark')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
    with cols[2].container():
        "#### Top driving factors"
        df = df_eigen_top[df_eigen_top.risk_com=='Preventive Capacity'][['ind_name', 'ind_eigenvalue']]
        st.dataframe(df)
   
    """
    ### Anticipatory Capacity
    """
    cols = st.columns((2, 4, 3), gap='medium')
    with cols[0].container():
        "#### Top kebeles"
        df = df_hrisk_top.groupby('kebele2')['Anticipato'].mean().sort_values(ascending=False).reset_index()
        st.dataframe(df)
    with cols[1].container():
        "#### Anticipatory Capacity Index Scores"
        fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                            locations=df_hrisk_top.index,
                            color = 'Anticipato', 
                            color_continuous_scale="Reds",
                            projection='mercator',
                            range_color=(df_hrisk_top['Anticipato'].min(),
                                         df_hrisk_top['Anticipato'].max()),
                            labels={'Anticipato':''})
        fig.update_layout(template='plotly_dark')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
    with cols[2].container():
        "#### Top driving factors"
        df = df_eigen_top[df_eigen_top.risk_com=='Anticipatory Capacity'][['ind_name', 'ind_eigenvalue']]
        st.dataframe(df)
    """
    ### Transformative Capacity
    """
    cols = st.columns((2, 4, 3), gap='medium')
    with cols[0].container():
        "#### Top kebeles"
        df = df_hrisk_top.groupby('kebele2')['Transforma'].mean().sort_values(ascending=False).reset_index()
        st.dataframe(df)
    with cols[1].container():
        "#### Transformative Capacity Index Scores"
        fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                            locations=df_hrisk_top.index,
                            color = 'Transforma', 
                            color_continuous_scale="Reds",
                            projection='mercator',
                            range_color=(df_hrisk_top['Transforma'].min(),
                                         df_hrisk_top['Transforma'].max()),
                            labels={'Transforma':''})
        fig.update_layout(template='plotly_dark')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)
    with cols[2].container():
        "#### Top driving factors"
        df = df_eigen_top[df_eigen_top.risk_com=='Transformative Capacity'][['ind_name', 'ind_eigenvalue']]
        st.dataframe(df)

if info=='City Risk Index':
    ""
    ""
    df_hrisk_top = gpd.read_file(dfrisk_data)
    df_hrisk_top['kebele2'] = df_hrisk_top['kebele']
    df_hrisk_top = df_hrisk_top.set_index('kebele2') 
    df_eigen_top = pd.read_parquet(eigen_data)
    
    cols = st.columns(1)
    with cols[0].container():
        st.markdown('#### Aggregate Average City Risk Index Scores')
        bars = alt.Chart(df_hrisk_top).mark_bar(color='darkred').encode(
            y=alt.Y('CRI:Q').stack('zero').title('City Risk Index (CRI)'),
            x=alt.X('kebele:N', sort='-y'),
        )
        text = alt.Chart(df_hrisk_top).mark_text(dy=15, dx=3, color='white', align='center', fontSize=10, fontStyle='Italic',
                                                 fontWeight='bold').encode(
            y=alt.Y('CRI:Q').stack('zero'),
            x=alt.X('kebele:N', sort='-y'),
            text=alt.Text('CRI:Q', format='.0f')
        )
        bars_text = (bars + text)
        st.altair_chart(bars_text, use_container_width=True)
    
    cols = st.columns(1)
    with cols[0].container():
        "### City Risk Index Scores"
        fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                            locations=df_hrisk_top.index,
                            color = 'CRI', 
                            color_continuous_scale="Reds",
                            projection='mercator',
                            range_color=(df_hrisk_top['CRI'].min(),
                                         df_hrisk_top['CRI'].max()),
                            labels={'CRI':''})
        fig.update_layout(template='plotly_dark')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)

    df_rr2 = pd.melt(df_hrisk_top, id_vars='kebele', value_vars=['HRF', 'CRF', 'CRI'], var_name='Risk Factor',
                     value_name='Risk Score')

    cols = st.columns(1)
    with cols[0].container():
        "### Risk Factors driving the CRI"
        bars = alt.Chart(df_rr2).mark_bar().encode(
            y=alt.Y('sum(Risk Score):Q').stack('zero').title('Sum of Index Score'),
            x=alt.X('kebele:N', sort='-y'),
            color=alt.Color('Risk Factor').title('Risk Factor')
        )
        text = alt.Chart(df_rr2).mark_text(dy=15, dx=3, color='white', align='center', fontSize=10, fontStyle='Italic',
                                           fontWeight='bold').encode(
            y=alt.Y('sum(Risk Score):Q').stack('zero'),
            x=alt.X('kebele:N', sort='-y'),
            detail='Risk Factor:N',
            text=alt.Text('sum(Risk Score):Q', format='.0f')
        )
        bars_text = (bars + text)
        st.altair_chart(bars_text, use_container_width=True)

    cols = st.columns(1)
    with cols[0].container():
        "### Hazard Vs Community Risk Factors"
        bars = alt.Chart(df_rr2[df_rr2['Risk Factor'] !='CRI']).mark_bar().encode(
            x=alt.X('sum(Risk Score):Q').stack('zero').title('Sum of Index Score'),
            y=alt.Y('kebele:N', sort='-x'),
            color=alt.Color('Risk Factor').title('Risk Factor')
        )
        text = alt.Chart(df_rr2[df_rr2['Risk Factor']!='CRI']).mark_text(dy=3, dx=-15, color='white', align='center',
                                                                         fontSize=10,
                                                                         fontStyle='Italic', fontWeight='bold').encode(
            x=alt.X('sum(Risk Score):Q').stack('zero'),
            y=alt.Y('kebele:N', sort='-x'),
            detail='Risk Factor:N',
            text=alt.Text('sum(Risk Score):Q', format='.0f')
        )
        bars_text = (bars + text)
        st.altair_chart(bars_text, use_container_width=True)

    cols = st.columns(1)
    with cols[0].container():
        "### Disaster Resilience Zone Desigination"
        fig = px.choropleth(df_hrisk_top, geojson=df_hrisk_top.geometry,
                            locations=df_hrisk_top.index,
                            color = 'zones_3', 
                            color_continuous_scale="Oranges",
                            projection='mercator',
                            #range_color=(df_hrisk_top['HRF'].min(),
                                        # df_hrisk_top['HRF'].max()),
                            labels={'zones_3':''})
        fig.update_layout(template='plotly_dark')
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig)

    cols = st.columns(1)
    with cols[0].container():
        "### Zone A: Disaster Resilience Zones by Risk Factors"
        data = df_hrisk_top.reset_index()[['kebele', 'HRF', 'CRF', 'CRI', 'zones_3']].copy()
        data_ab = pd.pivot_table(data, index=['kebele', 'zones_3'], values=['HRF', 'CRF', 'CRI'], aggfunc='mean').reset_index()
        bars1 = alt.Chart(data_ab[data_ab.zones_3=='Zone A']).mark_bar().encode(
            x=alt.X('HRF:Q').title('Hazard Risk Factors (HRF)'),
            y=alt.Y('kebele:N', sort='-x'),
            color=alt.Color('zones_3').title('Zone Designation')
        )
        bars2 = alt.Chart(data_ab[data_ab.zones_3=='Zone A']).mark_bar().encode(
            x=alt.X('CRF:Q').title('Community Risk Factors (CRF)'),
            y=alt.Y('kebele:N', sort='-x'),
            color=alt.Color('zones_3').title('Zone Designation')
        )
        bar1_bar2 = (bars1 | bars2)
        st.altair_chart(bar1_bar2, use_container_width=True)

    cols = st.columns(1)
    with cols[0].container():
        "### Zone B: Disaster Resilience Zones by Risk Factors"
        data = df_hrisk_top.reset_index()[['kebele', 'HRF', 'CRF', 'CRI', 'zones_3']].copy()
        data_ab = pd.pivot_table(data, index=['kebele', 'zones_3'], values=['HRF', 'CRF', 'CRI'], aggfunc='mean').reset_index()
        bars1 = alt.Chart(data_ab[data_ab.zones_3=='Zone B']).mark_bar().encode(
            x=alt.X('HRF:Q').title('Hazard Risk Factors (HRF)'),
            y=alt.Y('kebele:N', sort='-x'),
            color=alt.Color('zones_3').title('Zone Designation')
        )
        bars2 = alt.Chart(data_ab[data_ab.zones_3=='Zone B']).mark_bar().encode(
            x=alt.X('CRF:Q').title('Community Risk Factors (CRF)'),
            y=alt.Y('kebele:N', sort='-x'),
            color=alt.Color('zones_3').title('Zone Designation')
        )
        bar1_bar2 = (bars1 | bars2)
        st.altair_chart(bar1_bar2, use_container_width=True)

    cols = st.columns(1)
    with cols[0].container():
        "### Zone C: Disaster Resilience Zones by Risk Factors"
        data = df_hrisk_top.reset_index()[['kebele', 'HRF', 'CRF', 'CRI', 'zones_3']].copy()
        data_ab = pd.pivot_table(data, index=['kebele', 'zones_3'], values=['HRF', 'CRF', 'CRI'], aggfunc='mean').reset_index()
        bars1 = alt.Chart(data_ab[data_ab.zones_3=='Zone C']).mark_bar().encode(
            x=alt.X('HRF:Q').title('Hazard Risk Factors (HRF)'),
            y=alt.Y('kebele:N', sort='-x'),
            color=alt.Color('zones_3').title('Zone Designation')
        )
        bars2 = alt.Chart(data_ab[data_ab.zones_3=='Zone C']).mark_bar().encode(
            x=alt.X('CRF:Q').title('Community Risk Factors (CRF)'),
            y=alt.Y('kebele:N', sort='-x'),
            color=alt.Color('zones_3').title('Zone Designation')
        )
        bar1_bar2 = (bars1 | bars2)
        st.altair_chart(bar1_bar2, use_container_width=True)
