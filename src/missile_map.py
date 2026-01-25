import pandas as pd
import folium


def load_bases(path="../data/bases.csv"):
    return pd.read_csv(path)


def load_ranges(path="../data/ranges.csv"):
    return pd.read_csv(path)


def create_map(center=[30, 115], zoom=4, tiles="CartoDB dark_matter"):
    return folium.Map(location=center, zoom_start=zoom, tiles=tiles)


def add_range_layers(map_obj, bases_df, ranges_df):
    missile_layers = {}

    for _, r in ranges_df.iterrows():
        code = r["missile_code"]
        fg = folium.FeatureGroup(name=f"{code} coverage", show=False)
        fg.add_to(map_obj)  # Attach once
        missile_layers[code] = fg

    ranges_by_code = {
        row["missile_code"]: row
        for _, row in ranges_df.iterrows()
    }

    for _, base in bases_df.iterrows():
        missiles_str = str(base.get("missiles", "") or "").strip()
        if not missiles_str:
            continue

        missile_codes = []
        for code in missiles_raw.split(","):
            clean_code = code.strip()
            if clean_code:
                missile_codes.append(clean_code)

        for code in missile_codes:
            if code not in ranges_by_code:
                continue

            r = ranges_by_code[code]

            radius_km = r["radius_km"]
            color = r["color"]
            label = r["label"]

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
    map_obj.save(output_path)


def build_plarf_map(
    bases_path="../data/bases.csv",
    ranges_path="../data/ranges.csv",
    output_path="../output/plarf_missile_coverage.html",
):
    bases = load_bases(bases_path)
    ranges = load_ranges(ranges_path)

    m = create_map()
    add_range_layers(m, bases, ranges)
    add_legend(m, ranges)
    export_map(m, output_path)

    return m

build_plarf_map(bases_path="../data/bases.csv", ranges_path="../data/ranges.csv", output_path="../backend/output/map.html")