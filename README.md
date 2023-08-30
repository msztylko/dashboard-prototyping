# dashboard-prototyping
Notes from working on various dashboards.

## Design workflow

1. Rapid prototyping V1
   - **High-level goal:** get working demo ASAP and better understand problem
   - Technical aspects:
     - jupyter + pandas for data exploration
     - plotly to prototype the dashboard
     - streamlit for demo and to get user feedback
2. Backend V2
   - **High-level goal:** model and validate data. Check general architecture
   - Technical aspects:
     - flask app for data processing with endpoint to frontend
     - switch streamlit to make reqeusts to flask backend instead of previous upstream. Keep working demo along the way
     - estimate storage and add simple caching with Redis or sqlite
3. Frontend V3
   - **High-level goal**: focus on better UI
   - Technical aspects:
     - switch to Dash for more interactive usage 

Next versions are created to solve problems from previous versions on the way to deliver final product. 

## [Static dashboard](https://github.com/msztylko/dashboard-prototyping/tree/master/static_dashboard)

<p float="left">
  <img src="https://github.com/msztylko/dashboard-prototyping/blob/master/images/dashboard.gif" width="300" height="200" />
  <img src="https://github.com/msztylko/dashboard-prototyping/blob/master/images/backend.gif" width="300" height="200" /> 
  <img src="https://github.com/msztylko/dashboard-prototyping/blob/master/images/dash_frontend.gif" width="300" height="200" />
</p>
