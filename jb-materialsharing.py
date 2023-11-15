# THE MATERIAL SHARING ADD-ON
#
# Initial release was developed and shared November 2023 by Johan Basberg.
#
# I hope you this will finally allow us all to easily share materials without
# having to resort to screenshots.
# 
# Future feature: allow me to copy some nodes, not the entire material.
#
# Give me a shout-out on Twitter if you find it useful: @johanhwb
#
# Enjoy!
# Johan


bl_info = {
	"author": "Johan Basberg",
	"version": (0, 3, 47),
	"name": "Material Sharing using JSON",
	"blender": (2, 80, 0),
	"category": "Material",
	"location": "TopBar > Edit",
	"description": "Copying and pasting active material as JSON for easy sharing.",
}

import bpy
import json
from mathutils import Vector, Euler

class BlenderEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bpy.types.bpy_prop_array):
			return list(obj)
		elif isinstance(obj, Vector):
			return list(obj)
		elif isinstance(obj, Euler):
			return list(obj)
		return super().default(obj)


class JB_MATERIALSHARING_OT_save_material_json_to_file(bpy.types.Operator):
		bl_idname = "jb_nodesharing.save_material"
		bl_label = "Save Material"
		bl_options = {'REGISTER', 'UNDO'}
		
		def execute(self, context):
			if context.active_object:
				active_material = context.active_object.active_material
				if active_material:
					
					material_json = material_to_json(active_material)
					
					if material_json:
						# Specify an absolute path for the JSON file
						json_file_path = context.scene.render.filepath + active_material.name + '.json'
					
						# Dump the JSON data to the specified file path using the custom encoder
						with open(json_file_path, "w") as json_file:
							json.dump(material_json, json_file, indent=4, cls=BlenderEncoder)
							self.report({'INFO'}, f"Material successfully saved to '{json_file_path}'")
			else:
				self.report({'WARNING'}, 'No active material to copy: Please select an object and try again')
					
			return {'FINISHED'}


class JB_MATERIALSHARING_OT_copy_material(bpy.types.Operator):
	bl_idname = "jb_nodesharing.copy_material"
	bl_label = "Copy Material"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		# Get the active material
		#active_material = context.active_object.active_material
		#
		#if active_material:
		#	# Store the material as text in a property
		#	context.scene.JB_MATERIALSHARING_copy_paste = str(active_material)
		#	self.report({'INFO'}, 'Material copied successfully')
		#else:
		#	self.report({'WARNING'}, 'No active material to copy')
		#
		
		# Example: Convert the active material to JSON
		if context.active_object:
			active_material = context.active_object.active_material
			if active_material:
				
				material_json = self.material_to_json(active_material)
				
				json_formatted = json.dumps(material_json, indent=4, cls=BlenderEncoder)
				context.window_manager.clipboard = json_formatted
				
				self.report({'INFO'}, 'Material successfully copied to clipboard.')
		else:
			self.report({'WARNING'}, 'No active material to copy: Please select an object and try again')
				
		return {'FINISHED'}

		
	def material_to_json(material):
		# Check if the material uses nodes
		if material.use_nodes:
			node_tree = material.node_tree
			nodes_data = []
		
			# Iterate through the nodes in the node tree
			for node in node_tree.nodes:
				node_data = {
					"name": node.name,
					"type": node.bl_idname,
					"location": (node.location.x, node.location.y),
					"inputs": {},
					"outputs": {}
				}
		
				# Store information about inputs
				for input_socket in node.inputs:
					input_data = {
						"links": [{"from_node": link.from_node.name, "from_socket": link.from_socket.name} for link in input_socket.links]
					}
		
					# Check if the socket is connected
					if hasattr(input_socket, "default_value"):
						input_data["default_value"] = input_socket.default_value
		
					node_data["inputs"][input_socket.name] = input_data
		
				# Store information about outputs
				for output_socket in node.outputs:
					output_data = {
						"links": [{"to_node": link.to_node.name, "to_socket": link.to_socket.name} for link in output_socket.links]
					}
		
					# Check if the socket is connected
					if hasattr(output_socket, "default_value"):
						output_data["default_value"] = output_socket.default_value
		
					node_data["outputs"][output_socket.name] = output_data
		
				nodes_data.append(node_data)
		
			material_data = {
				"name": material.name,
				"nodes": nodes_data
			}
		
			return material_data
		else:
			return None




	

					

