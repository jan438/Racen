import svgwrite

def create_svg_with_path(output_file):
    try:
        # Create an SVG drawing (size in pixels or any SVG unit)
        dwg = svgwrite.Drawing(output_file, size=("200px", "200px"))

        # Define an SVG path string (M = move, L = line, Z = close path)
        path_data = "M 10 80 C 40 10, 65 10, 95 80 S 150 150, 180 80"

        # Add the path to the drawing
        dwg.add(dwg.path(
            d=path_data,
            stroke="blue",
            fill="none",
            stroke_width=2
        ))

        # Save the SVG file
        dwg.save()
        print(f"SVG file created: {output_file}")

    except Exception as e:
        print(f"Error creating SVG: {e}")

if __name__ == "__main__":
    create_svg_with_path("SVG/graph.svg")
    
    
coords = [(10, 10), (50, 60), (90, 20)]
path_data = "M {} {} ".format(*coords[0]) + " ".join(f"L {x} {y}" for x, y in coords[1:])

key = input("Wait")
