#!/usr/bin/env python
# coding: utf-8

# # Analysis of NYC voting data for the 2025 Mayoral Democratic Primary 

# ### Data sources
# * [Election Districts](https://www.nyc.gov/content/planning/pages/resources/datasets/election-districts)
# * [Congressional Districts](https://www.nyc.gov/content/planning/pages/resources/datasets/congressional-districts)
# * [Voting Data](https://vote.nyc/page/election-results-summary)

# In[1]:


import geopandas as gpd
import pandas as pd
import folium
import sys
import os
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


# In[2]:


repo_path = os.path.split(os.getcwd())[0]

sys.path.insert(0, repo_path + "/src")
sys.path.insert(0, repo_path + "/data")


# ## Combine Geo files and de-duplicate

# In[3]:


# read in shape files
gdfa = gpd.read_file(repo_path + "/data/nyed_25b/nyed.shp")
gdfc = gpd.read_file(repo_path + "/data/nycg_25b/nycg.shp")


# In[4]:


# join geo files
udf = gdfc.overlay(gdfa, how="union")


# In[5]:


intdf = gpd.sjoin(udf, gdfc, how="left")
intdf.shape


# In[6]:


intdf = intdf[["CongDist_left", "ElectDist", "geometry"]]
intdf.columns = ["cong_dist", "precinct_id", "geometry"]
intdf.columns


# In[7]:


intdf = intdf.dissolve(by=["cong_dist", "precinct_id"], aggfunc='first').reset_index()
intdf["geometry"] = intdf.normalize()
intdf = intdf.drop_duplicates()
dist = intdf[["cong_dist", "precinct_id"]]
dist = dist.groupby("precinct_id")["cong_dist"].agg("first").reset_index()


# In[8]:


dist.shape, intdf.shape


# ## Merge Vote Data with Election Districts & Reshape

# In[9]:


# read in voting data
vdf = pd.read_csv(repo_path + "/data/votes.csv")


# In[10]:


# create standardized precint id, which is a concatenation of Assembly District id and Election District id
# the `ElectDist` field in the geo files is already in the format but needs to be converted to a string

dist["precinct_id"] = dist["precinct_id"].map(lambda x: str(round(x)))

vdf["ad_id"] = vdf["AD"].map(lambda x: x.split("-")[0].replace("AD", ""))
vdf["ed_id"] = vdf["election_district"].map(lambda x: x.replace("ED ", "").zfill(3))
vdf["precinct_id"] = vdf[["ad_id", "ed_id"]].apply(lambda row: ''.join(row.values.astype(str)), axis=1)


# In[11]:


# merge voting data and geo ids without geometry
votes = pd.merge(vdf, dist, how="left", on="precinct_id")


# In[12]:


votes.head()


# ## Add additional columns

# In[13]:


candidates = ["zohran_kwame_mamdani", "scott_m_stringer", "selma_k_bartholomew", "zellnor_myrie",
              "adrienne_e_adams", "andrew_m_cuomo", "jessica_ramos", "whitney_r_tilson",
              "michael_blake", "brad_lander", "paperboy_love_prince", "write_in"]

top_candidates = ["zohran_kwame_mamdani", "brad_lander", "andrew_m_cuomo"]
else_candidates = [c for c in candidates if c not in top_candidates]
progressive_candidates = ["zohran_kwame_mamdani", "brad_lander"]


votes["total"] = votes[candidates].apply(lambda row: sum(row), axis=1)
votes["progressive"] = votes[progressive_candidates].apply(lambda row: sum(row), axis=1)
votes["else"] = votes[else_candidates].apply(lambda row: sum(row), axis=1)


# In[14]:


votes[candidates + ["total", "progressive", "else"]].sum().sort_values(ascending=False)


# ## Recombine Geo data

# In[15]:


gdfa.columns


# In[16]:


votes.columns


# In[17]:


dist.columns


# In[18]:


votes_ge = pd.merge(dist, votes, how="left", on="precinct_id")


# In[19]:


votes_ge.columns


# In[20]:


votes_ge.shape


# In[21]:


votes_ge.head()


# In[22]:


votes_ge[candidates].sum()


# In[23]:


votes_ge = votes_ge[["precinct_id", "cong_dist_x", "total", "progressive", "else"] + candidates]
votes_ge.columns = ["precinct_id", "cong_dist"] + list(votes_ge.columns)[2:]


# In[24]:


for col in "cong_dist", "precinct_id":
    votes_ge[col] = [str(round(int(x))) for x in votes_ge[col]]


# In[25]:


votes_ge.head()


# ## Plot some maps

# In[26]:


cdf = intdf.plot(figsize=(15,15), column="cong_dist", cmap="tab20", alpha=0.5)
intdf.plot(ax=cdf, color="none", edgecolor='black', alpha=0.2, linewidth=0.5)
gdfc.plot(ax=cdf, color="none", edgecolor='black', alpha=0.5)
plt.show()


# In[27]:


for col in "cong_dist", "precinct_id":
    intdf[col] = [str(round(int(x))) for x in intdf[col]]


# In[28]:


for df in intdf, votes_ge:
    df["precinct_cong"] = df.apply(lambda x: "_".join([x.precinct_id, x.cong_dist]), axis=1)


