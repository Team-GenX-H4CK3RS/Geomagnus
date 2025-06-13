import ee
import geemap

# Authenticate and initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# Create a geemap instance
Map = geemap.Map(center=[15.9129, 79.7400], zoom=7)

# Define study area geometry for Andhra Pradesh and Karnataka
geometry = ee.Geometry.Polygon([
    [[74.0, 11.5], [81.5, 11.5], [81.5, 19.5], 
     [74.0, 19.5], [74.0, 11.5]]
])

# Load ASTER imagery collection
aster_collection = (ee.ImageCollection("ASTER/AST_L1T_003")
                    .filterBounds(geometry)
                    .filterDate('2020-01-01', '2024-12-31')
                    .filter(ee.Filter.lt('CLOUD_COVER', 10))
                    .median())

# Load Landsat 8 collection
landsat_collection = (ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
                      .filterBounds(geometry)
                      .filterDate('2020-01-01', '2024-12-31')
                      .filter(ee.Filter.lt('CLOUD_COVER', 10))
                      .median())

# Atmospheric correction for ASTER
aster_corrected = aster_collection.select(
    ['B01', 'B02', 'B03', 'B04', 'B05', 
     'B06', 'B07', 'B08', 'B09']).multiply(0.0001)

# Mineral Indices Calculations
ferric_iron = aster_corrected.expression(
    '(B02 / B01)', {
        'B02': aster_corrected.select('B02'),
        'B01': aster_corrected.select('B01')
    }).rename('Ferric_Iron')

alunite = aster_corrected.expression(
    '(B06 / B05) * 0.5 + (B07 / B05) * 0.5', {
        'B06': aster_corrected.select('B06'),
        'B05': aster_corrected.select('B05'),
        'B07': aster_corrected.select('B07')
    }).rename('Alunite')

kaolinite = aster_corrected.expression(
    '(B06 / B05) * (B04 / B06)', {
        'B06': aster_corrected.select('B06'),
        'B05': aster_corrected.select('B05'),
        'B04': aster_corrected.select('B04')
    }).rename('Kaolinite')

carbonate = aster_corrected.expression(
    '(B08 / B09)', {
        'B08': aster_corrected.select('B08'),
        'B09': aster_corrected.select('B09')
    }).rename('Carbonate')

silica = aster_corrected.expression(
    '(B10 / B11) * 1.3', {
        'B10': aster_corrected.select('B10'),
        'B11': aster_corrected.select('B11')
    }).rename('Silica')

# Landsat-based indices
rock_index = landsat_collection.expression(
    '(B7 - B2) / (B7 + B2)', {
        'B7': landsat_collection.select('SR_B7'),
        'B2': landsat_collection.select('SR_B2')
    }).rename('Rock_Index')

iron_hydroxyl = landsat_collection.expression(
    '(B3 / B1) + (B5 / B7)', {
        'B3': landsat_collection.select('SR_B3'),
        'B1': landsat_collection.select('SR_B1'),
        'B5': landsat_collection.select('SR_B5'),
        'B7': landsat_collection.select('SR_B7')
    }).rename('Iron_Hydroxyl')

# Combine all mineral indices
mineral_indices = ee.Image.cat([
    ferric_iron, alunite, kaolinite, carbonate, 
    silica, rock_index, iron_hydroxyl
])

# Unsupervised classification for Gold Potential Mapping
training = mineral_indices.sample(
    region=geometry,
    scale=30,
    numPixels=5000
)

clusterer = ee.Clusterer.wekaKMeans(5).train(training)
classified = mineral_indices.cluster(clusterer)
gold_potential = classified.remap([0,1,2,3,4], [0,1,2,3,4]).rename('Gold_Potential')

# Visualization parameters
vis_params = {
    'min': 0, 'max': 4, 
    'palette': ['blue', 'green', 'yellow', 'orange', 'red']
}

# Add layers to the map
Map.addLayer(gold_potential.clip(geometry), vis_params, 'Gold Potential Map')
Map.addLayer(geometry, {'color': 'white'}, 'Study Area', False)

# Export results to Drive
task = ee.batch.Export.image.toDrive(
    image=gold_potential.clip(geometry),
    description='AP_Karnataka_Gold_Potential',
    scale=30,
    region=geometry,
    maxPixels=1e10,
    fileFormat='GeoTIFF'
)
task.start()

# Display the map
Map.addLayerControl()
Map
