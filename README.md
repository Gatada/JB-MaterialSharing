# JB-NodeSharing
The Blender add-on that saves and loads materials to text files as JSON for easy sharing.

## How It Works

When you copy a material, the currently active material of the currently selected object is copied as follows: The script runs through the node tree, parsing each property and storing its value.

When you paste, the script first creates the nodes, followed by the links between each node.

## Future Feature

I want to be able to select any node of a material and share only the selected settings.

