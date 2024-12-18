import numpy as np
import pandas as pd
import geopandas as gpd
from plotnine import *
import plotly.express as px
import streamlit as st 
import pycountry

def get_ISO_A3_code(country_name):
    try:
        
        country = pycountry.countries.lookup(country_name)
        return country.alpha_3
    except LookupError:
        return None  


st.set_page_config(layout='wide')
st.header("The History of Global Natural Gas Production")

#loading data
line_data=pd.read_csv('../data/transformed_natural_gas_production.csv')
map_data = pd.read_excel('../data/The history of global natural gas production.xlsx',sheet_name = 0)
world_map = gpd.read_file('../data/worldmap.geojson')
country_border = gpd.read_file('../data/countries.geojson')

#data manupilation
plot_map = world_map.merge(map_data , how='left' , left_on='SOVEREIGNT' , right_on='Country')
plot_map = plot_map[['SOVEREIGNT','Cumulative production','geometry']]
country_border = country_border.rename(columns={'ADMIN':'country'})

data = pd.read_csv('../data/tidy_gas.csv',index_col=0)
data['ISO_A3'] = data['country'].apply(get_ISO_A3_code)
data.loc[data['country'] == 'Russia', 'ISO_A3'] = 'RUS'
data.loc[data['country'] == 'Turkey', 'ISO_A3'] = 'TUR'
data.loc[data['country'] == 'Brunei', 'ISO_A3'] = 'BRN'
data.loc[data['country'] == 'East Timor', 'ISO_A3'] = 'TLS'
data['gas'] = pd.to_numeric(data['gas'],errors='coerce')
line_data = data

with st.sidebar:
    st.title("setting the data")
    select_form = st.selectbox("choose the visualization form",
        ["maps", "table",
        "line chart"])
    if select_form in ['line chart','table']  :
        select_countries = st.multiselect('Select up to 5 countries' , line_data['country'].unique(),max_selections=5)
        select_year = st.slider("Choose a year", 1900, 2022,value = 2022 )
    if select_form == 'maps' :
        show_single_year = st.checkbox('show single year')
        select_year = st.slider("Choose a year", 1900, 2022,value = 2022)


if select_form == "maps":
    if show_single_year:
        line_plot = line_data.query('Year == @select_year')
        fig = px.choropleth_mapbox(
            geojson = country_border, data_frame = line_data, color = "gas",
            featureidkey="properties.ISO_A3",
            locations = "ISO_A3",
            mapbox_style = "carto-positron",zoom = 1,
            color_continuous_scale=px.colors.sequential.Reds,
            hover_name = "country", hover_data = {"country": False },
            title = "Natural gas production by country, {}".format(select_year))
        
        fig.update_layout(
            width=2000,  
            height=800,  
            legend=dict(
                x=0,
                y=1,
                xanchor='left',
                yanchor='top'
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        fig = px.choropleth_mapbox(
            geojson = plot_map, data_frame = plot_map, color = "Cumulative production",
            featureidkey="properties.SOVEREIGNT",
            locations = "SOVEREIGNT",
            mapbox_style = "carto-positron",zoom = 1,
            color_continuous_scale=px.colors.sequential.Reds,
            hover_name = "SOVEREIGNT", hover_data = {"SOVEREIGNT": False},
            title = "Cumulative natural gas production by country, 1900-2022")

        fig.update_layout(
            width=2000,  
            height=800,  
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
    fig2.update_layout(
            width=2000,  
            height=800,  
        )

    st.plotly_chart(fig2)
    
elif select_form =='table':
    line_plot = line_data[line_data['country'].isin(select_countries)]
    line_plot = line_plot.query('Year <= @select_year')
    line_plot = line_plot.pivot(index='Year', columns='country', values='gas').sort_values('Year',ascending=False)
    st.dataframe(line_plot)



