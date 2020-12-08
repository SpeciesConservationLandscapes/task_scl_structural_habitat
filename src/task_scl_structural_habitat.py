import argparse
import ee
import time
from datetime import datetime, timezone
from task_base import SCLTask


class SCLStructruralHabitat(SCLTask):
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
        "lc_elev_reclass": {
            "ee_type": SCLTask.FEATURECOLLECTION,
            "ee_path": "projects/SCL/v1/Panthera_tigris/source/landcover_reclass_lookup/lc_reclass_test",  # need final table
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
        self.lc_elev_reclass = ee.FeatureCollection(
            self.inputs["lc_elev_reclass"]["ee_path"]
        )

    def calc(self):

        zone_numbers = self.zones.aggregate_histogram("Biome_zone").keys()
        lc_val = self.lc_elev_reclass.aggregate_array("lc_value")

        zones_img = self.zones.reduceToImage(
            properties=["Biome_zone"], reducer=ee.Reducer.mode()
        ).rename("Biome_zone")

        def str_hab_by_zone(li):
            zone_string = ee.String(li)
            zone_number = ee.Number.parse(li)
            column = ee.String("elev_zone").cat(zone_string)
            elev_zone = self.lc_elev_reclass.aggregate_array(column)
            reclass_img = (
                self.elevation.lt(self.land_cover.remap(lc_val, elev_zone))
                .updateMask(zones_img.eq(zone_number))
                .selfMask()
            )
            return reclass_img

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
    parser.add_argument("-d", "--taskdate", default=datetime.now(timezone.utc).date())
    parser.add_argument("-s", "--species", default="Panthera_tigris")
    parser.add_argument("--scenario", default=SCLTask.CANONICAL)
    options = parser.parse_args()
    sclstrhab_task = SCLStructruralHabitat(**vars(options))
    sclstrhab_task.run()
