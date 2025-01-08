import tkinter as tk
from tkinter import filedialog, messagebox
import math
import svgpathtools

def svg_to_gcode(input_svg, output_gcode, divisor, feedrate=1000, z_move_height=1, samples_per_curve=20):
    # Open SVG file
    paths, _ = svgpathtools.svg2paths(input_svg)

    # Start G-code file
    with open(output_gcode, 'w') as f:
        # Initialize the G-code
        f.write("; G-code generated from SVG\n")
        f.write("G21 ; Set units to mm\n")
        f.write("G90 ; Absolute positioning\n")

        # Iterate through paths
        for path in paths:
            # For each path, write the initial position
            for segment in path:
                # Break curves into linear approximations
                points = [
                    segment.point(t)
                    for t in [i / samples_per_curve for i in range(samples_per_curve + 1)]
                ]

                # Move to the start point
                start = points[0]
                f.write(f"G0 X{start.real / divisor:.3f} Y{start.imag / divisor:.3f}\n")
                f.write(f"M03 S255\n")  # Turn on the tool

                # Draw each line segment
                for point in points[1:]:
                    f.write(f"G1 X{point.real / divisor:.3f} Y{point.imag / divisor:.3f} F{feedrate}\n")

                f.write(f"M05\n")  # Turn off the tool

        # End G-code
        f.write("G0 X0 Y0 ; Move to origin\n")
        f.write("M30 ; End of program\n")

# GUI Functions
def open_file():
    # Open a file dialog to select an SVG file
    file_path = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
    if file_path:
        file_label.config(text=f"Selected file: {file_path}")

def convert_svg():
    # Get the SVG file path from the label text
    svg_file = file_label.cget("text").replace("Selected file: ", "")
    if not svg_file:
        messagebox.showerror("Error", "Please select an SVG file first.")
        return

    if not svg_file.endswith(".svg"):
        messagebox.showerror("Error", "Selected file is not an SVG file.")
        return

    # Get the divisor from the input field
    try:
        divisor = float(divisor_entry.get())
        if divisor <= 0:
            raise ValueError("Divisor must be greater than 0.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid positive number for the divisor.")
        return

    # Set the output G-code file name
    output_file = filedialog.asksaveasfilename(defaultextension=".gcode", filetypes=[("G-code files", "*.gcode")])
    if output_file:
        try:
            svg_to_gcode(svg_file, output_file, divisor)
            messagebox.showinfo("Success", f"G-code saved to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert SVG to G-code: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("SVG to G-code Converter")

# Create the file input and buttons
file_label = tk.Label(root, text="No file selected", width=50, anchor='w')
file_label.pack(padx=20, pady=5)

open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack(padx=20, pady=5)

divisor_label = tk.Label(root, text="Enter divisor:")
divisor_label.pack(padx=20, pady=5)

divisor_entry = tk.Entry(root)
divisor_entry.insert(0, "10")  # Default value
divisor_entry.pack(padx=20, pady=5)

convert_button = tk.Button(root, text="Convert", command=convert_svg)
convert_button.pack(padx=20, pady=5)

# Run the GUI
root.mainloop()
