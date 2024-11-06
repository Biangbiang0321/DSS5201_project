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


if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True  # 设置标记
    data = pd.read_csv('../data/tidy_gas.csv',index_col=0)
    country_border = gpd.read_file('../data/countries.geojson')
    country_border = country_border.rename(columns={'ADMIN':'country'})
    data_with_border = data.merge(country_border,how='left',on='country')

    found = []
    not_found=[]
    for j in data_with_border[data_with_border['ISO_A2'].isna()]['country'].unique():
        find = 0
        print('searching for any country name containing {}…………\n'.format(j))
        for i in country_border['country'].unique():
            if j in i :
                print('yes there is {}\n'.format(i))
                find = 1
                found.append((i,j))
        if find == 0:
            print('no there is  no {}\n'.format(j))
            not_found.append(j)

    for i,j in found:
        data_with_border.loc[data_with_border['country'] == j,['ISO_A3','ISO_A2','geometry']] = country_border[country_border['country'] ==i ][['ISO_A3','ISO_A2','geometry']].values
    data_with_border_no_border = data_with_border[data_with_border['ISO_A2'].isna()]
    data_with_border = data_with_border[~data_with_border['ISO_A2'].isna()]
    data_with_border = gpd.GeoDataFrame(data_with_border,geometry='geometry')
    data_with_border = data_with_border[data_with_border['gas'].apply(is_float)]
    data_with_border['gas'] = data_with_border['gas'].astype(float)




data = pd.read_csv('../data/tidy_gas.csv',index_col=0)
country_border = gpd.read_file('../data/countries.geojson')
country_border = country_border.rename(columns={'ADMIN':'country'})
data_with_border = data.merge(country_border,how='left',on='country')

found = []
not_found=[]
for j in data_with_border[data_with_border['ISO_A2'].isna()]['country'].unique():
    find = 0
    print('searching for any country name containing {}…………\n'.format(j))
    for i in country_border['country'].unique():
        if j in i :
            print('yes there is {}\n'.format(i))
            find = 1
            found.append((i,j))
    if find == 0:
        print('no there is  no {}\n'.format(j))
        not_found.append(j)

for i,j in found:
    data_with_border.loc[data_with_border['country'] == j,['ISO_A3','ISO_A2','geometry']] = country_border[country_border['country'] ==i ][['ISO_A3','ISO_A2','geometry']].values
data_with_border_no_border = data_with_border[data_with_border['ISO_A2'].isna()]
data_with_border = data_with_border[~data_with_border['ISO_A2'].isna()]
data_with_border = gpd.GeoDataFrame(data_with_border,geometry='geometry')
data_with_border = data_with_border[data_with_border['gas'].apply(is_float)]
data_with_border['gas'] = data_with_border['gas'].astype(float)



with st.sidebar:
    st.title("setting the data")
    select_year = st.slider("Choose a year", 1900, 2023)
    select_countrys = st.multiselect('Select up to 5 countries' , data_with_border['country'].unique(),max_selections=5)
    select_form = st.selectbox("choose the visualization form",
        ["maps", "chart",
        "line chart "])




plot_data = data_with_border[data_with_border['Year'] == select_year]

#全球地理图，对应原网站图一
fig = px.choropleth_mapbox(
    geojson = plot_data, data_frame = plot_data, color = "gas",
    featureidkey="properties.country",
    locations = "country",
    mapbox_style = "carto-positron",zoom = 1,
    color_continuous_scale = 'blues',
    title = "world gas production by countries")
st.plotly_chart(fig)

plot_data2 = data_with_border[data_with_border['country'].isin(select_countrys)]
fig = px.line(plot_data2,x='Year' ,y='gas' , color = "country")