#config += debug_and_release
TEMPLATE      = subdirs
CONFIG += ordered
SUBDIRS       = common \
                meshlab \
# IO plugins
                meshlabplugins/io_base\           # a few basic file formats (ply, obj, off), without this you cannot open anything
                meshlabplugins/io_collada\ 
                meshlabplugins/io_json \
		meshlabplugins/filter_meshing \
                meshlabplugins/io_tri\
# Filter plugins
                meshlabplugins/filter_meshing \
# Edit Plugins
                meshlabplugins/edit_pickpoints \
# Sample Plugins
                sampleplugins/sampleedit \
