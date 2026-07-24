#!/usr/bin/env python3
"""
Blender script to batch convert Collada (.dae) files to glTF 2.0 (.glb)
Usage: blender -b -P convert_to_gltf.py
"""

import os
import bpy
import sys

# Input and output directories
input_dir = "models/riscv"
output_dir = "models/riscv"

# Get command line arguments (files to convert)
args = sys.argv
try:
    # Find the -- marker which separates blender args from script args
    args_index = args.index("--") + 1
    dae_files = args[args_index:]
except (ValueError, IndexError):
    # If no files specified, convert all .dae in input_dir
    dae_files = [f for f in os.listdir(input_dir) if f.endswith('.dae')]

print(f"Found {len(dae_files)} files to convert: {dae_files}")

for filename in dae_files:
    if not filename.endswith('.dae'):
        continue
        
    input_path = os.path.join(input_dir, filename)
    output_filename = os.path.splitext(filename)[0] + '.glb'
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"\nProcessing: {filename}")
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Import Collada file
    print(f"  Importing: {input_path}")
    bpy.ops.import_scene.collada(filepath=input_path)
    
    # Export as glTF 2.0
    print(f"  Exporting: {output_path}")
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_keep_originals=False,
        export_try_omit_duplicate_materials=True,
        export_image_format='AUTO'
    )
    
    print(f"  Done: {output_filename}")

print("\nConversion complete!")