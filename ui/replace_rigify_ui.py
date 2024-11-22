from bpy.types import (UILayout, Object,
		VIEW3D_MT_rigify, BONE_PT_rigify_buttons, DATA_PT_rigify)
try:
	from bpy.types import (
		DATA_PT_rigify_bone_groups,
		DATA_PT_rigify_layer_names
	)
except:
	# These will fail in Blender 4.0.
	pass
import bpy

from rigify import rig_lists, feature_sets, feature_set_list
from rigify.ui import build_type_list

from ..generation.cloudrig import draw_layers_ui
from ..rig_features.ui import draw_label_with_linebreak, is_cloud_metarig, is_advanced_mode
from ..utils.misc import check_addon
from .rig_types_ui import get_active_pose_bone


def is_blender_version_compatible() -> bool:
	"""Return whether current Blender version is compatible 
	with current CloudRig version."""
	cloudrig_module_name = __package__.replace("rigify.feature_sets.", "").replace(".ui", "")
	cloudrig_module = getattr(feature_sets, cloudrig_module_name)

	cloudrig_min = cloudrig_module.rigify_info['blender']
	cloudrig_max = cloudrig_module.max_blender_version

	return cloudrig_max >= bpy.app.version >= cloudrig_min

def draw_version_check(layout: UILayout) -> bool:
	""" If Blender is too old or new, draw a link to download
		another version of CloudRig.
	"""

	# if not is_blender_version_compatible():
	# 	draw_label_with_linebreak(layout, f"Version mismatch detected.", alert=True)
	# 	draw_label_with_linebreak(layout, f"Download an older or newer version here:", alert=True)
	# 	op = layout.operator('wm.url_open', text="Releases", icon='URL')
	# 	op.url = "https://gitlab.com/blender/CloudRig/-/releases"
	# 	return False

	return True

def draw_cloudrig_rigify_generate(self, context):
	layout = self.layout
	layout.use_property_split=True
	layout.use_property_decorate=False
	metarig = context.object

	if not is_cloud_metarig(metarig):
		return self.draw_old(context)
	
	if not draw_version_check(layout):
		return

	text = "Generate CloudRig"
	if metarig.data.rigify_target_rig:
		text = "Re-Generate CloudRig"
	layout.operator("pose.cloudrig_generate", text=text)
	layout.separator()

def draw_rigify_header(self, context):
	layout = self.layout

	if not is_cloud_metarig(context.object):
		return self.draw_old(context)

	layout.operator('pose.cloudrig_generate', text="Generate")
	layout.operator('object.cloudrig_metarig_toggle')

	if context.mode == 'POSE':
		from rigify.operators.copy_mirror_parameters import draw_copy_mirror_ops
		draw_copy_mirror_ops(self, context)

	if context.mode == 'EDIT_ARMATURE':
		layout.separator()
		layout.operator('armature.metarig_sample_add')
		if is_advanced_mode(context):
			layout.separator()
			layout.operator('armature.rigify_encode_metarig', text="Encode Metarig")
			layout.operator('armature.rigify_encode_metarig_sample', text="Encode Metarig Sample")

def metarig_contains_fk_chain(metarig: Object) -> bool:
	"""Return whether or not a metarig contains an FK rig. Used to determine
	whether animation generation checkbox should appear or not."""
	for pb in metarig.pose.bones:
		if pb.rigify_type!='':
			rig_module = rig_lists.rigs[pb.rigify_type]["module"].Rig
			# This is a bit nasty but importing CloudFKCHainRig and using issubclass() breaks parameter registering (don't ask me why!)
			if 'cloud_fk_chain' in str(rig_module.mro()):
				return True
	return False

def extend_rigify_advanced_panel(self, context):
	"""For newer versions of Rigify (starting with Blender 3.1 I think), 
	there is now an 'Advanced' sub-panel, so we don't have to create our own."""

	metarig = context.object
	if not is_cloud_metarig(metarig):
		return

	layout = self.layout
	layout.use_property_split=True
	layout.use_property_decorate=False
	layout = layout.column()

	cloudrig = metarig.data.cloudrig_parameters

	layout.label(text="CloudRig")

	layout.prop(cloudrig, 'advanced_mode')
	layout.separator()

	# Bone Group Color Parameters
	layout.prop(metarig.data, "rigify_colors_lock", text="Unified Select/Active Colors")
	if metarig.data.rigify_colors_lock:
		layout.prop(metarig.data.rigify_selection_colors, "select", text="Select Color")
		layout.prop(metarig.data.rigify_selection_colors, "active", text="Active Color")
		layout.separator()

	### Root Bone Parameters
	layout.prop(cloudrig, 'create_root')
	if cloudrig.create_root and cloudrig.advanced_mode:
		layout.prop(cloudrig, 'double_root')
		layout.separator()

	# Test Animation Parameters
	if metarig_contains_fk_chain(metarig):
		heading = "Generate Action"
		if cloudrig.test_action:
			heading = "Update Action"
		act_row = layout.row(heading=heading)
		act_row.prop(cloudrig, 'generate_test_action', text="")
		act_col = act_row.column()
		act_col.prop(cloudrig, 'test_action', text="")
		act_col.enabled = cloudrig.generate_test_action

	if not cloudrig.advanced_mode:
		return

	if check_addon(context, 'bone_gizmos'):
		layout.prop(cloudrig, 'auto_setup_gizmos')

