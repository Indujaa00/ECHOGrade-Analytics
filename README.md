# ECHOGrade Analytics

**A techno-economic decision-support platform for semester-end paper recovery campaigns in educational campuses.**

Pilot campus: **IIT Madras** | Built with Python + Streamlit | Two-phase operational model

---

## Project Overview

ECHOGrade Analytics is a logistics and financial planning tool that models the collection, transport, and sale of paper waste generated during hostel move-out periods at the end of an academic semester.

The system is not a recycling awareness app. It is an operations and economics tool designed to answer a specific question:

> **Is running a structured paper recovery drive at IIT Madras operationally feasible and financially viable — and under what conditions does it cross into profitability?**

The platform supports two operational phases: pre-campaign planning using forecast models, and post-campaign analysis using actual collected weights.

---

## Problem Statement

During semester-end vacations at IIT Madras, students vacate hostels within a compressed 2–5 day window. A significant volume of paper — notes, printouts, textbooks, and packaging — is discarded during this period, much of it going to unsegregated waste streams.

The logistical challenge is coordination: 21 hostels, varying populations, a narrow collection window, and multiple competing recycling vendors at different distances with different price points. Without a structured model, organising such a campaign requires guesswork.

This platform replaces guesswork with parameterised scenario analysis.

---

## Key Insight

Paper recovery at this scale operates on a thin margin. The model shows that:

- At 30% campus participation, the campaign runs at a **small loss** (approximately ₹1,800 deficit).
- At 50% participation, the campaign is near break-even (approximately ₹614 deficit).
- At 70% participation, the campaign generates **₹15,500+ in net profit** and diverts over 5,200 kg from landfill.

Vendor selection and transport distance have a meaningful impact on net revenue. The optimal vendor in the model (ITC GreenCycle, 18 km, ₹13/kg) outperforms local recyclers despite a slightly longer distance, due to significantly better pricing.

---

## Methodology

### Participation Model
Each hostel's participation rate is drawn from a uniform distribution centred on the campus-level rate with a ±10 percentage point spread. The seed is fixed (seed = 42) for reproducibility. This reflects realistic variation driven by hostel culture, warden engagement, and peer effects.

### Paper Generation Model
```
Participants = Population × Hostel Participation Rate
Paper (kg)   = Participants × Average Paper per Participant
```
Default average paper per participant: **0.75 kg** (editable in sidebar).

### Logistics Model
Hostels are grouped into three geographic zones based on IIT Madras campus layout:
- **Gajendra Circle Zone**: Ganga, Godavari, Jamuna, Brahmaputra, Saraswathi, Sindhu
- **Hostel Zone**: Alakananda, Cauvery, Krishna, Mahanadhi, Narmada, Pampa, Mandakini, Tapti
- **Taramani Zone**: Bhadra, Sabarmati, Sarayu, Sharavathi, Swarnamukhi, Tunga, Tamiraparani

Truck trips per zone are calculated using ceiling division. No routing API is used; the model is intentionally simplified to reflect the planning-level precision appropriate for a feasibility study.

### Financial Model
```
Revenue      = Total Paper × Vendor Price − Transport Cost
Total Cost   = Truck Costs + Labour Costs + Miscellaneous Cost
Net Profit   = Revenue − Total Cost
```

### Environmental Model
```
Trees Saved      = Paper (kg) × 0.017
CO₂ Avoided      = Paper (kg) × 1.084 kg
Landfill Diverted = Paper (kg) × 1.0 kg
```
Conversion factors are editable and sourced from standard waste management literature.

---

## Dashboard Features

| Page | Description |
|------|-------------|
| Executive Overview | KPI summary, zone pie chart, P&L waterfall, model explanation |
| Hostel Analytics | Editable hostel population table, participation simulation, paper generation by hostel |
| Logistics & Routing | Zone-wise truck routes, trip counts, utilisation gauge, worker requirements |
| Vendor Analysis | Editable vendor table, net revenue ranking, optimal vendor selection |
| Financial Analysis | Full P&L, cost breakdown, sensitivity analysis (profit vs participation rate) |
| Environmental Impact | Trees, CO₂, and landfill metrics; hostel-level environmental contribution |
| Execution Mode | Enter actual collected weights; recalculates all outputs using real data |
| Forecast vs Actual | Hostel-level comparison, MAE, MAPE, error visualisation |

---

## Repository Structure

```
echograde-analytics/
│
├── app.py                          # Main Streamlit application (single file)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── assumptions.md                  # Model assumptions and limitations
├── results.md                      # Scenario analysis outputs
│
├── data/
│   ├── hostels.csv                 # IIT Madras hostel dataset (modelled)
│   └── vendors.csv                 # Recycling vendor dataset
│
└── docs/
    └── ECHOGrade_Case_Study.md     # Consulting-style case study document
```

---

## Technology Stack

| Component | Library / Tool |
|-----------|---------------|
| Web framework | Streamlit 1.35+ |
| Data processing | Pandas, NumPy |
| Visualisation | Plotly Express, Plotly Graph Objects |
| Language | Python 3.9+ |
| Styling | Custom CSS (dark-teal consulting theme) |

No database, no API keys, no external data feeds required. The application runs entirely on local computation.

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/echograde-analytics.git
cd echograde-analytics

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

All parameters are adjustable from the sidebar in real time. No configuration file is required.

---

## Example Use Case

**Scenario: IIT Madras Sustainability Cell is planning the May 2025 drive.**

1. Open the app. Set campus participation rate to **50%** in the sidebar.
2. Navigate to **Hostel Analytics** to review per-hostel paper estimates.
3. Go to **Logistics & Routing** to confirm truck trip requirements (2 trips at 63% utilisation).
4. Check **Vendor Analysis** — ITC GreenCycle (18 km, ₹13/kg) is selected as optimal.
5. Review **Financial Analysis** — the campaign is near break-even at 50%, profitable above ~65%.
6. After the drive, switch to **Execution Mode**. Enter actual weights per hostel.
7. Navigate to **Forecast vs Actual** to assess model accuracy and calibrate for future campaigns.

---

## Results & Insights

Detailed scenario outputs are in [`results.md`](results.md). Summary:

| Scenario | Paper Recovered | Net Profit | Trees Saved | CO₂ Avoided |
|----------|----------------|-----------|-------------|-------------|
| 30% participation | 2,315 kg | −₹1,802 | 39 | 2,510 kg |
| 50% participation | 3,791 kg | −₹614  | 64 | 4,110 kg |
| 70% participation | 5,264 kg | +₹15,526 | 89 | 5,706 kg |

The campaign becomes financially self-sustaining at approximately 52–55% participation under default assumptions. Environmental benefits are positive at all participation levels.

---

## Future Improvements

- **Live weight input via QR code or Google Forms** — allow hostel coordinators to submit data from their phones during the drive, feeding directly into Execution Mode.
- **Multi-semester historical tracking** — persist results across campaigns to track forecasting accuracy improvement over time.
- **Route optimisation** — replace the simplified zone model with actual driving distance calculations using OpenStreetMap data.
- **Student engagement module** — estimate the effect of different awareness interventions (WhatsApp messages, warden announcements) on participation rate, modelled as a Bernoulli uplift.
- **Expand to other campuses** — the model is parameterised; adapting it to NIT Trichy, BITS Pilani, or any large residential campus requires only updating the hostel dataset and zone map.

---

## License

MIT License. See `LICENSE` for details.

---

## Author

Built as a portfolio project demonstrating product analytics, supply chain modelling, and sustainability operations skills.