class JB_MATERIALSHARING_OT_paste_material_from_clipboard(bpy.types.Operator):
	bl_idname = "jb_nodesharing.paste_material_from_clipboard"
	bl_label = "Paste Material"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):		
		active_object = context.active_object
		if active_object is not None and active_object.active_material is not None:

			# Get the JSON string from the clipboard in Blender
			json_string_from_clipboard = context.window_manager.clipboard
			
			
			# Attempt to parse JSON string representing material data
			material_data_from_clipboard = json.loads(json_string_from_clipboard)
			
			# Call the function to create material from the retrieved data
			create_material_from_json(context, material_data_from_clipboard)
			
			try:
				# Attempt to parse JSON string representing material data
				material_data_from_clipboard = json.loads(json_string_from_clipboard)
				
				# Call the function to create material from the retrieved data
				self.create_material_from_json(context, material_data_from_clipboard)
				
				self.report({'INFO'}, 'Material was successfully pasted!')
				
				return {'FINISHED'}
						
			except json.JSONDecodeError:
				# Handle the case where JSON parsing fails
				self.report({'WARNING'}, 'Invalid material format on Clipboard')
				return {'CANCELLED'}
				
			except ValueError as ve:
				self.report({'WARNING'}, f"Error creating material: {ve}")
				return {'CANCELLED'}
				# Handle the specific ValueError, such as displaying a user-friendly error message
			
			except Exception as e:
				self.report({'WARNING'}, f"Unexpected error: {e}")
				print(e)
				return {'CANCELLED'}

		else:
			self.report({'WARNING'}, 'No active object or active material. Select an object with a material')
			return {'CANCELLED'}
			
			
	def create_material_from_json(context, material_data):
		if not isinstance(material_data, dict):
			raise ValueError("Invalid material data. Expected a dictionary.")
			
		# Check for the presence of required keys
		required_keys = ["name", "nodes"]
		for key in required_keys:
			if key not in material_data:
				raise ValueError(f"Invalid material format. Missing key '{key}' in material data.")
		
		# Check if there's an active object with a material slot
		if context.active_object and context.active_object.type == 'MESH' and context.active_object.material_slots:
			
			# Clear all nodes in the node tree
			context.active_object.active_material.node_tree.nodes.clear()
			
			# Create a new material or use the first material slot's material
			# material = context.active_object.material_slots[0].material
			bpy.ops.material.new()
			material = context.active_object.active_material
			material.name = material_data.get("name", "Material")
			
			nodes_data = material_data.get("nodes", [])
			node_dict = {}
			
			# Create nodes
			for node_data in nodes_data:
				node_type = node_data.get("type", "")
				node_name = node_data.get("name", "")
				node_location = node_data.get("location", (0, 0))
			
				# Use shader.new_node_tree instead of ops.node.add for shader nodes
				shader_tree = material.node_tree
				new_node = shader_tree.nodes.new(type=node_type)
				new_node.location.x = node_location[0]
				new_node.location.y = node_location[1]
				
				node_dict[node_name] = new_node
			
			# Connect nodes
			for node_data in nodes_data:
				from_node_name = node_data.get("name", "")
				from_node = node_dict[from_node_name]
			
				for input_name, input_data in node_data.get("inputs", {}).items():
					input_socket = from_node.inputs.get(input_name)
					if input_socket:
						for link_data in input_data.get("links", []):
							to_node_name = link_data.get("from_node", "")
							to_socket_name = link_data.get("from_socket", "")
							to_node = node_dict.get(to_node_name)
							if to_node:
								to_socket = to_node.outputs.get(to_socket_name)
								if to_socket:
									bpy.context.active_object.active_material.node_tree.links.new(input_socket, to_socket)	
			
			# Set default values
			for node_data in nodes_data:
				node_name = node_data.get("name", "")
				node = node_dict.get(node_name)
			
				# Set default values for input sockets
				for input_name, input_data in node_data.get("inputs", {}).items():
					input_socket = node.inputs.get(input_name)
					if input_socket:
						default_value = input_data.get("default_value")
						if default_value is not None:
							input_socket.default_value = default_value
		
			# Switch back to the 3D View context
			# context.area.type = 'VIEW_3D'
		
		else:
			raise ValueError('No active object with material slots found')


classes = (
	JB_MATERIALSHARING_OT_save_material_json_to_file,
	JB_MATERIALSHARING_OT_copy_material,
	JB_MATERIALSHARING_OT_paste_material_from_clipboard
)

def menu_func(self, context):
	self.layout.separator()
	self.layout.operator(JB_MATERIALSHARING_OT_save_material_json_to_file.bl_idname)
	self.layout.separator()
	self.layout.operator(JB_MATERIALSHARING_OT_copy_material.bl_idname)
	self.layout.operator(JB_MATERIALSHARING_OT_paste_material_from_clipboard.bl_idname)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.TOPBAR_MT_edit.append(menu_func)

	bpy.types.Scene.JB_MATERIALSHARING_copy_paste = bpy.props.StringProperty(default="")

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	bpy.types.TOPBAR_MT_edit.remove(menu_func)

	del bpy.types.Scene.JB_MATERIALSHARING_copy_paste

if __name__ == "__main__":
	register()
