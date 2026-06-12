# 1. Install dependencies completely silently
!pip install -q pyswisseph geopy

import swisseph as swe
from datetime import datetime, timedelta, time
from geopy.geocoders import Nominatim
import ipywidgets as widgets
from IPython.display import display, HTML

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

# --- Core Computation Logic ---
def execute_calculation(date_val, time_val, place_val, offset_val):
    try:
        # Fallback coordinate handler if geopy geo-lookup times out
        lat, lon, resolved_address = 28.6139, 77.2090, "New Delhi (Fallback Default)"
        try:
            geolocator = Nominatim(user_agent="colab_nadi_notebook")
            location = geolocator.geocode(place_val, timeout=4)
            if location:
                resolved_address = location.address
        except:
            pass # Use local fallback gracefully if structural firewall blocks the network

        # Chronology Parsers
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

        # Add Ketu
        rahu_res, _ = swe.calc_ut(jd_utc, swe.MEAN_NODE, swe.FLG_SIDEREAL)
        ketu_longi = (rahu_res[0] + 180) % 360
        ketu_sign_name = ZODIAC_SIGNS[int(ketu_longi // 30)]
        planetary_degrees["Ketu"] = ketu_longi % 30
        planet_to_sign["Ketu"] = ketu_sign_name
        sign_to_planets[ketu_sign_name].append("Ketu")

        # Build Influencer Sets (Conjunctions + Sign Lords)
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

        # Generate HTML Dashboard Output Structure
        html_output = f"""
        <div style="font-family: sans-serif; padding: 15px; border: 1px solid #ddd; border-radius:8px; background:#fafafa; margin-top:15px;">
            <div style="background: #2980b9; color: white; padding: 10px; font-weight: bold; border-radius: 4px; margin-bottom:15px;">
                📍 Map Location: {resolved_address}
            </div>

            <h3 style="color:#2c3e50; margin-bottom:5px;">1. Sign Alignments & Dynamic Influencer Maps</h3>
            <table style="width:100%; border-collapse: collapse; margin-bottom: 25px; background:white; font-size:14px;">
                <thead>
                    <tr style="background:#f2f2f2; border-bottom:2px solid #ddd; text-align:left;">
                        <th style="padding:8px;">Planet</th>
                        <th style="padding:8px;">Zodiac Sign</th>
                        <th style="padding:8px;">Degree inside Sign</th>
                        <th style="padding:8px;">Dynamic Set (Conjunctions + Lords)</th>
                    </tr>
                </thead>
                <tbody>
        """
        for p in CYCLE_ORDER:
            html_output += f"""
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding:8px; font-weight:bold;">{p}</td>
                    <td style="padding:8px;">{planet_to_sign[p]}</td>
                    <td style="padding:8px; font-family:monospace;">{planetary_degrees[p]:.4f}°</td>
                    <td style="padding:8px; color:#27ae60; font-weight:600;">{", ".join(influencer_sets[p])}</td>
                </tr>
            """
        html_output += "</tbody></table>"

        # Life Cycles Calculations
        for cycle_num, cycle_offset in [(1, 0), (2, 50)]:
            html_output += f"""
            <div style="background:#2c3e50; color:white; padding:8px; font-weight:bold; margin-top:20px; border-radius:4px;">
                ⏳ LIFE CYCLE {cycle_num} (Ages {1 + cycle_offset} - {50 + cycle_offset})
            </div>
            """
            for primary_planet in CYCLE_ORDER:
                timing_range = PLANETARY_TIMING_YEARS[primary_planet]
                p_start = timing_range[0] + cycle_offset
                p_end = timing_range[1] + cycle_offset

                html_output += f"""
                <div style="margin: 10px 0; border: 1px solid #e0e0e0; border-radius: 4px; background: white; padding: 10px;">
                    <strong style="color:#d35400;">🔸 {primary_planet} Period</strong> (Age {p_start}-{p_end}) — <span style="color:#7f8c8d; font-size:12px;">Sign: {planet_to_sign[primary_planet]}</span>
                    <table style="width:100%; border-collapse:collapse; font-size:13px; margin-top:5px; text-align:left;">
                        <tr style="color:#7f8c8d; border-bottom:1px solid #eee;">
                            <th style="padding:4px;">Influencer Trigger</th>
                            <th style="padding:4px;">Sign Position</th>
                            <th style="padding:4px;">Degree Used</th>
                            <th style="padding:4px; color:#c0392b;">Event Calculation Window</th>
                        </tr>
                """
                for influencer in influencer_sets[primary_planet]:
                    deg = planetary_degrees[influencer]
                    period_length = (timing_range[1] - timing_range[0]) + 1
                    degree_influence_years = (deg / 30.0) * period_length
                    total_years_from_birth = (p_start - 1) + degree_influence_years
                    event_date = local_dt + timedelta(days=total_years_from_birth * 365.25)

                    html_output += f"""
                        <tr style="border-bottom:1px solid #f9f9f9;">
                            <td style="padding:4px; font-weight:600;">{influencer}</td>
                            <td style="padding:4px;">{planet_to_sign[influencer]}</td>
                            <td style="padding:4px; font-family:monospace;">{deg:.3f}°</td>
                            <td style="padding:4px; font-weight:bold; color:#d35400;">{event_date.strftime('%Y-%m-%d')}</td>
                        </tr>
                    """
                html_output += "</table></div>"

        html_output += "</div>"
        return html_output
    except Exception as e:
        return f"<div style='color:red; font-weight:bold;'>Error executing: {str(e)}</div>"

# --- Create Native Widget Layout Elements ---
ui_date = widgets.DatePicker(description='Birth Date:', value=datetime(2026, 6, 12).date())
ui_hour = widgets.IntText(description='Hour (0-23):', value=19, min=0, max=23)
ui_minute = widgets.IntText(description='Minute (0-59):', value=48, min=0, max=59)
ui_place = widgets.Text(description='Birth Place:', value='noida, India')
ui_offset = widgets.FloatText(description='UTC Offset:', value=5.5)
ui_button = widgets.Button(description='Calculate Map & Cycles', button_style='primary')
ui_output = widgets.Output()

def on_click_action(b):
    with ui_output:
        ui_output.clear_output()
        print("⚡ Processing Swiss Ephemeris data...")
        # Construct time_val from ui_hour and ui_minute
        time_val = time(hour=ui_hour.value, minute=ui_minute.value)
        result_html = execute_calculation(ui_date.value, time_val, ui_place.value, ui_offset.value)
        ui_output.clear_output()
        display(HTML(result_html))

ui_button.on_click(on_click_action)

# --- Display Interactive UI Inside Notebook Cell Output ---
display(widgets.VBox([
    widgets.HTML("<h2>🪐 Interactive Nadi Astrology Profile Engine</h2>"),
    widgets.HBox([ui_date, ui_hour, ui_minute]),
    widgets.HBox([ui_place, ui_offset]),
    widgets.Label(""),
    ui_button,
    ui_output
]))