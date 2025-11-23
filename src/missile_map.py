import pandas as pd
import folium


def load_bases(path="../data/bases.csv"):
    """Load PLARF base coordinates from CSV."""
    return pd.read_csv(path)


def load_ranges(path="../data/ranges.csv"):
    """Load missile range definitions (km, colors, categories)."""
    return pd.read_csv(path)

def create_map(center=[30, 115], zoom=4, tiles="CartoDB dark_matter"):
    """
    Create a folium map centered on China.

    tiles examples:
      - 'OpenStreetMap'
      - 'CartoDB positron'  (light)
      - 'CartoDB dark_matter' (dark)
    """
    return folium.Map(location=center, zoom_start=zoom, tiles=tiles)


def add_base_markers(map_obj, bases_df):
    """Add markers for each PLARF base."""
    for _, base in bases_df.iterrows():
        folium.Marker(
            location=[base["lat"], base["lon"]],
            popup=base["name"],
            tooltip=base["name"],
        ).add_to(map_obj)

def add_range_layers(map_obj, bases_df, ranges_df):
    """
    Create a SEPARATE layer for each missile type (not just category).

    A layer named "DF-26", "DF-21D", "DF-17", etc.

    Only bases that actually have that missile will appear in that layer.
    """

    # 1. Create a FeatureGroup for EACH missile code
    missile_layers = {}

    for _, r in ranges_df.iterrows():
        code = r["missile_code"]
        missile_layers[code] = folium.FeatureGroup(name=f"{code} coverage")
        missile_layers[code].add_to(map_obj)  # Attach once

    # 2. Build lookup for missile_code → row
    ranges_by_code = {
        row["missile_code"]: row
        for _, row in ranges_df.iterrows()
    }

    # 3. For each base, draw circles ONLY for its missiles
    for _, base in bases_df.iterrows():

        # Parse comma-separated missile list
        missiles_str = str(base.get("missiles", "") or "").strip()
        if not missiles_str:
            continue  # base has no missile data

        missile_codes = [
            code.strip()
            for code in missiles_str.split(",")
            if code.strip()
        ]

        for code in missile_codes:

            # Skip unknown missiles
            if code not in ranges_by_code:
                continue

            r = ranges_by_code[code]

            # Extract missile range and color
            radius_km = r["radius_km"]
            color = r["color"]
            label = r["label"]

            # Add circle ONLY to the layer for that missile
            folium.Circle(
                location=[base["lat"], base["lon"]],
                radius=radius_km * 1000,
                popup=f'{base["name"]} – {label}',
                color=color,
                weight=1,
                fill=True,
                fill_opacity=0.09,
            ).add_to(missile_layers[code])

    # 4. Enable layer toggles
    folium.LayerControl().add_to(map_obj)

def add_legend(map_obj, ranges_df):
    rows = []
    for _, r in ranges_df.iterrows():
        color = r["color"] if pd.notna(r["color"]) else "black"
        rows.append(
            f'<span style="color:{color};">&#9679;</span> {r["missile_code"]} ({r["radius_km"]} km)'
        )
    rows_html = "<br>".join(rows)

    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        z-index:9999;
        font-size:14px;
        background-color: white;
        padding: 10px;
        border: 2px solid grey;
        border-radius: 4px;
        opacity: 0.9;
        ">
        <b>Missile Coverage</b><br>
        {rows_html}
    </div>
    """

    map_obj.get_root().html.add_child(folium.Element(legend_html))

def export_map(map_obj, output_path="../output/map.html"):
    """Save folium map as HTML file."""
    map_obj.save(output_path)


def build_plarf_map(
    bases_path="../data/bases.csv",
    ranges_path="../data/ranges.csv",
    output_path="../output/plarf_styled_dark.html",
):
    """
    Convenience function: load data, build a styled map,
    add markers, layers, legend, and export it.
    """
    bases = load_bases(bases_path)
    ranges = load_ranges(ranges_path)

    m = create_map()
    add_base_markers(m, bases)
    add_range_layers(m, bases, ranges)
    add_legend(m, ranges)
    export_map(m, output_path)

    return m