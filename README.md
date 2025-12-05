# NYC Democratic Primary Data from 2025

Analysis of the democratic primary vote for mayor in NYC, June 2025.

Read my analysis and see visualizations on [my website](https://emilyschuch.com/works/nyc-democratic-mayoral-primary-2025/).

The notebook `nyc_primary_2025.ipynb` uses geopandas to combine precinct level geometry with congressional district geometry and add vote totals for the first round of ranked choice voting in the NYC Democratic Mayoral Primary. I also scraped data from Ballotpedia to add the Partisan Voter Index (PVI) developed by the Cook Political Report for 2026. See the full definition of PVI in the data source linked below.

If you have issues viewing the notebook file, [use this link](https://nbviewer.org/github/emschuch/nyc-primary-2025/blob/main/notebooks/nyc_primary_2025.ipynb) instead. Alternatively, the code is viewable in the python file `nyc_primary_2025.py` without the visualizations and outputs.

## Data Sources:
* Precint Geometry: [NYC Department of City Planning - Election Districts](https://www.nyc.gov/content/planning/pages/resources/datasets/election-districts)
* Congressional Districts: [NYC Department of City Planning - Congressional Districts](https://www.nyc.gov/content/planning/pages/resources/datasets/congressional-districts)
* Voting Data: [NYC Board of Elections](https://github.com/christopherkenny/nyc-election-june-24-2025/blob/main/data/votes.csv)
* Cook Political Report PVI: [Ballotpedia](https://ballotpedia.org/The_Cook_Political_Report%27s_Partisan_Voter_Index#resultsanalysis-2026-1)
