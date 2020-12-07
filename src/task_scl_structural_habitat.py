import argparse
import ee
import time
from datetime import datetime, timezone
from task_base import SCLTask


class str_hab(SCLTask):
    scale = 300
    inputs = {
        "land_cover": {
            "ee_type": SCLTask.IMAGECOLLECTION,
            "ee_path": "projects/HII/v1/source/lc/ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992_2015-v207",
            "maxage": 5,  # until full image collection of structural habitat
        },
        "elevation": {
            "ee_type": SCLTask.IMAGE,
            "ee_path": "CGIAR/SRTM90_V4",
            "static": True,
        },
        "zones": {
            "ee_type": SCLTask.FEATURECOLLECTION,
            "ee_path": "projects/SCL/v1/Panthera_tigris/zones",
            "static": True,
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.land_cover, _ = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["land_cover"]["ee_path"])
        )
        self.elevation = ee.Image(self.inputs["elevation"]["ee_path"])
        self.zones = ee.FeatureCollection(self.inputs["zones"]["ee_path"])
        # self.set_aoi_from_ee(self.inputs["probability"]["ee_path"])

    def calc(self):

        zones_img = self.zones.reduceToImage(
            properties=['Biome_zone'],
            reducer=ee.Reducer.mode()
        ).rename('Biome_zone')

        def remap_elev(from_list, to_list, zone_number, z_img, elev_img, lc_img):
            return (elev_img.lt(
            lc_img.remap(from_list, to_list)
                .updateMask(z_img.eq(zone_number)))
                .multiply(100))


        def remap_lc_by_zone(lc_list, z1_list, z2_list, z3_list, z_img, elev_img, lc_img):
            lc_zone1=remap_elev(lc_list, z1_list, 1,
                                zones_img, elev_img, lc_img)
            lc_zone2=remap_elev(lc_list, z2_list, 2,
                                zones_img, elev_img, lc_img)
            lc_zone3=remap_elev(lc_list, z3_list, 3,
                                zones_img, elev_img, lc_img)
            return (ee.ImageCollection.fromImages([lc_zone1, lc_zone2, lc_zone3])
                .mosaic()
                .selfMask()
                .rename('str_hab'))

        lcClassification=[{
            'category': 'No Data',
            'lcClass': 0,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Cropland, rainfed',
            'lcClass': 10,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Herbaceous cover',
            'lcClass': 11,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Tree or shrub cover',
            'lcClass': 12,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Cropland, irrigated or post‐flooding',
            'lcClass': 20,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Mosaic cropland (>50%) / natural vegetation (tree, shrub, herbaceous cover) (<50%)',
            'lcClass': 30,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Mosaic natural vegetation (tree, shrub, herbaceous cover) (>50%) / cropland (<50%)',
            'lcClass': 40,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Tree cover, broadleaved, evergreen, closed to open (>15%)',
            'lcClass': 50,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, broadleaved, deciduous, closed to open (>15%)',
            'lcClass': 60,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, broadleaved, deciduous, closed (>40%)',
            'lcClass': 61,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, broadleaved, deciduous, open (15‐40%)',
            'lcClass': 62,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, needleleaved, evergreen, closed to open (>15%)',
            'lcClass': 70,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, needleleaved, evergreen, closed (>40%)',
            'lcClass': 71,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, needleleaved, evergreen, open (15‐40%)',
            'lcClass': 72,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, needleleaved, deciduous, closed to open (>15%)',
            'lcClass': 80,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, needleleaved, deciduous, closed (>40%)',
            'lcClass': 81,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, needleleaved, deciduous, open (15‐40%)',
            'lcClass': 82,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, mixed leaf type (broadleaved and needleleaved)',
            'lcClass': 90,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Mosaic tree and shrub (>50%) / herbaceous cover (<50%)',
            'lcClass': 100,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Mosaic herbaceous cover (>50%) / tree and shrub (<50%)',
            'lcClass': 110,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Shrubland',
            'lcClass': 120,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Evergreen shrubland',
            'lcClass': 121,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Deciduous shrubland',
            'lcClass': 122,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Grassland',
            'lcClass': 130,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Lichens and mosses',
            'lcClass': 140,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Sparse vegetation (tree, shrub, herbaceous cover) (<15%)',
            'lcClass': 150,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Sparse tree (<15%)',
            'lcClass': 151,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Sparse shrub (<15%)',
            'lcClass': 152,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Sparse herbaceous cover (<15%)',
            'lcClass': 153,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Tree cover, flooded, fresh or brakish water',
            'lcClass': 160,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Tree cover, flooded, saline water',
            'lcClass': 170,
            'elevation_zone1': 3350,
            'elevation_zone2': 3350,
            'elevation_zone3': 3350
        },
            {
            'category': 'Shrub or herbaceous cover, flooded, fresh/saline/brakish water',
            'lcClass': 180,
            'elevation_zone1': 2000,
            'elevation_zone2': 2000,
            'elevation_zone3': 2000
        },
            {
            'category': 'Urban areas',
            'lcClass': 190,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Bare areas',
            'lcClass': 200,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Consolidated bare areas',
            'lcClass': 201,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Unconsolidated bare areas',
            'lcClass': 202,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Water bodies',
            'lcClass': 210,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
            {
            'category': 'Permanent snow and ice',
            'lcClass': 220,
            'elevation_zone1': 0,
            'elevation_zone2': 0,
            'elevation_zone3': 0
        },
        ]

        lcFrom= []
        zone1= []
        zone2= []
        zone3= []

        for i in range(len(lcClassification)):
            lcFrom.append(lcClassification[i].get('lcClass'))
            zone1.append(lcClassification[i].get('elevation_zone1'))
            zone2.append(lcClassification[i].get('elevation_zone2'))
            zone3.append(lcClassification[i].get('elevation_zone3'))

        str_hab= remap_lc_by_zone(lcFrom, zone1, zone2, zone3, zones_img, self.elevation, self.land_cover)
        print(str_hab)
        exit()

# need to do the following:
    # set up exports (including asset location/naming)
    # aoi
    # refine table values

# export_path = "scl_poly/{}/scl_polys".format(self.taskdate)
#
# self.export_fc_ee(scl_polys, export_path)


def check_inputs(self):
    super().check_inputs()


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate",
                        default = datetime.now(timezone.utc).date())
    parser.add_argument("-s", "--species", default = "Panthera_tigris")
    parser.add_argument("--scenario", default = SCLTask.CANONICAL)
    options=parser.parse_args()
    sclstats_task=str_hab(**vars(options))
    sclstats_task.run()
