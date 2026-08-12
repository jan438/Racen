import svgwrite
import os

def coords_to_svg_path(coords):
    """
    Convert a list of (x, y) tuples into an SVG path string.
    Uses 'M' for move-to and 'L' for line-to commands.
    """
    if not coords or not all(isinstance(pt, (tuple, list)) and len(pt) == 2 for pt in coords):
        raise ValueError("coords must be a list of (x, y) tuples")

    # Start with 'M' for the first point, then 'L' for the rest
    path_cmds = [f"M {coords[0][0]} {coords[0][1]}"]
    path_cmds += [f"L {x} {y}" for x, y in coords[1:]]
    return " ".join(path_cmds)

def save_svg(coords, filename="output.svg", stroke="black", stroke_width=2, fill="none"):
    """
    Save coordinates as an SVG file with a <path> element.
    """
    path_data = coords_to_svg_path(coords)

    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
     width="500" height="500" viewBox="0 0 500 500">
  <path d="{path_data}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />
</svg>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"SVG saved to {os.path.abspath(filename)}")

# Example usage
if __name__ == "__main__":
    # Example coordinates
    points = [(50, 50), (150, 80), (200, 200), (100, 250), (50, 200)]
    save_svg(points, filename="SVG/path_example.svg")
    
key = input("Wait")
