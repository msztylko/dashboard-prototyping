# dashboard-prototyping
Notes from working on various dashboards.

## Design workflow

1. Rapid prototyping
   - **High-level goal:** get working demo ASAP and better understand problem
   - Technical aspects:
     - jupyter + pandas for data exploration
     - plotly to prototype the dashboard
     - streamlit for demo and to get user feedback
2. Backend
   - **High-level goal:** model and validate data. Check general architecture
   - Technical aspects:
     - flask app for data processing with endpoint to frontend
     - switch streamlit to make reqeusts to flask backend instead of previous upstream. Keep working demo along the way
     - estimate storage and add simple caching with Redis or sqlite
4. Frontend
   - **High-level goal**: focus on better UI
   - Technical aspects:
     - switch to Dash for more interactive usage 