# In[29]:


geo = pd.merge(intdf, votes_ge, how="left", on="precinct_cong")


# In[30]:


geo.head()


# In[31]:


geo.shape


# ## Get Congressional District Info

# In[32]:


import requests
import bs4


# In[33]:


# pull data from the cook political report by scraping ballotpedia
url ="https://ballotpedia.org/The_Cook_Political_Report%27s_Partisan_Voter_Index"
req = requests.get(url)
req.status_code


# In[34]:


soup = bs4.BeautifulSoup(req.text, 'html.parser')


# In[35]:


print('Classes of each table:')
for table in soup.find_all('table'):
    print(table.get('id'))


# In[36]:


table_id = "dt-0242e256"
table = soup.find('table', id=table_id)


# In[37]:


# Collecting Ddata
for row in table.tbody.find_all('tr'):    
    # Find all data for each column
    columns = row.find_all('td')
    # print(columns)


# In[38]:


# Defining of the dataframe
df = pd.DataFrame(columns=['district', 'incumbent', 'pvi'])

# Collecting Ddata
for row in table.tbody.find_all('tr'):    
    # Find all data for each column
    columns = row.find_all('td')
    
    if(columns != []):
        district = columns[0].text.strip()
        incumbent = columns[1].text.strip()
        pvi = columns[2].text.strip()

        new_row = pd.DataFrame({'district': district,  'incumbent': incumbent, 'pvi': pvi}, index=[0])

        df = pd.concat([df, new_row], ignore_index=True)


# In[39]:


df.head()


# In[40]:


df["state"] = df["district"].map(lambda x: x.split("'")[0])
df["cong_dist"] = df["district"].map(lambda x: x.split("'")[1].strip("s "))


# In[41]:


dfny = df[df.state == "New York"]
dfny


# In[42]:


for sfx in "st", "nd", "rd", "th":
    dfny["cong_dist"] = dfny["cong_dist"].map(lambda x: x.replace(sfx, ""))


# In[43]:


geo.columns


# In[44]:


geo = geo[['cong_dist_x', 'precinct_id_x', 'geometry', 'precinct_cong',
            'total', 'progressive', 'else',
            'zohran_kwame_mamdani', 'scott_m_stringer', 'selma_k_bartholomew',
            'zellnor_myrie', 'adrienne_e_adams', 'andrew_m_cuomo', 'jessica_ramos',
            'whitney_r_tilson', 'michael_blake', 'brad_lander',
            'paperboy_love_prince', 'write_in']]


# In[45]:


geo.columns = ['cong_dist', 'precinct_id'] + list(geo.columns)[2:]


# In[46]:


geo['cong_dist'] = geo['cong_dist'].astype(str)
dfny['cong_dist'] = dfny['cong_dist'].astype(str)


# In[47]:


geo = geo.merge(dfny, how="left", on="cong_dist")


# In[48]:


# save combined file
geo.to_csv(repo_path + "/data/votes_by_precinct.csv", index=False)


# In[49]:


geo["pct_mamdani"] = geo.apply(lambda x: x.zohran_kwame_mamdani / x.total if x.total > 0 else 0, axis=1)
geo["pct_cuomo"] = geo.apply(lambda x: x.andrew_m_cuomo / x.total if x.total > 0 else 0, axis=1)
geo["pct_progressive"] = geo.apply(lambda x: (x.brad_lander + x.zohran_kwame_mamdani) / x.total if x.total > 0 else 0, axis=1)


# In[50]:


for col in "pct_mamdani", "pct_progressive", "pct_cuomo":
    geo[col + "_display"] = geo[col].map(lambda x: "{:2.1%}".format(x))


# In[51]:


m = folium.Map(location=(40.705, -73.95), zoom_start=11, tiles="cartodb positron")               

g = folium.Choropleth(
    geo_data=geo,
    data=geo["pct_mamdani"],
    columns=["precinct_id", "cong_dist", "incumbent", "pvi", "pct_mamdani", "total"],
    key_on="feature.id",
    bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
    fill_color="BuPu",
    nan_fill_color="white",
    fill_opacity=0.9,
    line_color="white",
    line_weight=0.5,
    line_opacity=0.8,
    name="2025 Mayoral Democratic Primary",
    legend_name="Percent of Votes"
    
).add_to(m)

c = folium.GeoJson(
    data=gdfc,
    style_function=lambda feature: {
        "fillColor": "none",
        "color": "black",
        "weight": 1,
    }
).add_to(m) 

#Add Customized Tooltips to the map
feature = folium.features.GeoJson(
                data=geo,
                name='tooltip',
                style_function=lambda x: {'color':'none','fillColor':'transparent','weight':0.5},
                tooltip=folium.features.GeoJsonTooltip(
                    fields=["cong_dist", "incumbent", "pvi", "pct_mamdani_display", "total"],
                    aliases=["Cong District:", "House Rep:", "Cook's PVI:", "Mamdani %:", "Total Votes:"],
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                    """,
                    max_width=800,),
                        highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
                    ).add_to(m) 


folium.LayerControl().add_to(m)


m  # show map


# In[6]:


# save notebook as a python file
get_ipython().system('jupyter nbcovert --to script nyc_primary_2025.ipynb')


# In[ ]:




