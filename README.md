# Maharashtra CAP Dashboard

This is a fully functional Streamlit app for Maharashtra Climate Action Plan (CAP) Dashboard.

## Features
- Home page: City-wise emissions map, top 10 emitters
- City Information: Full city data table, CAP PDF download (requires name & email)
- Admin (EinTrust-only): CAP Update, Data Collection, GHG Inventory, Recommended Actions
- Last Updated on all pages
- Minimalist dark theme inspired by ChatGPT
- CAP PDF generation using fpdf2
- SharePoint integration for saving CAP PDFs
- Dummy coordinates included for all 43 cities

## Setup Instructions (Streamlit Cloud)
1. Fork or upload the folder to your Streamlit Cloud repository.
2. Add **secrets** for SharePoint credentials:
   - CLIENT_ID
   - CLIENT_SECRET
   - SHAREPOINT_SITE
   - SHAREPOINT_DOC
3. Ensure `requirements.txt` is present.
4. Deploy the app. Streamlit Cloud will install dependencies automatically.
5. Launch the app at `[Your App URL]`.

## Notes
- Admin password is set to `eintrust123` (change in `mahacap.py` for production)
- All data and PDFs are auto-uploaded to SharePoint in folders by city
- CAP PDF download requires entering Name & Official Email
