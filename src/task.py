import argparse
import ee
import time
from datetime import datetime, timezone
from task_base import SCLTask


class SCLStructruralHabitat(SCLTask):
    scale = 300
    BIOME_ZONE_LABEL = "Zone"
    ELEV_ZONE_LABEL = "elev_zone"
    LC_VALUE_LABEL = "lc_value"
    inputs = {
        "land_cover_esa": {
            "ee_type": SCLTask.IMAGECOLLECTION,
            "ee_path": "projects/HII/v1/source/lc/ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992_2015-v207",
            "maxage": 5,  # until full image collection of structural habitat
        },
        "land_cover_modis": {
            "ee_type": SCLTask.IMAGECOLLECTION,
            "ee_path": "MODIS/006/MCD12Q1",
            "maxage": 2,  # until full image collection of structural habitat
        },
        "elevation": {
            "ee_type": SCLTask.IMAGECOLLECTION,
            "ee_path": "JAXA/ALOS/AW3D30/V3_2",
            "static": True,
        },
        "zones": {
            "ee_type": SCLTask.FEATURECOLLECTION,
            "ee_path": "projects/SCL/v1/Panthera_tigris/zones",
            "static": True,
        },
        "lc_elev_reclass_esa": {
            "ee_type": SCLTask.FEATURECOLLECTION,
            "ee_path": "projects/SCL/v1/Panthera_tigris/landcover_reclass_lookup/lc_elev_reclass_esa",
            "static": True,
        },
        "lc_elev_reclass_modis": {
            "ee_type": SCLTask.FEATURECOLLECTION,
            "ee_path": "projects/SCL/v1/Panthera_tigris/landcover_reclass_lookup/lc_elev_reclass_modis",
            "static": True,
        },
    }

    thresholds = {
        "elevation_min_limit": 0,
        "elevation_max_limit": 3350,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.land_cover_esa, _ = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["land_cover_esa"]["ee_path"])
        )
        self.land_cover_modis, _ = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["land_cover_modis"]["ee_path"])
        )
        self.elevation = (
            ee.ImageCollection(self.inputs["elevation"]["ee_path"])
            .select(0)
            .mosaic()
        )
        self.zones = ee.FeatureCollection(self.inputs["zones"]["ee_path"])
        self.lc_elev_reclass_esa = ee.FeatureCollection(
            self.inputs["lc_elev_reclass_esa"]["ee_path"]
        )
        self.lc_elev_reclass_modis = ee.FeatureCollection(
            self.inputs["lc_elev_reclass_modis"]["ee_path"]
        )

    def calc(self):
        zone_numbers = self.zones.aggregate_histogram(
            self.BIOME_ZONE_LABEL
        ).keys()
        lc_val_esa = self.lc_elev_reclass_esa.aggregate_array(
            self.LC_VALUE_LABEL
        )
        lc_val_modis = self.lc_elev_reclass_modis.aggregate_array(
            self.LC_VALUE_LABEL
        )

        zones_img = self.zones.reduceToImage(
            properties=[self.BIOME_ZONE_LABEL], reducer=ee.Reducer.mode()
        ).rename(self.BIOME_ZONE_LABEL)

        def str_hab_by_zone(li):
            elev_limit = self.elevation.gte(
                self.thresholds["elevation_min_limit"]
            ).And(self.elevation.lte(self.thresholds["elevation_max_limit"]))
            zone_string = ee.String(li)
            zone_number = ee.Number.parse(li)
            column = ee.String(self.ELEV_ZONE_LABEL).cat(zone_string)
            elev_zone_esa = self.lc_elev_reclass_esa.aggregate_array(column)
            elev_zone_modis = self.lc_elev_reclass_modis.aggregate_array(column)
            reclass_img_esa = (
                self.elevation.updateMask(elev_limit)
                .lte(self.land_cover_esa.remap(lc_val_esa, elev_zone_esa))
                .updateMask(zones_img.eq(zone_number))
                .selfMask()
            )

            reclass_img_modis = (
                self.elevation.updateMask(elev_limit)
                .lte(
                    self.land_cover_modis.select(0).remap(
                        lc_val_modis, elev_zone_modis
                    )
                )
                .updateMask(zones_img.eq(zone_number))
                .selfMask()
            )
            return reclass_img_modis.gt(0).And(reclass_img_esa.gt(0)).selfMask()

        structural_habitat = (
            ee.ImageCollection(zone_numbers.map(str_hab_by_zone))
            .mosaic()
            .rename("str_hab")
        )

        self.export_image_ee(structural_habitat, "structural_habitat")


def check_inputs(self):
    super().check_inputs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate")
    parser.add_argument("-s", "--species")
    parser.add_argument("--scenario")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing outputs instead of incrementing",
    )
    options = parser.parse_args()
    sclstrhab_task = SCLStructruralHabitat(**vars(options))
    sclstrhab_task.run()
