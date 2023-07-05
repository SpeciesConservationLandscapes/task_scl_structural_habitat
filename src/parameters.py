from Panthera_tigris_pars import (
    HEIGHT as PANTHERA_TIGRIS_HEIGHT,
    LC_RECLASS as PANTHERA_TIGRIS_LC_RECLASS,
)
from Panthera_leo_pars import (
    HEIGHT as PANTHERA_LEO_HEIGHT,
    LC_RECLASS as PANTHERA_LEO_LC_RECLASS,
)
from Panthera_onca_pars import (
    HEIGHT as PANTHERA_ONCA_HEIGHT,
    LC_RECLASS as PANTHERA_ONCA_LC_RECLASS,
)
from Bison_bison_pars import (
    HEIGHT as BISON_BISON_HEIGHT,
    LC_RECLASS as BISON_BISON_LC_RECLASS,
)

BIOME_ZONE_LABEL = "Zone"
ELEV_ZONE_LABEL = "elev_zone"
LC_VALUE_LABEL = "lc_value"
INCLUDE_CLASS = "include_class"
INCLUDE_HEIGHT = "include_height"

HEIGHT = {
    "Panthera_tigris": PANTHERA_TIGRIS_HEIGHT,
    "Panthera_leo": PANTHERA_LEO_HEIGHT,
    "Panthera_onca": PANTHERA_ONCA_HEIGHT,
    "Bison_bison": BISON_BISON_HEIGHT,
}

LC_ELEV_RECLASS_ESA = {
    "Panthera_tigris": PANTHERA_TIGRIS_LC_RECLASS,
    "Panthera_leo": PANTHERA_LEO_LC_RECLASS,
    "Panthera_onca": PANTHERA_ONCA_LC_RECLASS,
    "Bison_bison": BISON_BISON_LC_RECLASS,
}
