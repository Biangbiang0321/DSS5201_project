import numpy as np
import pandas as pd
import geopandas as gpd
from plotnine import *
import plotly.express as px
import streamlit as st 

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

st.header("The History of Global Natural Gas Production")

map_data = pd.read_excel('../data/The history of global natural gas production.xlsx',sheet_name = 0)
world_map = gpd.read_file('../data/worldmap.geojson')
plot_map = world_map.merge(map_data , how='left' , left_on='SOVEREIGNT' , right_on='Country')
plot_map = plot_map.replace(np.NaN,0)
plot_map = plot_map[['SOVEREIGNT','Cumulative production','geometry']]


fig = px.choropleth_mapbox(
    geojson = plot_map, data_frame = plot_map, color = "Cumulative production",
    featureidkey="properties.SOVEREIGNT",
    locations = "SOVEREIGNT",
    mapbox_style = "carto-positron",zoom = 1,
    color_continuous_scale = 'YlOrRd',
    hover_name = "SOVEREIGNT", hover_data = {"SOVEREIGNT": False},
    title = "Cumulative natural gas production by country, 1900-2022")

fig.update_layout(
    legend=dict(
        x=0,     # 图例的横向位置，0 表示最左
        y=1,     # 图例的纵向位置，1 表示最上
        xanchor='left',  # 以图例框的左边缘对齐
        yanchor='top'    # 以图例框的上边缘对齐
    )
)
st.plotly_chart(fig)