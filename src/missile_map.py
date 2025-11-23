import pandas as pd
import folium


def load_bases(path="../data/bases.csv"):
    """Load PLARF base coordinates from CSV."""
    return pd.read_csv(path)


def load_ranges(path="../data/ranges.csv"):
    """Load missile range definitions (km, colors, categories)."""
    return pd.read_csv(path)


def create_map(center=[30, 115], zoom=4):
    """Create a folium map centered on China."""
    return folium.Map(location=center, zoom_start=zoom)


def add_base_markers(map_obj, bases_df):
    """Add markers for each PLARF base."""
    for _, base in bases_df.iterrows():
        folium.Marker(
            location=[base["lat"], base["lon"]],
            popup=base["name"],
            tooltip=base["name"],
        ).add_to(map_obj)


def add_range_layers(map_obj, bases_df, ranges_df):
    """Create separate layers for each missile category."""
    layers = {}

    # Create a FeatureGroup for each category
    for category in ranges_df["category"].unique():
        layers[category] = folium.FeatureGroup(name=f"{category} coverage")

    # Add circles
    for _, base in bases_df.iterrows():
        for _, r in ranges_df.iterrows():
            circle = folium.Circle(
                location=[base["lat"], base["lon"]],
                radius=r["radius_km"] * 1000,
                popup=f'{base["name"]} – {r["label"]}',
                color=r["color"],
                fill=True,
                fill_opacity=0.08,
            )
            layers[r["category"]].add_to(map_obj)
            circle.add_to(layers[r["category"]])

    # Attach layers to the map
    for layer in layers.values():
        layer.add_to(map_obj)

    # Add a layer toggle UI
    folium.LayerControl().add_to(map_obj)


def export_map(map_obj, output_path="../output/map.html"):
    """Save folium map as HTML file."""
    map_obj.save(output_path)