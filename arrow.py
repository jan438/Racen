import svgwrite
import math

def rotate_point(x, y, angle_deg, cx=0, cy=0):
    """
    Rotate a point (x, y) around a center (cx, cy) by angle_deg degrees.
    """
    angle_rad = math.radians(angle_deg)
    dx, dy = x - cx, y - cy
    qx = cx + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
    qy = cy + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
    return qx, qy

def rotate_path_coords(coords, angle_deg, cx=0, cy=0):
    """
    Rotate a list of (x, y) coordinates.
    """
    return [rotate_point(x, y, angle_deg, cx, cy) for x, y in coords]

# Create SVG drawing
dwg = svgwrite.Drawing("SVG/rotated_arrow.svg", size=("200px", "200px"))

# Original arrow path coordinates (simple triangle arrow)
arrow_coords = [(50, 100), (150, 100), (100, 50)]

# Rotate arrow 180 degrees around center (100, 100)
rotated_coords = rotate_path_coords(arrow_coords, 180, cx=100, cy=100)

# Convert coordinates to SVG path string
def coords_to_path(coords):
    path_str = f"M {coords[0][0]},{coords[0][1]} "
    for x, y in coords[1:]:
        path_str += f"L {x},{y} "
    path_str += "Z"  # Close path
    return path_str

# Add original arrow (red)
dwg.add(dwg.path(d=coords_to_path(arrow_coords),
                 fill="red", stroke="black", stroke_width=2))

# Add rotated arrow (blue)
dwg.add(dwg.path(d=coords_to_path(rotated_coords),
                 fill="blue", stroke="black", stroke_width=2))

# Save SVG
dwg.save()
print("SVG saved as rotated_arrow.svg")

key = input("Wait")
