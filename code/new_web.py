import numpy as np
import pandas as pd
import geopandas as gpd
from plotnine import *
import plotly.express as px
import streamlit as st 
import pycountry
def get_country_official_name(country_name):
    try:
        # 使用 pycountry 获取国家对象
        country = pycountry.countries.lookup(country_name)
        return country.official_name if hasattr(country, 'official_name') else country.name
    except LookupError:
        return country_name


st.set_page_config(layout='wide')
st.header("The History of Global Natural Gas Production")

#loading data
line_data=pd.read_csv('../data/transformed_natural_gas_production.csv')
map_data = pd.read_excel('../data/The history of global natural gas production.xlsx',sheet_name = 0)
world_map = gpd.read_file('../data/worldmap.geojson')
line_data.replace('United States','United States of America')
#data manupilation
plot_map = world_map.merge(map_data , how='left' , left_on='SOVEREIGNT' , right_on='Country')
plot_map = plot_map[['SOVEREIGNT','Cumulative production','geometry']]
#line_data['country'] = line_data['country'].apply(get_country_official_name)
with st.sidebar:
    st.title("setting the data")
    select_form = st.selectbox("choose the visualization form",
        ["maps", "table",
        "line chart"])
    if select_form in ['line chart','table']  :
        select_countries = st.multiselect('Select up to 5 countries' , line_data['country'].unique(),max_selections=5)
        select_year = st.slider("Choose a year", 1900, 2022)
    if select_form == 'maps' :
        show_single_year = st.checkbox('show single year')
        select_year = st.slider("Choose a year", 1900, 2022)


if select_form == "maps":
    if show_single_year:
        line_plot = line_data.query('Year == @select_year')
        fig = px.choropleth_mapbox(
            geojson = world_map, data_frame = line_plot, color = "gas",
            featureidkey="properties.SOVEREIGNT",
            locations = "country",
            mapbox_style = "carto-positron",zoom = 1,
            color_continuous_scale = 'blues',
            title = "world gas production by countries")
        st.plotly_chart(fig)
    else:
        fig = px.choropleth_mapbox(
            geojson = plot_map, data_frame = plot_map, color = "Cumulative production",
            featureidkey="properties.SOVEREIGNT",
            locations = "SOVEREIGNT",
            mapbox_style = "carto-positron",zoom = 1,
            color_continuous_scale = 'YlOrRd',
            hover_name = "SOVEREIGNT", hover_data = {"SOVEREIGNT": False},
            title = "Cumulative natural gas production by country, 1900-2022")

        fig.update_layout(
            width=2000,  # 设置图的宽度，单位为像素
            height=800,  # 设置图的高度，单位为像素
            legend=dict(
                x=0,
                y=1,
                xanchor='left',
                yanchor='top'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif select_form == "line chart":
    if not select_countries:
        select_countries=['United States', 'Russia', 'Canada']

    line_plot = line_data[line_data['country'].isin(select_countries)]
    line_plot = line_plot.query('Year <= @select_year')
    
    fig2 = px.area(
        line_plot,
        x="Year",
        y="gas",
        color="country",  
        title="Natural gas production by country, 1900-{}".format(select_year),
        labels={"gas": "Production(Ej)", "Year": "Year"})


    st.plotly_chart(fig2)
    
elif select_form =='table':
    line_plot = line_data[line_data['country'].isin(select_countries)]
    line_plot = line_plot.query('Year <= @select_year')
    line_plot['diff'] = line_plot['gas'].diff()
    st.dataframe(line_plot)



