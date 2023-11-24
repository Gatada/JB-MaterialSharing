# Material Sharing
Finally we can stop sharing Materials and Material Nodes as images!

This is the Blender add-on that allows you to copy and paste Blender Materials as JSON! There is also a shortcut to save the active material as a file.

I have been wanting this for a long time, so now I finally spent the time to make it. And it works great! Look for the new options to Copy, Paste and Save Material in the Edit menu.

Coming soon: Please join me on https://matdb.org where we all can share and copy materials freely!

Thanks!
Johan

## Feature Highlights
![Share](https://github.com/Gatada/JB-MaterialSharing/assets/326334/eb5b72d6-46c8-4bb8-9e97-9afe3dc35e15)


* *Copy Entire Material*: It only copies all the nodes and their state and links (make sure nothing is selected, otherwise you will only copy the selection). No files will be included. The copy operation converts the material information into a JSON format, which is a text-based data interchange format. The JSON structure is copied to your clipboard.

* *Copy Partial Material*: If you have selected anything of the active material, clicking **Copy Material** will only copy the selection. This way you can share smaller parts of a larger material. Neat, right?

* *Paste Material*: When you have a copied material on your clipboard, you can select an object and paste it. Easy. *Please note:* It replaces the active material. The operation can be undone.

* *Save Material*: Saves the current active material for the currently selected object in a .json file, stored in the output path of your Blender file, named after the material.


# Installation
![Install](https://github.com/Gatada/JB-MaterialSharing/assets/326334/513f9de0-5130-4b80-b431-b9801fabf860)


This is a very simple process:

1. Download the zipped archive (which you unzip) or just the *jb-materialsharing.py* file to any location.
2. Open Blender Preferences (CMD+comma on MacOS).
3. Go to the Add-ons tab and click the Install at the top.
4. Browse to the downloaded python script and select and install it.
5. Blender will copy the file to its installed addons folder.
6. Finally, enable the script, it is called: Material: *Material Sharing using JSON*

The new shortcuts to copy and paste a JSON material is available at the bottom of the Edit menu. This is also where you will find the option to Savea Material.

## How It Works

When you copy the entire or only selected parts of the active material of the currently selected object, the script runs through the node tree, parsing each property and storing its value. It then stores the links between the nodes. And finally, it formats the data in the JSON format and copies it to your clipboard (Unless you use Save Material).

When you paste, the active material is replaced (and lost) by the pasted material. First the script creates the nodes, gives each property its value, and then establishes all the links between each node.

Let me know what you think!

Johan

