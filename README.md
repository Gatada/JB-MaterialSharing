# Material Sharing
The Blender add-on that saves and loads materials to text files as JSON for easy sharing.

## Feature Highlights

* *Save Material*: Saves the current active material for the currently selected object in a .json file, stored in the output path of your Blender file, named after the material.

* *Copy Entire Material*: It only copies all the nodes and their state and links (make sure nothing is selected, otherwise you will only copy the selection). No files will be included. The copy operation converts the material information into a JSON format, which is a text-based data interchange format. The JSON structure is copied to your clipboard.

* *Copy Partial Material*: If you have selected anything of the active material, clicking **Copy Material** will only copy the selection. This way you can share smaller parts of a larger material. Neat, right?

* *Paste Material*: When you have a copied material on your clipboard, you can select an object and paste it. Easy. *Please note:* It replaces the active material. The operation can be undone.

## How It Works

When you copy the entire or only selected parts of the active material of the currently selected object, the script runs through the node tree, parsing each property and storing its value. It then stores the links between the nodes. And finally, it formats the data in the JSON format and copies it to your clipboard (Unless you use Save Material).

When you paste, the active material is replaced (and lost) by the pasted material. First the script creates the nodes, gives each property its value, and then establishes all the links between each node.

Let me know what you think!

Johan

