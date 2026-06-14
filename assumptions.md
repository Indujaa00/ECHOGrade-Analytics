# Model Assumptions — ECHOGrade Analytics

This document describes every assumption embedded in the ECHOGrade model, the rationale for each, and an honest assessment of its limitations.

---

## 1. Participation Assumptions

### 1.1 Campus-Level Participation Rate
**Default:** 50%  
**Range:** 0–100% (user-adjustable)

**Rationale:** In voluntary campus waste drives at Indian universities, participation rates between 40–60% have been observed in student surveys and sustainability initiative reports. 50% is a neutral planning baseline that does not assume success or failure.

**Limitation:** This figure is not derived from IIT Madras-specific data. No historical paper recovery drive has been run at IIT Madras under this format, so there is no empirical baseline to calibrate against. The sensitivity analysis in the Financial Analysis page deliberately shows how outcomes change across the 10–100% range to compensate for this uncertainty.

### 1.2 Hostel-Level Participation Variation
**Method:** Each hostel's participation rate is drawn from a uniform distribution over [campus_rate − 0.10, campus_rate + 0.10], clipped to [0, 1].  
**Random seed:** 42 (fixed)

**Rationale:** It is unrealistic to assume all hostels participate at exactly the campus average. Variation arises from warden engagement, hostel culture, and student awareness. A ±10 percentage point spread is a conservative estimate of this variation — sufficient to create realistic hostel-level differences without overstating dispersion.

**Limitation:** Uniform distribution is the simplest model. A Beta distribution or truncated Normal would more accurately represent real participation rates, which are bounded and typically cluster around a mode rather than being flat across a range. The fixed seed means the variation pattern is consistent but not a sample of a true distribution.

---

## 2. Paper Generation Assumptions

### 2.1 Average Paper per Participating Student
**Default:** 0.75 kg  
**Range:** 0.25–1.5 kg (user-adjustable)

**Rationale:** 0.75 kg represents roughly 150–200 A4 sheets of paper, or 3–4 printed assignments plus miscellaneous notes. This is a conservative estimate for a single semester's disposable paper from a science or engineering student. Students who print extensively (project reports, lab manuals) may generate 1–1.5 kg. Students in digital-first courses may generate under 0.5 kg.

**Limitation:** No actual measurement exists for IIT Madras. The range 0.25–1.5 kg is informed by analogous campus waste audits, but these are from different institutional contexts. Paper generation likely varies significantly by department and year of study. The model does not capture this variation — it applies a single campus-wide average.

### 2.2 Paper Type Composition
**Assumption:** All paper collected is of uniform recyclable quality (A4 printing paper, notebooks, paperback covers).

**Limitation:** In practice, paper waste includes glossy paper (magazines, lab covers), laminated material, spiral-bound notebooks with metal components, and wet/contaminated paper. Contamination typically reduces effective recyclable weight by 5–15%. The model does not apply a contamination discount.

---

## 3. Labour Assumptions

### 3.1 Worker Productivity
**Default:** 500 kg per worker per day  
**Editable in sidebar**

**Rationale:** This covers manual aggregation, bagging, loading, and weighing. 500 kg per day per worker is a standard estimate for semi-mechanised paper handling — realistic for workers moving paper from hostel dump rooms to a collection point using trolleys or manual carts.

**Limitation:** This figure varies with: distance between dump room and collection point, availability of trolleys, and paper packaging (loose vs. bagged). Hostels with long distances between dump rooms and vehicle access points would see lower effective productivity. The model does not vary productivity by hostel.

### 3.2 Worker Cost per Day
**Default:** ₹1,000 per worker per day  
**Editable**

**Rationale:** Approximately ₹1,000/day is consistent with unskilled/semi-skilled daily labour rates in Chennai as of 2023–2024, accounting for potential overtime. Contractor-sourced labour may include a 15–20% agency markup.

**Limitation:** Does not account for statutory benefits (PF, ESI) if workers are on formal payroll. Also does not include supervisory costs.

### 3.3 Collection Duration
**Default:** 3 days  
**Editable**

**Rationale:** Based on typical IIT Madras end-of-semester vacation schedules, the window between the last examination and hostel closure spans approximately 3–5 days. 3 days is the lower bound of this window.

**Limitation:** The model assumes all workers operate for all collection days at full productivity. In practice, the work may be front-loaded (days 1–2 heavy, day 3 light), and weather or hostel access issues could reduce effective working days.

---

## 4. Truck Assumptions

### 4.1 Truck Capacity
**Default:** 3,000 kg  
**Editable**

**Rationale:** A standard mini-truck or 3-tonne LCV (Light Commercial Vehicle) available for hire in Chennai. Common vendors in the IIT Madras vicinity operate vehicles in the 2,000–4,000 kg range.

