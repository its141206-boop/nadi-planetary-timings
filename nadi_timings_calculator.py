import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# --- Core Data Structures & Settings ---
swe.set_ephe_path(None)

PLANET_MAP = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    "Aries": ["Mars"], "Taurus": ["Venus"], "Gemini": ["Mercury"],
    "Cancer": ["Moon"], "Leo": ["Sun"], "Virgo": ["Mercury"],
    "Libra": ["Venus"], "Scorpio": ["Mars", "Ketu"], "Sagittarius": ["Jupiter"],
    "Capricorn": ["Saturn"], "Aquarius": ["Saturn", "Rahu"], "Pisces": ["Jupiter"]
}

PLANETARY_TIMING_YEARS = {
    "Jupiter": (16, 21), "Sun": (22, 23), "Moon": (24, 24),
    "Venus": (25, 27), "Mars": (28, 32), "Mercury": (33, 35),
    "Saturn": (36, 41), "Rahu": (42, 48), "Ketu": (49, 50)
}

CYCLE_ORDER = ["Jupiter", "Sun", "Moon", "Venus", "Mars", "Mercury", "Saturn", "Rahu", "Ketu"]

# --- Core Computation Engine ---
def execute_calculation(date_val, time_val, place_val, offset_val):
    # Fallback coordinates if geopy hits a rate limit or timeout on public cloud hosts
    resolved_address = "New Delhi (Default Fallback)"
    try:
        geolocator = Nominatim(user_agent="streamlit_nadi_calculator")
        location = geolocator.geocode(place_val, timeout=5)
        if location:
            resolved_address = location.address
    except:
        pass 
    
    local_dt = datetime.combine(date_val, time_val)
    utc_dt = local_dt - timedelta(hours=float(offset_val))
    jd_utc = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
    
    planetary_degrees = {}
    planet_to_sign = {}
    sign_to_planets = {sign: [] for sign in ZODIAC_SIGNS}
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    for name, swe_id in PLANET_MAP.items():
        res, _ = swe.calc_ut(jd_utc, swe_id, swe.FLG_SIDEREAL)
        longi = res[0] % 360
        sign_idx = int(longi // 30)
        sign_name = ZODIAC_SIGNS[sign_idx]
        planetary_degrees[name] = longi % 30
        planet_to_sign[name] = sign_name
        sign_to_planets[sign_name].append(name)
        
    # Calculate Ketu (180 degrees away from Rahu node)
    rahu_res, _ = swe.calc_ut(jd_utc, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    ketu_longi = (rahu_res[0] + 180) % 360
    ketu_sign_name = ZODIAC_SIGNS[int(ketu_longi // 30)]
    planetary_degrees["Ketu"] = ketu_longi % 30
    planet_to_sign["Ketu"] = ketu_sign_name
    sign_to_planets[ketu_sign_name].append("Ketu")
    
    # Build Conjunctions and Lords Maps dynamically
    influencer_sets = {}
    for planet in CYCLE_ORDER:
        current_sign = planet_to_sign[planet]
        conjunctions = sign_to_planets[current_sign]
        lords = SIGN_LORDS[current_sign]
        
        combined = []
        for p in conjunctions + lords:
            if p not in combined:
                combined.append(p)
        influencer_sets[planet] = combined

    return resolved_address, planetary_degrees, planet_to_sign, influencer_sets, local_dt

# --- Streamlit Presentation Layer ---
st.set_page_config(page_title="Nadi Astrology Dashboard", layout="wide")
st.title("🪐 Dynamic Nadi Planetary Timing Dashboard")
st.markdown("Calculates absolute planetary positions, processes active sign conjunctions, maps sign rulers, and predicts active cycle windows.")

# Setup Two Side-by-Side Dashboard Columns
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📥 Birth Metrics")
    ui_date = st.date_input("Birth Date", datetime(2005, 7, 24).date())
    ui_time = st.time_input("Birth Time (Local)", datetime.strptime("12:00", "%H:%M").time())
    ui_place = st.text_input("Birth Place (City, Country)", "New Delhi, India")
    ui_offset = st.number_input("Timezone UTC Offset (Hours)", min_value=-12.0, max_value=14.0, value=5.5, step=0.5)
    
    calculate_clicked = st.button("Calculate Profiles & Timelines", type="primary")

with col2:
    st.header("📊 Computational Timelines")
    
    if calculate_clicked:
        with st.spinner("Accessing Swiss Ephemeris Engine..."):
            address, degrees, sign_map, influencer_sets, local_dt = execute_calculation(
                ui_date, ui_time, ui_place, ui_offset
            )
            
            st.success(f"📍 Map Anchor Confirmed: {address}")
            
            # Section 1: Positions Table Display
            st.subheader("1. Sign Alignments & Dynamic Influencer Maps")
            positions_data = []
            for p in CYCLE_ORDER:
                positions_data.append({
                    "Planet": p,
                    "Zodiac Sign": sign_map[p],
                    "Degree inside Sign": f"{degrees[p]:.4f}°",
                    "Dynamic Set (Conjunctions + Lords)": ", ".join(influencer_sets[p])
                })
            st.table(positions_data)
            
            # Section 2: Interactive Tabs for the 50-year Life Cycles
            st.subheader("2. Life Cycle Predictive Chronology")
            tab1, tab2 = st.tabs(["Life Cycle 1 (Ages 1-50)", "Life Cycle 2 (Ages 51-100)"])
            
            for idx, cycle_offset in enumerate([0, 50]):
                current_tab = tab1 if idx == 0 else tab2
                with current_tab:
                    for primary_planet in CYCLE_ORDER:
                        timing_range = PLANETARY_TIMING_YEARS[primary_planet]
                        p_start = timing_range[0] + cycle_offset
                        p_end = timing_range[1] + cycle_offset
                        
                        expander_title = f"🔸 {primary_planet} Period (Age {p_start}-{p_end}) — Sign: {sign_map[primary_planet]}"
                        with st.expander(expander_title):
                            events_table = []
                            for influencer in influencer_sets[primary_planet]:
                                deg = degrees[influencer]
                                period_length = (timing_range[1] - timing_range[0]) + 1
                                degree_influence_years = (deg / 30.0) * period_length
                                total_years_from_birth = (p_start - 1) + degree_influence_years
                                event_date = local_dt + timedelta(days=total_years_from_birth * 365.25)
                                
                                events_table.append({
                                    "Influencer Trigger": influencer,
                                    "Sign Position": sign_map[influencer],
                                    "Degree Used": f"{deg:.3f}°",
                                    "Calculated Trigger Date": event_date.strftime('%Y-%m-%d')
                                })
                            st.dataframe(events_table, use_container_width=True)
