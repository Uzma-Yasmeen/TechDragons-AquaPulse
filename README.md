# TechDragons-AquaPulse

Welcome to the **AquaPulse Intelligence System**, built by team TechDragons for the final hackathon submission.

AquaPulse provides an end-to-end analytical framework to verify, monitor, and enforce urban Rainwater Harvesting mandates, tackling severe water scarcity in major Metropolitan areas like Chennai and Bengaluru.

## 📂 Final Project Structure
The repository has been fully organized and mapped to match our system architecture:
```text
TechDragons-AquaPulse/
├── architecture/      # System design & logic diagrams
├── documentation/     # Technical docs & user manuals 
├── slides/            # Presentation & pitch deck
├── websites/          # Core Streamlit application & logic
│   ├── app.py         # Main application entry point
│   ├── requirements.txt
│   ├── utils/         # Data persistence & visual logic (data_manager.py)
│   └── data/          # Simulated JSON database (buildings.json)
└── README.md          # Project mapping
```

## 🚀 How to Run the App
Since the application has been restructured for deployment, please execute the web app from the new `websites` directory.

1. Install dependencies:
   ```bash
   cd websites
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app.py
   ```

*Note: The system will automatically generate the `data/buildings.json` mock database upon its first successful boot.*