**Limitation:** The model assumes homogeneous truck fleet. In reality, a mix of vehicle sizes might be optimal. Paper is also volumetrically bulky — a 3,000 kg capacity truck may reach its volume limit before its weight limit for loosely packed paper. If paper density averages ~150 kg/m³ (loose), a 3,000 kg load requires ~20 m³ of cargo space, which exceeds a standard LCV. Compaction or baling would address this but is not modelled.

### 4.2 Truck Cost per Trip
**Default:** ₹15,000 per trip  
**Editable**

**Rationale:** Includes driver, fuel, and vehicle hire for a single round trip (campus to vendor and back). Consistent with Chennai-area transport rates for LCVs as of 2024.

**Limitation:** Cost varies with distance to vendor and fuel prices. The model uses a fixed trip cost rather than a distance-based formula for truck hire, which is a simplification. The vendor transport cost is separately modelled using a per-km rate.

### 4.3 Zone Routing
**Method:** Hostels are grouped into three fixed zones. Truck trips are calculated per zone using ceiling division. Route sequence within a zone is ordered by paper volume (highest first).

**Limitation:** This is a simplified logistics model. It does not account for actual driving distances between hostels within a zone, time constraints, or multi-trip scheduling within a zone. A single truck may need multiple passes within a zone if the load per route exceeds capacity.

---

## 5. Vendor Assumptions

### 5.1 Transport Rate
**Default:** ₹50 per km (one way)  
**Editable**

**Rationale:** ₹50/km is a reasonable estimate for one-way transport cost on top of the base truck hire, covering the additional distance to vendor from campus. This is distinct from the intra-campus collection truck cost.

**Limitation:** The model applies this rate to a one-way distance figure for each vendor. Return trip costs are not separately modelled. In practice, vendors often arrange their own collection, which would eliminate this cost entirely — an important sensitivity the platform does not capture.

### 5.2 Vendor Price (₹/kg)
**Dataset:** Modelled estimates. Not contractually verified.

**Rationale:** Prices in the dataset (₹10.50–₹13.00/kg) are consistent with prevailing market rates for office-grade waste paper in Chennai as of 2023–2024. TNPL (Tamil Nadu Newsprint and Papers Limited) and ITC GreenCycle are established buyers with known price points.

**Limitation:** Vendor prices fluctuate with the commodity paper market. Actual prices should be confirmed by direct vendor engagement before committing to a campaign. Bulk rate adjustments (for large volumes) are not modelled.

### 5.3 Vendor Capacity
The vendor dataset includes a `Capacity_kg_per_day` field. **This field is not currently used in campaign feasibility calculations.** It is included for reference and future model extension. At the volumes generated in this model (2,000–6,000 kg), capacity constraints are unlikely to bind for established industrial buyers.

---

## 6. Environmental Assumptions

### 6.1 Trees Saved per kg Paper Recycled
**Default:** 0.017 trees/kg

**Rationale:** Derived from the commonly cited figure that one tonne of recycled paper saves approximately 17 trees. This is an average across paper grades and tree species.

**Limitation:** The "trees per tonne" figure varies significantly by paper type and production method. Recycled office paper displaces virgin pulp differently than newsprint or cardboard. The figure used here is a round-number average and should not be cited in formal environmental reporting without specifying the methodology.

### 6.2 CO₂ Avoided per kg Paper Recycled
**Default:** 1.084 kg CO₂ per kg paper

**Rationale:** Based on lifecycle assessment literature comparing virgin paper production to recycled paper production, including avoided methane emissions from landfill decomposition of paper.

**Limitation:** CO₂ avoidance estimates range widely in the literature (0.9–1.8 kg CO₂/kg paper) depending on the system boundary and whether transport emissions and energy mix for the recycling facility are included. The figure used here is a mid-range estimate and does not account for local grid emissions at the vendor's facility.

### 6.3 Landfill Diversion
**Default:** 1.0 kg diverted per kg paper recovered (one-to-one)

**Rationale:** Simple assumption that all paper recovered would otherwise have gone to landfill. This is a reasonable upper bound for a campus context where paper is otherwise mixed with general waste.

**Limitation:** Some fraction of discarded campus paper is likely already recovered by informal waste pickers who regularly sort hostel bins. The model does not account for this substitution effect, which means landfill diversion figures may overstate the additionality of a formal recovery campaign.

---

## Summary of Key Uncertainties

| Assumption | Confidence | Impact on Output |
|------------|-----------|-----------------|
| Campus participation rate | Low (no prior data) | High |
| Avg paper per student (0.75 kg) | Low–Medium | High |
| Worker productivity (500 kg/day) | Medium | Medium |
| Truck capacity (3,000 kg) | Medium–High | Medium |
| Vendor price (₹10.5–13/kg) | Medium | High |
| CO₂ factor (1.084 kg/kg) | Medium | Low (for financial decisions) |

The participation rate and per-student paper generation assumptions together drive ~80% of the uncertainty in the output. The sensitivity analysis on the Financial Analysis page should be used to understand how outcomes respond to these inputs before making operational commitments.