@classmethod
def rigify_bone_groups_poll(cls, context):
	# If the current rig has only cloudrig elements, don't draw this panel.
	if is_cloud_metarig(context.object):
		for b in context.object.pose.bones:
			if b.rigify_type != "" and 'cloud' not in b.rigify_type:
				return True
		else:
			return False
	return bpy.types.DATA_PT_rigify_bone_groups.poll_old(context)

def draw_cloud_layer_names(self, context):
	""" Hijack Rigify's Layer Names panel and replace it with our own. """
	obj = context.object
	# If the current rig doesn't have any cloudrig elements, draw Rigify's UI.
	if not is_cloud_metarig(obj):
		bpy.types.DATA_PT_rigify_layer_names.draw_old(self, context)
		return

	arm = obj.data
	cloudrig = arm.cloudrig_parameters
	layout = self.layout

	# Ensure that the layers exist
	if len(arm.rigify_layers) != len(arm.layers):
		layout.operator('pose.cloudrig_layer_init')
		return

	# Layer Preview UI
	draw_layers_ui(layout, obj)

	# Layer Setup UI
	main_row = layout.row(align=True).split(factor=0.05)
	col_number = main_row.column()
	col_layer = main_row.column()

	for i in range(len(arm.rigify_layers)):
		if i in (0, 16):
			col_number.label(text="")
			text = ("Top" if i==0 else "Bottom") + " Row"
			row = col_layer.row()
			row.label(text=text)

		row = col_layer.row(align=True)
		col_number.label(text=str(i) + '.')
		rigify_layer = arm.rigify_layers[i]
		icon = 'RESTRICT_VIEW_OFF' if arm.layers[i] else 'RESTRICT_VIEW_ON'
		row.prop(arm, "layers", index=i, text="", toggle=True, icon=icon)
		icon = 'FAKE_USER_ON' if arm.layers_protected[i] else 'FAKE_USER_OFF'

		row.prop(rigify_layer, "name", text="")
		if rigify_layer.name:
			row.prop(rigify_layer, "row", text="UI Row")
		else:
			row.label(text="")

def draw_rigify_types(self, context):
	id_store = context.window_manager
	posebone = get_active_pose_bone(context)
	rig_name = posebone.rigify_type

	if 'cloud_' not in rig_name:
		return self.draw_old(context)

	layout = self.layout

	# Build types list
	build_type_list(context, id_store.rigify_types)

	# Rig type field
	get_feature_list_func = feature_set_list.get_installed_modules_names if hasattr(feature_set_list, "get_installed_modules_names") else feature_set_list.get_installed_list	# TODO: Remove after 3.0 compatibility drop
	metarig = context.object
	if len(get_feature_list_func()) > 0:
		row = layout.row()
		row.prop(metarig.data, "active_feature_set")
	row = layout.row()
	row.prop_search(posebone, "rigify_type", id_store, "rigify_types", text="Rig type")

	# Rig type parameters / Rig type non-exist alert
	if rig_name != "":
		try:
			rig = rig_lists.rigs[rig_name]['module']
		except (ImportError, AttributeError, KeyError):
			row = layout.row()
			box = row.box()
			box.label(text="ERROR: type \"%s\" does not exist!" % rig_name, icon='ERROR')
		else:
			if hasattr(rig.Rig, 'parameters_ui'):
				rig = rig.Rig
			try:
				rig.parameters_ui
			except AttributeError:
				col = layout.column()
				col.label(text="No options")
			else:
				col = layout.column()
				rig.parameters_ui(layout, posebone.rigify_parameters)

	layout.prop(metarig.data.cloudrig_parameters, 'advanced_mode', text="Show Advanced Options")

def register():
	# Hijack Rigify panels' draw functions.
	DATA_PT_rigify.draw_old = DATA_PT_rigify.draw
	DATA_PT_rigify.draw = draw_cloudrig_rigify_generate

	bpy.types.DATA_PT_rigify_advanced.append(extend_rigify_advanced_panel)

	if bpy.app.version <= (3, 6, 3):
		DATA_PT_rigify_bone_groups.poll_old = DATA_PT_rigify_bone_groups.poll
		DATA_PT_rigify_bone_groups.poll = rigify_bone_groups_poll

		DATA_PT_rigify_layer_names.draw_old = DATA_PT_rigify_layer_names.draw
		DATA_PT_rigify_layer_names.draw = draw_cloud_layer_names

	VIEW3D_MT_rigify.draw_old = VIEW3D_MT_rigify.draw
	VIEW3D_MT_rigify.draw = draw_rigify_header

	BONE_PT_rigify_buttons.draw_old = BONE_PT_rigify_buttons.draw
	BONE_PT_rigify_buttons.draw = draw_rigify_types

def unregister():
	# Restore Rigify panels' draw functions.
	bpy.types.DATA_PT_rigify_advanced.remove(extend_rigify_advanced_panel)
	try:
		DATA_PT_rigify.draw = DATA_PT_rigify.draw_old
		DATA_PT_rigify_bone_groups.poll = DATA_PT_rigify_bone_groups.poll_old
		DATA_PT_rigify_layer_names.draw = DATA_PT_rigify_layer_names.draw_old
		VIEW3D_MT_rigify.draw = VIEW3D_MT_rigify.draw_old
		BONE_PT_rigify_buttons.draw = BONE_PT_rigify_buttons.draw_old
	except AttributeError:
		print("Warning: Looks like CloudRig never got registered?")