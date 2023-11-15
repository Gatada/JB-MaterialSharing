# 

bl_info = {
	"author": "Johan Basberg",
	"version": (0, 3, 23),
	"name": "Material Sharing using JSON",
	"blender": (2, 80, 0),
	"category": "Material",
	"description": "Copying and pasting materials for easy sharing",
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


class JB_NODESHARING_OT_save_material_json_to_file(bpy.types.Operator):
		bl_idname = "jb_nodesharing.save_material"
		bl_label = "Save Material"
		bl_options = {'REGISTER', 'UNDO'}
		
		def execute(self, context):
			if bpy.context.active_object:
				active_material = bpy.context.active_object.active_material
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


class JB_NODESHARING_OT_copy_material(bpy.types.Operator):
	bl_idname = "jb_nodesharing.copy_material"
	bl_label = "Copy Material"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		# Get the active material
		#active_material = bpy.context.active_object.active_material
		#
		#if active_material:
		#	# Store the material as text in a property
		#	bpy.context.scene.jb_nodesharing_copy_paste = str(active_material)
		#	self.report({'INFO'}, 'Material copied successfully')
		#else:
		#	self.report({'WARNING'}, 'No active material to copy')
		#
		
		# Example: Convert the active material to JSON
		if bpy.context.active_object:
			active_material = bpy.context.active_object.active_material
			if active_material:
				
				material_json = material_to_json(active_material)
				
				json_formatted = json.dumps(material_json, indent=4, cls=BlenderEncoder)
				bpy.context.window_manager.clipboard = json_formatted
				
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

	
def create_material_from_json(context, material_data):
	if not isinstance(material_data, dict):
		raise ValueError("Invalid material data. Expected a dictionary.")
		
	# Check for the presence of required keys
	required_keys = ["name", "nodes"]
	for key in required_keys:
		if key not in material_data:
			raise ValueError(f"Invalid material format. Missing key '{key}' in material data.")
	
	# Check if there's an active object with a material slot
	if context.active_object and bpy.context.active_object.type == 'MESH' and context.active_object.material_slots:
		
		# Create a new material or use the first material slot's material
		# material = context.active_object.material_slots[0].material
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
		for link_data in material_data.get("links", []):
			from_node_name = link_data.get("from_node", "")
			from_socket_name = link_data.get("from_socket", "")
			to_node_name = link_data.get("to_node", "")
			to_socket_name = link_data.get("to_socket", "")
			
			from_node = node_dict.get(from_node_name)
			to_node = node_dict.get(to_node_name)
			
			if from_node and to_node:
				from_socket = from_node.outputs.get(from_socket_name)
				to_socket = to_node.inputs.get(to_socket_name)
			
				if from_socket and to_socket:
					# Create a new link between nodes without using bpy.ops.node.link
					material.node_tree.links.new(from_socket, to_socket)

	#	for node_data in nodes_data:
	#		node_name = node_data.get("name", "")
	#		node = node_dict.get(node_name)
	#		
	#		for output_name, output_data in node_data.get("outputs", {}).items():
	#			output_socket = node.outputs.get(output_name)
	#			if output_socket:
	#				for link_data in output_data.get("links", []):
	#					to_node_name = link_data.get("to_node", "")
	#					to_socket_name = link_data.get("to_socket", "")
	#					to_node = node_dict.get(to_node_name)
	#					if to_node:
	#						to_socket = to_node.inputs.get(to_socket_name)
	#						if to_socket:
	#							bpy.ops.node.link(type='SHADER', from_socket=output_socket, to_socket=to_node.inputs.get(to_socket_name))
	#							# material.node_tree.links.new(from_socket, to_socket)
	#		
	#		# Set default values for input sockets
	#		for input_name, input_data in node_data.get("inputs", {}).items():
	#			input_socket = node.inputs.get(input_name)
	#			if input_socket:
	#				default_value = input_data.get("default_value")
	#				if default_value is not None:
	#					input_socket.default_value = default_value
		
	
		# Switch back to the 3D View context
		# bpy.context.area.type = 'VIEW_3D'
	
	else:
		raise ValueError('No active object with material slots found')
					

class JB_NODESHARING_OT_paste_material_from_clipboard(bpy.types.Operator):
	bl_idname = "jb_nodesharing.paste_material_from_clipboard"
	bl_label = "Paste Material"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		# Get the stored material text
		#
		#	material_text = bpy.context.scene.jb_nodesharing_copy_paste
		#
		#	if material_text:
		#		# Create a new material
		#		new_material = bpy.data.materials.new(name="Pasted Material")
		#		new_material.use_nodes = True
		#		bpy.context.active_object.data.materials.append(new_material)
		#		bpy.context.active_object.active_material = new_material
		#
		#		# Create a new node tree and parse the material text
		#		tree = new_material.node_tree
		#		tree.nodes.clear()
		#		bpy.ops.node.read_file(filepath="", files=[{"name": "Material Nodes", "content": material_text}])
		#
		#		self.report({'INFO'}, 'Material pasted successfully')
		#	else:
		#		self.report({'WARNING'}, 'No material text to paste')
		
		# active_object = bpy.context.active_object
		# if active_object is not None and active_object.active_material is not None:
		# 	active_material = active_object.active_material
		# 	create_material_from_json(material_data)
		# else:
		# 	print("No active object or active material.")
		
		# Get the JSON string from the clipboard in Blender
		json_string_from_clipboard = bpy.context.window_manager.clipboard
		
		try:
			# Attempt to parse JSON string representing material data
			material_data_from_clipboard = json.loads(json_string_from_clipboard)
			
			# Call the function to create material from the retrieved data
			create_material_from_json(context, material_data_from_clipboard)
			
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
			return {'CANCELLED'}

	def parse_material(self, material):
		# Print basic information about the material
		print(f"Material Name: {material.name}")
		print(f"Use Nodes: {material.use_nodes}")
		
		# Access the material nodes
		if material.use_nodes:
			node_tree = material.node_tree
			nodes = node_tree.nodes

			self.print_node_connections(node_tree)
		
			# Print information about each node in the material
			for node in nodes:
				print("=" * 30)
				print(f"Node Type: {node.type}")
				print(f"Node Name: {node.name}")
				print(f"Node: {node}")
				
				self.parse_properties(node)
				
				print(f"Location: {node.location}\n\n")
		
				#	# Additional properties depending on the node type
				#	if node.type == 'BSDF_PRINCIPLED':
				#		print(f"Base Color: {node.base_color}")
				#		print(f"Metallic: {node.metallic}")
				#		print(f"Roughness: {node.roughness}")
				#	elif node.type == 'ShaderNodeTexImage':
				#	print(f"Image: {node.image}")
		
		return {'FINISHED'}
	
	def print_node_connections(self, node_tree):
		print("-" * 30)
		print("\n\nNODE CONNECTIONS")
		for link in node_tree.links:
			print(f"From Node: {link.from_node.name}")
			print(f"From Socket: {link.from_socket.name}")
			print(f"To Node: {link.to_node.name}")
			print(f"To Socket: {link.to_socket.name}")
			print("-" * 30)
		return {'FINISHED'}

		
	def parse_properties(self, bpy_struct):
		for prop_name, prop_info in bpy_struct.bl_rna.properties.items():
			# Check if the property is valid for the current context
			if bpy_struct.is_property_hidden(prop_name) or not bpy_struct.is_property_set(prop_name):
				continue
		
			# Access the property value
			prop_value = getattr(bpy_struct, prop_name)
		
			print(f"Property Name: {prop_name}")
			print(f"Property Type: {prop_info.type}")
			print(f"Property Value: {prop_value}")
			print("=" * 30)
		
		return {'FINISHED'}
		

classes = (
	JB_NODESHARING_OT_save_material_json_to_file,
	JB_NODESHARING_OT_copy_material,
	JB_NODESHARING_OT_paste_material_from_clipboard
)

def menu_func(self, context):
	self.layout.operator(JB_NODESHARING_OT_save_material_json_to_file.bl_idname)
	self.layout.operator(JB_NODESHARING_OT_copy_material.bl_idname)
	self.layout.operator(JB_NODESHARING_OT_paste_material_from_clipboard.bl_idname)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.TOPBAR_MT_edit.append(menu_func)

	bpy.types.Scene.jb_nodesharing_copy_paste = bpy.props.StringProperty(default="")

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	bpy.types.TOPBAR_MT_edit.remove(menu_func)

	del bpy.types.Scene.jb_nodesharing_copy_paste

if __name__ == "__main__":
	register()
