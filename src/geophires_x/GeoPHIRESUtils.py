from __future__ import annotations
from os.path import exists
import dataclasses
import json
import numbers
from functools import lru_cache

from scipy.interpolate import interp1d
import numpy as np

from geophires_x.Parameter import *

# user-defined static functions
# define lookup values for the density, specific heat capacity, enthalpy (aka "s", kJ/(kg K))
# and entropy (aka "h", kJ/kg) of water a function of T (deg-c)
# from https://www.engineeringtoolbox.com/water-properties-d_1508.html

# FIXME WIP use iapws library instead of hardcoded values

T = np.array(
    [
        0.01,
        10.0,
        20.0,
        25.0,
        30.0,
        40.0,
        50.0,
        60.0,
        70.0,
        80.0,
        90.0,
        100.0,
        110.0,
        120.0,
        140.0,
        160.0,
        180.0,
        200.0,
        220.0,
        240.0,
        260.0,
        280.0,
        300.0,
        320.0,
        340.0,
        360.0,
        373.946,
    ]
)
DensityH20 = np.array(
    [
        0.99984283,
        0.9998495,
        0.9982067,
        0.997047,
        0.9956488,
        0.9922152,
        0.98804,
        0.9832,
        0.97776,
        0.97179,
        0.96531,
        0.95835,
        0.95095,
        0.94311,
        0.92613,
        0.90745,
        0.887,
        0.86466,
        0.84022,
        0.81337,
        0.78363,
        0.75028,
        0.71214,
        0.66709,
        0.61067,
        0.52759,
        0.322,
    ]
)

# @deprecated(reason='Not used - TODO remove')
SpecificHeatH20 = np.array(
    [
        4.2199,
        4.1955,
        4.1844,
        4.1816,
        4.1801,
        4.1796,
        4.1815,
        4.1851,
        4.1902,
        4.1969,
        4.2053,
        4.2157,
        4.2283,
        4.2435,
        4.2826,
        4.3354,
        4.405,
        4.4958,
        4.6146,
        4.7719,
        4.9856,
        5.2889,
        5.7504,
        6.5373,
        8.208,
        15.004,
        419.1,
    ]
)

EntropyH20 = np.array(
    [
        0.0,
        0.15109,
        0.29648,
        0.36722,
        0.43675,
        0.5724,
        0.70381,
        0.83129,
        0.95513,
        1.0756,
        1.1929,
        1.3072,
        1.4188,
        1.5279,
        1.7392,
        1.9426,
        2.1392,
        2.3305,
        2.5177,
        2.702,
        2.8849,
        3.0685,
        3.2552,
        3.4494,
        3.6601,
        3.9167,
        4.407,
    ]
)
EnthalpyH20 = np.array(
    [
        0.000612,
        42.021,
        83.914,
        104.83,
        125.73,
        167.53,
        209.34,
        251.18,
        293.07,
        335.01,
        377.04,
        419.17,
        461.42,
        503.81,
        589.16,
        675.47,
        763.05,
        852.27,
        943.58,
        1037.6,
        1135.0,
        1236.9,
        1345.0,
        1462.2,
        1594.5,
        1761.7,
        2084.3,
    ]
)
UtilEff = np.array(
    [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0057,
        0.0337,
        0.0617,
        0.0897,
        0.1177,
        0.13,
        0.16,
        0.19,
        0.22,
        0.26,
        0.29,
        0.32,
        0.35,
        0.38,
        0.40,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
        0.4,
    ]
)

interp_density_func = interp1d(T, DensityH20)

# @deprecated(reason='Not used - TODO remove')
interp_specific_heat_func = interp1d(T, SpecificHeatH20)

interp_entropy_func = interp1d(T, EntropyH20)
interp_enthalpy_func = interp1d(T, EnthalpyH20)
interp_util_eff_func = interp1d(T, UtilEff)


@lru_cache(maxsize=None)
def DensityWater(Twater_degC: float) -> float:
    """
    Calculate the density of water as a function of temperature.

    Args:
        Twater_degC: The temperature of water in degrees C.
    Returns:
        The density of water in kg/m3.
    Raises:
        ValueError: If Twater is not a float or convertible to float.
    """
    if not np.can_cast(Twater_degC, float):
        raise ValueError(f'Twater ({Twater_degC}) must be a float or convertible to float.')

    return interp_density_func(Twater_degC) * 1e3


@lru_cache(maxsize=None)
def celsius_to_kelvin(celsius: float) -> float:
    """
    Convert temperature from Celsius to Kelvin.

    Args:
        celsius: Temperature in degrees Celsius.
    Returns:
        Temperature in Kelvin.
    Raises:
        ValueError: If celsius is not a float or convertible to float.
    """
    if not isinstance(celsius, (int, float)):
        raise ValueError("Invalid input for celsius. celsius must be a number.")

    CELSIUS_TO_KELVIN_CONSTANT = 273.15
    return celsius + CELSIUS_TO_KELVIN_CONSTANT


