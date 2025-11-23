import argparse

from src.missile_map import (
    load_bases,
    load_ranges,
    create_map,
    add_range_layers,
    add_legend,
    export_map,
)


def filter_bases(bases_df, missile=None, base_name=None):
    """Return only bases matching the missile code or base name."""
    df = bases_df.copy()

    if missile:
        df = df[df["missiles"].str.contains(missile, na=False)]

    if base_name:
        df = df[df["name"].str.contains(base_name, na=False)]

    return df


def list_bases(bases_df):
    """Print a simple list of bases and their missiles."""
    print("=== Bases ===")
    for _, row in bases_df.iterrows():
        missiles = row.get("missiles", "")
        print(f"- {row['name']} | missiles: {missiles}")


def list_missiles(ranges_df):
    """Print a simple list of missile types and their properties."""
    print("=== Missiles ===")
    for _, row in ranges_df.iterrows():
        print(
            f"- {row['missile_code']}: {row['label']} | "
            f"category={row['category']} | range={row['radius_km']} km"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Generate PLARF missile coverage maps from the command line."
    )

    parser.add_argument(
        "--missile",
        type=str,
        help="Filter to only bases with this missile code (e.g., DF-17).",
    )

    parser.add_argument(
        "--base",
        type=str,
        help='Filter to a specific base (e.g., "Brigade 626" or "Meizhou").',
    )

    parser.add_argument(
        "--category",
        type=str,
        help="Filter to missile category (e.g., SRBM, MRBM, IRBM, HGV, ICBM, LACM).",
    )

    parser.add_argument(
        "--theme",
        type=str,
        default="dark",
        choices=["dark", "light"],
        help="Map theme (dark or light).",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output/cli_generated_map.html",
        help="Output HTML file path (relative to project root).",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Ignore filters and include all bases.",
    )

    parser.add_argument(
        "--list-bases",
        action="store_true",
        help="List all bases and exit.",
    )

    parser.add_argument(
        "--list-missiles",
        action="store_true",
        help="List all missile types and exit.",
    )

    args = parser.parse_args()

    # Load data
    bases = load_bases()
    ranges = load_ranges()

    # Handle listing modes first
    if args.list_bases:
        list_bases(bases)
        # If user ONLY wants listing, exit now
        if not (args.missile or args.base or args.category or args.all):
            return

    if args.list_missiles:
        list_missiles(ranges)
        if not (args.missile or args.base or args.category or args.all):
            return

    # Apply category filter to missile ranges (optional)
    if args.category:
        cat = args.category.upper()
        ranges = ranges[ranges["category"].str.upper() == cat]
        if ranges.empty:
            print(f"No missiles found in category '{args.category}'. Exiting.")
            return

    # Apply base filters unless --all is set
    if not args.all:
        bases = filter_bases(bases, missile=args.missile, base_name=args.base)
        if bases.empty:
            print("No bases matched your base/missile filters. Exiting.")
            return

    # Choose tiles for theme
    tiles = "CartoDB dark_matter" if args.theme == "dark" else "CartoDB positron"

    # Create and populate map
    m = create_map(tiles=tiles)
    add_range_layers(m, bases, ranges)
    add_legend(m, ranges)

    # Export
    export_map(m, args.output)

    print(f"Map generated: {args.output}")


if __name__ == "__main__":
    main()