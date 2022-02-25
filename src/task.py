import argparse
import ee
from task_base import SCLTask
from reclass_list import lc_elev_reclass_esa


class SCLStructruralHabitat(SCLTask):
    scale = 300
    BIOME_ZONE_LABEL = "Zone"
    ELEV_ZONE_LABEL = "elev_zone"
    LC_VALUE_LABEL = "lc_value"
    inputs = {
        "land_cover_esa": {
            "ee_type": SCLTask.IMAGECOLLECTION,
            "ee_path": "projects/HII/v1/source/lc/ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992_2015-v207",
            "maxage": 5,
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
        "forest_height": {
            "ee_type": SCLTask.IMAGECOLLECTION,
            "ee_path": "projects/SCL/v1/Panthera_tigris/source/Hansen_Forest_Height",
            "maxage": 5,
        },
        "watermask": {
            "ee_type": SCLTask.IMAGE,
            "ee_path": "projects/HII/v1/source/phys/watermask_jrc70_cciocean",
            "static": True,
        },
    }

    thresholds = {
        "elevation_min_limit": 0,
        "elevation_max_limit": 3350,
        "forest_height_height_threshold": 5,
        "forest_height_cover_threshold": 50,
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
        self.watermask = ee.Image(self.inputs["watermask"]["ee_path"])

    def calc(self):
        def reclass_list_to_fc(dictionary):
            return ee.Feature(None, dictionary)

        reclass_table = ee.FeatureCollection(
            ee.List(lc_elev_reclass_esa).map(reclass_list_to_fc)
        ).filter(ee.Filter.eq("include_class", 1))

        lc_height_test = reclass_table.filter(ee.Filter.eq("include_height", 1))
        lc_height_test_vals = lc_height_test.aggregate_array(self.LC_VALUE_LABEL)
        lc_no_height_test = reclass_table.filter(ee.Filter.eq("include_height", 0))
        lc_no_height_test_vals = lc_no_height_test.aggregate_array(self.LC_VALUE_LABEL)

        forest_height_mask = (
            self.forest_height.updateMask(self.watermask)
            .gte(self.thresholds["forest_height_height_threshold"])
            .reduceResolution(reducer=ee.Reducer.mean(), maxPixels=125)
            .reproject(scale=self.scale, crs=self.crs)
            .gte(self.thresholds["forest_height_cover_threshold"] / 100)
        )
        elev_limit = self.elevation.gte(self.thresholds["elevation_min_limit"]).And(
            self.elevation.lte(self.thresholds["elevation_max_limit"])
        )

        zone_numbers = self.zones.aggregate_histogram(self.BIOME_ZONE_LABEL).keys()
        zones_image = self.zones.reduceToImage(
            properties=[self.BIOME_ZONE_LABEL], reducer=ee.Reducer.mode()
        ).rename(self.BIOME_ZONE_LABEL)

        def landcover_reclass(lc, lc_val, elev_zone, zone, test_height):
            elevation_mask = self.elevation.updateMask(elev_limit)
            zone_lc_elev_no_height = (
                elevation_mask.lte(lc.remap(lc_val, elev_zone))
                .updateMask(zones_image.eq(zone))
                .selfMask()
            )

            zone_lc_elev_height = zone_lc_elev_no_height.updateMask(forest_height_mask)

            if test_height:
                return zone_lc_elev_height
            else:
                return zone_lc_elev_no_height

        def str_hab_by_zone(zone):
            zone_string = ee.String(zone)
            zone_number = ee.Number.parse(zone)
            column = ee.String(self.ELEV_ZONE_LABEL).cat(zone_string)
            elev_zone_esa_no_height = lc_no_height_test.aggregate_array(column)
            elev_zone_esa_height = lc_height_test.aggregate_array(column)

            reclass_img_esa_no_height = landcover_reclass(
                self.land_cover_esa,
                lc_no_height_test_vals,
                elev_zone_esa_no_height,
                zone_number,
                False,
            )
            reclass_img_esa_height = landcover_reclass(
                self.land_cover_esa,
                lc_height_test_vals,
                elev_zone_esa_height,
                zone_number,
                True,
            )

            str_hab_image = ee.Image(
                ee.Algorithms.If(
                    lc_no_height_test_vals.length().eq(0),
                    reclass_img_esa_height,
                    ee.ImageCollection(
                        [reclass_img_esa_no_height, reclass_img_esa_no_height]
                    ).reduce(ee.Reducer.max()),
                )
            )

            return str_hab_image.gt(0).selfMask()

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
