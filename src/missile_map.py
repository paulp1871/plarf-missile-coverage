import pandas as pd
import folium


def load_bases(path="../data/bases.csv"):
    """load PLARF base coordinates from CSV file"""
    return pd.read_csv(path)


def load_ranges(path="../data/ranges.csv"):
    """load missile range definitions (km, colors, categories)"""
    return pd.read_csv(path)


def create_map(center=[30, 115], zoom=4, tiles="CartoDB dark_matter"):
    """
    create map centered on china
    """
    return folium.Map(location=center, zoom_start=zoom, tiles=tiles)


def add_range_layers(map_obj, bases_df, ranges_df):
    """
    create a separate layer for each missile type
    """
    missile_layers = {}
    for _, row in ranges_df.iterrows():
        code = row["missile_code"]
        feature_group = folium.FeatureGroup(name=f"{code} coverage")
        feature_group.add_to(map_obj)
        missile_layers[code] = feature_group

    ranges_by_code = {}
    for _, row in ranges_df.iterrows():
        ranges_by_code[row["missile_code"]] = row

    for _, base in bases_df.iterrows():
        missiles_raw = str(base.get("missiles", "") or "").strip()
        if not missiles_raw:
            continue

        missile_codes = []
        for code in missiles_raw.split(","):
            clean_code = code.strip()
            if clean_code:
                missile_codes.append(clean_code)

        for code in missile_codes:
            missile_range = ranges_by_code.get(code)
            if missile_range is None:
                continue

            radius_km = missile_range["radius_km"]
            color = missile_range["color"]
            label = missile_range["label"]

            base_location = [base["lat"], base["lon"]]
            popup_text = f'{base["name"]} - {label}'

            folium.Marker(
                location=base_location,
                popup=popup_text,
                tooltip=base["name"],
            ).add_to(missile_layers[code])

            folium.Circle(
                location=base_location,
                radius=radius_km * 1000,
                popup=popup_text,
                color=color,
                weight=1,
                fill=True,
                fill_opacity=0.09,
            ).add_to(missile_layers[code])

    folium.LayerControl().add_to(map_obj)


def add_legend(map_obj, ranges_df):
    legend_rows = []
    for _, row in ranges_df.iterrows():
        color = row["color"] if pd.notna(row["color"]) else "black"
        code = row["missile_code"]
        radius_km = row["radius_km"]
        legend_rows.append(
            f'<span style="color:{color};">&#9679;</span> {code} ({radius_km} km)'
        )

    rows_html = "<br>".join(legend_rows)

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
    """save folium map as HTML file"""
    map_obj.save(output_path)


def build_plarf_map(
    bases_path="../data/bases.csv",
    ranges_path="../data/ranges.csv",
    output_path="../output/plarf_missile_coverage.html",
):
    """
    convenience function: load data, build a styled map,
    add markers, layers, legend, and export
    """
    bases = load_bases(bases_path)
    ranges = load_ranges(ranges_path)

    m = create_map()
    add_range_layers(m, bases, ranges)
    add_legend(m, ranges)
    export_map(m, output_path)

    return m