@lru_cache(maxsize=None)
def ViscosityWater(water_temperature: float) -> float:
    """
    The ViscosityWater function is used to calculate the viscosity of water as a function of temperature.
    Args:
        water_temperature: the temperature of water in degrees C
    Returns:
        Viscosity of water in Ns/m2
    Raises:
        ValueError: If water_temperature is not a float or convertible to float.
    """
    if not isinstance(water_temperature, numbers.Real) or water_temperature < 0 or water_temperature > 370:
        raise ValueError(
            f"Invalid input for water_temperature. water_temperature must be a non-negative number and must be within the range of 0 to 370 degrees Celsius. The input value was: {water_temperature}"
        )

    TEMPERATURE_OFFSET = 140
    TEMPERATURE_CONSTANT = 247.8
    WATER_VISCOSITY_CONSTANT = 2.414e-5

    temperature_difference = celsius_to_kelvin(water_temperature) - TEMPERATURE_OFFSET
    temperature_exponent = TEMPERATURE_CONSTANT / temperature_difference
    muwater = WATER_VISCOSITY_CONSTANT * (10**temperature_exponent)

    return muwater


@lru_cache(maxsize=None)
def HeatCapacityWater(Twater_degC: float) -> float:
    """
    Calculate the isobaric specific heat capacity (c_p) of water as a function of temperature.

    Args:
        Twater_degC: The temperature of water in degrees C.
    Returns:
        The isobaric specific heat capacity of water as a function of temperature in J/kg-K.
    Raises:
        ValueError: If Twater_degC is not a float or convertible to float.
    """
    if not isinstance(Twater_degC, numbers.Real) or Twater_degC < 0 or Twater_degC > 500:
        raise ValueError(
            f'Invalid input for Twater_degC.'
            f'Twater_degC must be a non-negative number and must be within the range of 0 to 500 degrees Celsius.'
            f'The input value was: {Twater_degC}'
        )

    # if Twater_degC < T[0] or Twater_degC > T[-1]:
    #     raise ValueError(f'Input temperature {Twater_degC} is out of range [{T[0]},{T[-1]}].')

    try:
    #     from iapws.iapws95 import IAPWS95
    #     return IAPWS95(T=celsius_to_kelvin(Twater_degC), x=0).cp * 1e3
    # except NotImplementedError as nie:
        from iapws.iapws97 import IAPWS97
        return IAPWS97(T=celsius_to_kelvin(Twater_degC), x=0).cp * 1e3
    except NotImplementedError as nie:
        raise ValueError(f'Input temperature {Twater_degC} is out of range or otherwise not implemented') from nie


@lru_cache(maxsize=None)
def RecoverableHeat(Twater: float) -> float:
    """
    the RecoverableHeat function is used to calculate the recoverable heat fraction as a function of temperature

    Args:
        DefaultRecoverableHeat: The default recoverable heat fraction
        Twater: the temperature of water in degrees C
    Returns:
        the recoverable heat fraction as a function of temperature
    Raises:
        ValueError: If Twater is not a float or convertible to float.
        ValueError: If DefaultRecoverableHeat is not a float or convertible to float.
    """
    LOW_TEMP_THRESHOLD = 90.0
    HIGH_TEMP_THRESHOLD = 150.0
    LOW_TEMP_RECOVERABLE_HEAT = 0.43
    HIGH_TEMP_RECOVERABLE_HEAT = 0.66

    if not isinstance(Twater, (int, float)):
        raise ValueError("Twater must be a number")

    if Twater <= LOW_TEMP_THRESHOLD:
        recoverable_heat = LOW_TEMP_RECOVERABLE_HEAT
    elif Twater >= HIGH_TEMP_THRESHOLD:
        recoverable_heat = HIGH_TEMP_RECOVERABLE_HEAT
    else:
        recoverable_heat = 0.0038 * Twater + 0.085

    return recoverable_heat


@lru_cache(maxsize=None)
def VaporPressureWater(Twater: float) -> float:
    """
    The VaporPressureWater function is used to calculate the vapor pressure of water as a function of temperature.
    Uses the Antione Equation.

    Args:
        Twater: the temperature of water in degrees C
    Returns:
        The vapor pressure of water as a function of temperature in kPa
    Raises:
        ValueError: If Twater is not a float or convertible to float.
        ValueError: If Twater is below 0.
    """
    if not isinstance(Twater, (int, float)):
        raise ValueError("Twater must be a number")
    if Twater < 0:
        raise ValueError("Twater must be greater than or equal to 0")

    # Constants for the calculation
    if Twater < 100:
        A = 8.07131
        B = 1730.63
        C = 233.426
    else:
        A = 8.14019
        B = 1810.94
        C = 244.485

    # Calculate the vapor pressure using the Antione Equation
    vapor_pressure = 133.322 * (10 ** (A - B / (C + Twater))) / 1000

    return vapor_pressure


@lru_cache(maxsize=None)
def EntropyH20_func(temperature: float) -> float:
    """
        the EntropyH20_func function is used to calculate the entropy of water as a function of temperature

        Args:
            temperature: the temperature of water in degrees C
        Returns:
            the entropy of water as a function of temperature in kJ/kg-K
    ``    Raises:

    """
    try:
        temperature = float(temperature)
    except ValueError:
        raise TypeError("Input temperature must be a float")

    if temperature < T[0] or temperature > T[-1]:
        raise ValueError(f"Input temperature must be within the range of {T[0]} to {T[-1]} degrees C.")

    entropy = interp_entropy_func(temperature)
    return entropy


