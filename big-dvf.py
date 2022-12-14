#!/usr/bin/env python3

import pandas as pd
import plotly.express as px
from geopy.geocoders import BANFrance, Nominatim

# STEP 1: Read DVF data, and filter by department
# df = pd.read_csv("valeursfoncieres-2021.txt", sep="|")
# df["Valeur fonciere"] = df["Valeur fonciere"].str.replace(",", ".").astype(float)
# df_95 = df.query("`Code departement` == 95")
# df_95.to_pickle('dvf-95.pkl')
# df_94 = df.query("`Code departement` == 94")
# df_94.to_pickle('dvf-94.pkl')
# df_93 = df.query("`Code departement` == 93")
# df_93.to_pickle('dvf-93.pkl')
# df_92 = df.query("`Code departement` == 92")
# df_92.to_pickle('dvf-92.pkl')
# df_91 = df.query("`Code departement` == 91")
# df_91.to_pickle('dvf-91.pkl')

# STEP 2: Filter according to more specific criteria (eg. acreage)
df_91 = pd.read_pickle('dvf-91.pkl')
df_94 = pd.read_pickle('dvf-94.pkl')
df = pd.concat([df_91, df_94])
qry = df.query("`Code type local` == 1")
qry = qry.query("`Surface terrain` >= 570 and `Surface terrain` <= 615")
qry = qry.query("`Surface reelle bati` >= 120 and `Surface reelle bati` <= 130")
qry = qry.query("`Valeur fonciere` > 300000 and `Valeur fonciere` < 400000")

print("{} entries found".format(qry.shape[0]))

# STEP 3: Geocoding
def geocode(row):
    #geocoder = BANFrance()
    geocoder = Nominatim(user_agent="big-dvf")
    address = "{} {} {} {}".format(row["No voie"],
                                   row["Type de voie"],
                                   row["Voie"],
                                   row["Commune"])
    location = geocoder.geocode(address)
    if location is None:
        return row
    row['lat'] = location.latitude
    row['lon'] = location.longitude
    return row
qry = qry.apply(geocode, axis=1)

# STEP 4: Build description
def describe(row):
    address = "{} {} {} {}".format(row["No voie"],
                                   row["Type de voie"],
                                   row["Voie"],
                                   row["Commune"])
    text = """Valeur foncière : {}<br>
Adresse : {}<br>
Surface : {}<br>""".format(row["Valeur fonciere"],
        address,
        row["Surface terrain"])
    row["Description"] = text
    return row
qry = qry.apply(describe, axis=1)

# STEP 4: Plot on a map
fig = px.scatter_mapbox(qry, lat="lat", lon="lon", hover_name="Description",#hover_data=["State", "Population"],
                        color_discrete_sequence=["fuchsia"], zoom=3)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()