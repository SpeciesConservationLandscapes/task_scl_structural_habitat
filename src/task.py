import argparse
import ee
from task_base import SCLTask
from parameters import *


def reclass_list_to_fc(dictionary):
    return ee.Feature(None, dictionary)


class SCLStructruralHabitat(SCLTask):
    scale = 300
    inputs = {
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
        "land_cover_esa": {
            "ee_type": SCLTask.IMAGECOLLECTION,
            "ee_path": "ESA-CCI-LC-L4-LCCS",
            "maxage": 5,
        },
        "forest_height": {
            "ee_type": SCLTask.IMAGECOLLECTION,
            "ee_path": "projects/SCL/v1/Panthera_tigris/source/Hansen_Forest_Height",
            "maxage": 5,
        },
    }

    thresholds = {
        "forest_height_height_threshold": 5,
        "forest_height_cover_threshold": 75,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.land_cover_esa, _ = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["land_cover_esa"]["ee_path"])
        )
        self.forest_height, _ = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["forest_height"]["ee_path"])
        )
        self.elevation = (
            ee.ImageCollection(self.inputs["elevation"]["ee_path"]).select(0).mosaic()
        )
        self.zones = ee.FeatureCollection(self.inputs["zones"]["ee_path"])
        self.zone_numbers = self.zones.aggregate_histogram(BIOME_ZONE_LABEL).keys()
        self.zones_image = self.zones.reduceToImage(
            properties=[BIOME_ZONE_LABEL], reducer=ee.Reducer.mode()
        ).rename(BIOME_ZONE_LABEL)
        self.reclass_table = ee.FeatureCollection(
            ee.List(lc_elev_reclass_esa).map(reclass_list_to_fc)
        ).filter(ee.Filter.eq(INCLUDE_CLASS, 1))

    def landcover_reclass(self, lc_val, elev_zone, zone):
        return (
            self.elevation.lte(self.land_cover_esa.remap(lc_val, elev_zone))
            .updateMask(self.zones_image.eq(zone))
            .selfMask()
        )

    def calc(self):
        lc_height = self.reclass_table.filter(ee.Filter.eq(INCLUDE_HEIGHT, 1))
        lc_height_vals = lc_height.aggregate_array(LC_VALUE_LABEL)
        lc_no_height = self.reclass_table.filter(ee.Filter.eq(INCLUDE_HEIGHT, 0))
        lc_no_height_vals = lc_no_height.aggregate_array(LC_VALUE_LABEL)

        forest_height_mask = (
            self.forest_height.updateMask(self.watermask)
            .gte(self.thresholds["forest_height_height_threshold"])
            .reduceResolution(reducer=ee.Reducer.mean(), maxPixels=125)
            .reproject(scale=self.scale, crs=self.crs)
            .gte(self.thresholds["forest_height_cover_threshold"] / 100)
        )

        def str_hab_by_zone(zone):
            zone_string = ee.String(zone)
            zone_number = ee.Number.parse(zone)
            column = ee.String(ELEV_ZONE_LABEL).cat(zone_string)
            elev_zone_esa_no_height = lc_no_height.aggregate_array(column)
            elev_zone_esa_height = lc_height.aggregate_array(column)

            reclass_img_esa_no_height = self.landcover_reclass(
                lc_no_height_vals, elev_zone_esa_no_height, zone_number
            )
            reclass_img_esa_height = self.landcover_reclass(
                lc_height_vals, elev_zone_esa_height, zone_number
            ).updateMask(forest_height_mask)

            str_hab_image = ee.Image(
                ee.Algorithms.If(
                    lc_no_height_vals.length().eq(0),
                    reclass_img_esa_height,
                    ee.ImageCollection(
                        [reclass_img_esa_no_height, reclass_img_esa_no_height]
                    ).reduce(ee.Reducer.max()),
                )
            )

            return str_hab_image.gt(0).selfMask()

        structural_habitat = (
            ee.ImageCollection(self.zone_numbers.map(str_hab_by_zone))
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