@lru_cache(maxsize=None)
def EnthalpyH20_func(temperature: float) -> float:
    """
    the EnthalpyH20_func function is used to calculate the enthalpy of water as a function of temperature

    Args:
        temperature: the temperature of water in degrees C (float)
    Returns:
        the enthalpy of water as a function of temperature in kJ/kg
    Raises:
        TypeError: If temperature is not a float or convertible to float.
        ValueError: If temperature is not within the range of 0 to 373.946 degrees C.
    """
    try:
        temperature = float(temperature)
    except ValueError:
        raise TypeError("Input temperature must be a float")

    if temperature < 0:
        raise ValueError("Input temperature must be a non-negative number.")

    if temperature > T[-1]:
        raise ValueError(f"Input temperature must be within the range of 0 to {T[-1]} degrees C.")

    enthalpy = interp_enthalpy_func(temperature)
    return enthalpy


@lru_cache(maxsize=None)
def UtilEff_func(temperature: float) -> float:
    """
    the UtilEff_func function is used to calculate the utilization efficiency of the system as a function of temperature
    Args:
        temperature: the temperature of water in degrees C
    Returns:
         the utilization efficiency of the system as a function of temperature
    Raises:
        ValueError: If x is not a float or convertible to float.
        ValueError: If x is not within the range of 0 to 373.946 degrees C.
    """
    if not isinstance(temperature, (int, float)):
        raise ValueError("Input temperature must be a number")

    if temperature < T[0] or temperature > T[-1]:
        raise ValueError(f"Temperature must be within the range of {T[0]} to {T[-1]} degrees C.")

    util_eff = interp_util_eff_func(temperature)
    return util_eff


def read_input_file(return_dict_1, logger=None):
    """
    Read input file and return a dictionary of parameters
    :param return_dict_1: dictionary of parameters
    :param logger: logger object
    :return: dictionary of parameters
    :rtype: dict
    """
    logger.info(f'Init {__name__}')

    # Specify path of input file - it will always be the first command line argument.
    # If it doesn't exist, simply run the default model without any inputs

    # read input data (except input from optional filenames)
    if len(sys.argv) > 1:
        f_name = sys.argv[1]
        try:
            if exists(f_name):
                content = []
                logger.info(f'Found filename: {f_name}. Proceeding with run using input parameters from that file')
                with open(f_name, encoding='UTF-8') as f:
                    # store all input in one long string that will be passed to all objects
                    # so they can parse out their specific parameters (and ignore the rest)
                    content = f.readlines()
            else:
                logger.warning(f'File: {f_name} not found - proceeding with default parameter run...')
                return

        except BaseException as ex:
            print(ex)
            logger.error(f'Error {ex} using filename {f_name} proceeding with default parameter run...')
            return

        # successful read of data into list.  Now make a dictionary with all the parameter entries.
        # Index will be the unique name of the parameter.
        # The value will be a "ParameterEntry" structure, with name, value (optionally with units), optional comment
        for line in content:
            if line.startswith("#"):
                # skip any line that starts with "#" - # will be the comment parameter
                continue

            # now deal with the comma delimited parameters
            # split on a comma - that should give us major divisions,
            # Could be:
            # 1) Desc and Val (2 elements),
            # 2) Desc and Val with Unit (2 elements, Unit split from Val by space),
            # 3) Desc, Val, and comment (3 elements),
            # 4) Desc, Val with Unit, Comment (3 elements, Unit split from Val by space)
            # If there are more than 3 commas, we are going to assume it is parseable,
            # and that the commas are in the comment
            elements = line.split(',')

            if len(elements) < 2:
                # not enough commas, so must not be data to parse
                continue

                # we have good data, so make initial assumptions
            description = elements[0].strip()
            s_val = elements[1].strip()
            comment = ""  # cases 1 & 2 - no comment
            if len(elements) == 3:  # cases 3 & 4
                comment = elements[2].strip()

            if len(elements) > 3:
                # too many commas, so assume they are in comments
                for i in range(2, len(elements), 1):
                    comment = comment + elements[i]

            # done with parsing, now create the object and add to the dictionary
            p_entry = ParameterEntry(description, s_val, comment)
            return_dict_1[description] = p_entry  # make the dictionary element

    else:
        logger.warning(
            'No input parameter file specified on the command line. \
        Proceeding with default parameter run... '
        )

    logger.info(f'Complete {__name__}: {sys._getframe().f_code.co_name}')


class _EnhancedJSONEncoder(json.JSONEncoder):
    """
    Enhanced JSON encoder that can handle dataclasses
    :param json.JSONEncoder: JSON encoder
    :return: JSON encoder
    :rtype: json.JSONEncoder
    """

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def json_dumpse(obj) -> str:
    return json.dumps(obj, cls=_EnhancedJSONEncoder)
