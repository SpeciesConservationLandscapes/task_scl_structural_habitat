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
        self.set_aoi_from_ee(self.inputs["probability"]["ee_path"])


    def calc(self):

        print(land_cover)
        exit()

        # export_path = "scl_poly/{}/scl_polys".format(self.taskdate)
        #
        # self.export_fc_ee(scl_polys, export_path)

    def check_inputs(self):
        super().check_inputs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate", default=datetime.now(timezone.utc).date())
    parser.add_argument("-s", "--species", default="Panthera_tigris")
    parser.add_argument("--scenario", default=SCLTask.CANONICAL)
    options = parser.parse_args()
    sclstats_task = str_hab(**vars(options))
    sclstats_task.run()
