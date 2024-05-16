import logging
from dataclasses import dataclass
from enum import Enum

_logger = logging.getLogger(__name__)


class ProjectGeothermalTechnology(Enum):
    HYDROTHERMAL = 'Hydrothermal'
    EGS = 'EGS'


class ProjectPlantType(Enum):
    FLASH = 'Flash'
    BINARY = 'Binary'


@dataclass
class JediGeothermalResult:
    construction_period_total_jobs: int = None
    construction_period_earnings_MUSD: float = None
    construction_period_output_MUSD: float = None
    construction_period_value_added: float = None

    operating_years_annual_total_jobs: int = None
    operating_years_annual_earnings_MUSD: float = None
    operating_years_annual_output_MUSD: float = None
    operating_years_annual_value_added_MUSD: float = None


@dataclass
class JediGeothermalInputParameters:
    # TODO set default values to None, fake values are stubbed here for demonstration
    project_location_state = 'ID'
    year_of_construction = 2010
    construction_period_months = 21
    nominal_plant_size_mw_net_output = 10
    technology = ProjectGeothermalTechnology.HYDROTHERMAL
    resource_temperature_degC = 200
    resource_depth_m = 2250

    # TODO define all input parameters


def get_construction_period_total_jobs(input_params):
    return input_params.construction_period_months * input_params.nominal_plant_size_mw_net_output


class JediGeothermalClient:
    def __init__(self):
        self._logger = _logger

    def get_jedi_geothermal_result(self, input_params: JediGeothermalInputParameters) -> JediGeothermalResult:
        self._logger.info(f'Calculating JEDI result for: {input_params}')
        result: JediGeothermalResult = JediGeothermalResult()

        result.construction_period_total_jobs = get_construction_period_total_jobs(input_params)

        return result
