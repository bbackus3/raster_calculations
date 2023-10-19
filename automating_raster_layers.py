import processing

# path to 2 .tiff images
b8a_path = "C:/Users/BrittenyBackus/OneDrive - RoyceGeo/RFI/2021-07-22-00_00_2021-07-22-23_59_Sentinel-2_L2A_B8A_(Raw).tiff"
b11_path = "C:/Users/BrittenyBackus/OneDrive - RoyceGeo/RFI/2021-07-22-00_00_2021-07-22-23_59_Sentinel-2_L2A_B11_(Raw).tiff"
output_path = "C:/Users/BrittenyBackus/OneDrive - RoyceGeo/RFI/RT_output_early.tiff"

# create raster objects from image
b8a_raster = QgsRasterLayer(b8a_path, "2021-07-22-00_00_2021-07-22-23_59_Sentinel-2_L2A_B8A_(Raw)@1")
b11_raster = QgsRasterLayer(b8a_path, "2021-07-22-00_00_2021-07-22-23_59_Sentinel-2_L2A_B11_(Raw)@1")

# turn raster entries into a list
ras_entries = [b8a_raster, b11_raster]

# dictionary of parameters to pass through
calc_param= {
    'EXPRESSION': '("2021-07-22-00_00_2021-07-22-23_59_Sentinel-2_L2A_B8A_(Raw)@1"-"2021-07-22-00_00_2021-07-22-23_59_Sentinel-2_L2A_B11_(Raw)@1")/("2021-07-22-00_00_2021-07-22-23_59_Sentinel-2_L2A_B8A_(Raw)@1"+"2021-07-22-00_00_2021-07-22-23_59_Sentinel-2_L2A_B11_(Raw)@1")',
    'LAYERS': ras_entries,
    'OUTPUT': output_path
    }

# run the calculation
calc_output = processing.run("qgis:rastercalculator", calc_param)
print('raster calculation complete')
raster_layer_grey = iface.addRasterLayer(output_path)

# Layer coloring
#style = QgsStyle().defaultStyle()
#color_ramp_names = style.colorRampNames()
#color_ramp = style.colorRamp('Turbo').invert

# output path for new raster
color_path = "C:/Users/BrittenyBackus/OneDrive - RoyceGeo/RFI/RT_color_early.tiff"

# dictionary of parameters to pass through
calc_param2= {
    'EXPRESSION': ' if ( "RT_band_early@1" <= -.112,1,0)',
    'LAYERS': [raster_layer_grey],
    'OUTPUT': color_path
    }

# run the calculation
color_output = processing.run("qgis:rastercalculator", calc_param2)
print('color raster calculation complete')
raster_layer_color = iface.addRasterLayer(color_path)


# creating grid layer
ext = b8a_raster.extent()
xmin = ext.xMinimum()
xmax = ext.xMaximum()
ymin = ext.yMinimum()
ymax = ext.yMaximum()
coords = "%f,%f,%f,%f[EPSG:4326]" %(xmin, xmax, ymin, ymax)

grid_path = "C:/Users/BrittenyBackus/OneDrive - RoyceGeo/RFI/grid.geojson"

grid_params = {
    'TYPE': 2,
    'EXTENT': coords,
    'HSPACING': 31.3,
    'VSPACING': 31.3,
    'HOVERLAY': 0,
    'VOVERLAY': 0,
    'CRS': QgsCoordinateReferenceSystem("EPSG:3857"),
    'OUTPUT': grid_path
    }

out1 = processing.run('native:creategrid', grid_params)
grid = QgsVectorLayer(grid_path, 'grid', 'ogr')
QgsProject.instance().addMapLayer(grid)
print('grid created')


# Zonal Statistics
zonal_params = {
    'INPUT_RASTER': raster_layer_color,
    'RASTER_BAND': 1,
    'INPUT_VECTOR': grid,
    'STATISTICS': 6,
    }


#BREAKS HERE
print('calculating zonal statistics...')
zonal_out = processing.run("qgis:zonalstatistics", zonal_params)
print('zonal statistics calculation complete')


# extract by attribute
extracted_path = "C:/Users/BrittenyBackus/OneDrive - RoyceGeo/RFI/RT_extracted.gpkg"

extract_params = {
    'INPUT': zonal_out['INPUT_VECTOR'],
    'FIELD': '_max',
    'VALUE': '1',
    'OPERATOR': 0,
    'OUTPUT': extracted_path
    }

print('running extraction...')
extracted = processing.run("qgis:extractbyattribute", extract_params)
print('extraction complete')