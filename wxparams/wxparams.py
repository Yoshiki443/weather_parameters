"""
======================================
 Weather Parameters | Python module
======================================

Python module for calculating meteorological parameters
- Meteorological parameters
- Unit conversion

Copyright (c) Yoshiki Kato @ Weather Data Science

-*- coding: utf-8 -*-
"""
import numpy as np
import copy


"""
*----------------------*
 Wind-related functions
*----------------------*

Calculate wind velocity[m/s, kt, etc] and wind direction[degree]
given U and V components of winds[m/s, kt, etc].
"""
def UV_to_SpdDir(u,v):
    wspd = np.sqrt( u**2 + v**2 )
    wdir = np.rad2deg( np.arctan2(u,v) ) + 180.0

    wdir[ wdir==0 ] = 360.0
    wdir[ wspd==0 ] = 0.0
    return wspd, wdir

"""
Calculate U and V components of winds[m/s, kt, etc]
given wind velocity[m/s, kt, etc] and wind direction[degree].
"""
def SpdDir_to_UV(wspd, wdir):
	u = - wspd * np.sin( np.deg2rad(wdir) )
	v = - wspd * np.cos( np.deg2rad(wdir) )
	return u, v

"""
Convert 360-degree wind direction into 8 directions of winds
like "N, NE, E, SE, S, SW, W, NW", or "8, 1, 2, 3, 4, 5, 6, 7".
"""
def Deg_to_Dir8(val, dir_zero=None, numeric=False):
    dirname = ['N','NE','E','SE','S','SW','W','NW', dir_zero]
    deg = copy.deepcopy(val)
    deg[ deg==0 ] = 720

    deg = deg + 22.5
    deg[ deg>=360 ] -= 360
    deg = (deg/45).astype(np.int64)

    if numeric:
        deg[ deg==8 ] = 999
        deg[ deg==0 ] = 8
        deg[ deg==999 ] = 0
        return deg
    else:
        return np.frompyfunc(lambda x: dirname[x], 1, 1)(deg)

"""
Convert 360-degree wind direction into 16 directions of winds,
like "N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW",
or "16, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15".
"""
def Deg_to_Dir16(val, dir_zero=None, numeric=False):
    dirname = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW',dir_zero]
    deg = copy.deepcopy(val)
    deg[ deg==0 ] = 720

    deg = deg + 11.25
    deg[ deg>=360 ] -= 360
    deg = (deg/22.5).astype(np.int64)

    if numeric:
        deg[ deg==16 ] = 999
        deg[ deg==0 ] = 16
        deg[ deg==999 ] = 0
        return deg
    else:
        return np.frompyfunc(lambda x: dirname[x], 1, 1)(deg)

"""
Calculate cross wind, tail wind, and head wind component of wind
given wind velocity[m/s, kt, etc], wind direction[degree],
and runway direction[degree] of a airpot.
"""
def Cross_Wind(wspd, wdir, rwy):
    return np.abs( wspd * np.sin( np.deg2rad(wdir - rwy) ) )

def Tail_Wind(wspd, wdir, rwy):
    return - wspd * np.cos( np.deg2rad(wdir - rwy) )

def Head_Wind(wspd, wdir, rwy):
    return - Tail_Wind(wspd, wdir, rwy)


"""
*--------------------------*
 Moisture-related functions
*--------------------------*

Calculate dew point temperature[C]
given air temperature[C] and relative humidity[%].
"""
def RH_to_Td(t, rh, formula="Bolton"):
    rh = rh.clip(0.1, None)
    es = T_to_WVP(t, formula)
    e = es * rh / 100
    return WVP_to_T(e, formula)

"""
Calculate relative humidity[%]
given air temperature[C] and dew point temperature[C].
"""
def Td_to_RH(t, td, formula="Bolton"):
    es = T_to_WVP(t, formula)
    e = T_to_WVP(td, formula)
    return 100 * e / es

"""
Calculate saturated water vapor pressure[hPa] given air temperature[C].
If dew point temperature[C] is input, output water vapor pressure[hPa].
There are 3 formulas to calculate this.
(1st) Tetens equation
(2nd) WMO approximation equation
(3rd) Bolton equation
"""
def T_to_WVP(t, formula="Bolton"):
    if formula == "Tetens":
        return 6.1078 * 10 ** (7.5 * t / (t + 237.3))
    elif formula == "WMO":
        return np.exp(19.482 - 4303.4 / (t + 243.5))
    else:
        return 6.112 * np.exp( 17.67 * t / (t + 243.5) )

"""
Calculate air temperature[C] given saturated water vapor pressure[hPa].
If water vapor pressure[hPa] is input, output dew point temperature[C].
(1st) Tetens equation
(2nd) WMO approximation equation
(3rd) Bolton equation
"""
def WVP_to_T(es, formula="Bolton"):
    if formula == "Tetens":
        return 237.3 * np.log10(6.1078/es) / ( np.log10(es/6.1078) - 7.5 )
    elif formula == "WMO":
        return 4303.4 / (19.482 - np.log(es)) - 243.5
    else:
        return 243.5 / ( 17.67/np.log(es/6.112) - 1 )

"""
Calculate dew point depression
given air temperature[C] and dew point temperature[C].
"""
def T_Td(t, td):
    return t - td

"""
Calculate mixing ratio[g/g] given dew point temperature[C] and pressure[hPa].
"""
def Mixing_Ratio(td, p, formula="Bolton"):
    e = T_to_WVP(td, formula)
    return 0.622 * e / (p - e)


"""
*-----------------------------*
 Instability-related functions
*-----------------------------*

Calculate potential temperature[K] given air temperature[C] and pressure[hPa].
"""
def Theta(t, p):
    abs_t = 273.15
    R_div_Cp = 0.2857
    return (t + abs_t) * ( (1000./p) ** R_div_Cp )

"""
Calculate air temperature at lifted condensation level[K]
given air temperature[K] and dew point temperature[K].
The unit of air temperature and dew point temperature should be [K].
"""
def Tlcl(t, td):
    return 1 / ( 1 / (td - 56) + np.log(t/td) / 800 ) + 56

"""
Calculate equivalent potential temperature[K]
given air temperature[C], dew point temperature[C], and pressure[hPa].
Reference : https://www.data.jma.go.jp/add/suishin/jyouhou/pdf/371.pdf
"""
def Theta_e(t, td, p, formula="Bolton"):
    abs_t = 273.15
    R_div_Cp = 0.2857

    e = T_to_WVP(td, formula)
    m = Mixing_Ratio(td, p, formula)

    t = t + abs_t
    td = td + abs_t
    t_lcl = Tlcl(t, td)

    return t * (1000./(p-e))**R_div_Cp * (t/t_lcl)**(0.28*m) * np.exp( (3036./t_lcl - 1.78) * m * (1 + 0.448 * m ) )

"""
Calculate showalter stability index (SSI).
Input parameters are air temperature[C], dew point temperature[C],
and pressure[hPa] at the base level of an air parcel to be lifted,
and air temperature[C] and pressure[hPa] at the destination level
of the lifting air parcel.
"""
def SSI(p0, p1, t0, t1, td0, formula="Bolton"):
    ept = Theta_e(t0, td0, p0, formula)

    tl = np.full_like(t0, -20)
    diff = np.full_like(t0, 100)
    th = 0.001
    step = 120

    for i in range(20):
        step /= 2
        diff[ np.abs(diff)>=th ] = ept[ np.abs(diff)>=th ] - Theta_e(tl[ np.abs(diff)>=th ],tl[ np.abs(diff)>=th ],p1[ np.abs(diff)>=th ],formula)

        if (np.abs(diff) < th).all():
            break
        else:
            tl[ diff >= th ] += step
            tl[ diff <= - th ] -= step

    return t1 - tl

"""
Calculate K-Index
given air temperature[C] and dew point temperature[C] at 850hPa,
air temperature[C] and dew point temperature[C] at 700hPa,
and air temperature[C] at 500hPa.
"""
def K_Index(T850, Td850, T700, Td700, T500):
	return ( T850 - T500 ) + Td850 - ( T700 - Td700 )


"""
*---------------*
 Unit conversion
*---------------*

Unit of wind speed
(1st) m/s  -> knot
(2nd) knot -> m/s
"""
def MPS_to_KT(x):
    return x / 0.51444

def KT_to_MPS(x):
    return x * 0.51444

"""
Unit of length
(1st) meter -> feet
(2nd) feet  -> meter
"""
def M_to_FT(x):
    return x / 0.3048

def FT_to_M(x):
    return x * 0.3048

"""
Unit of temperature
(1st) degrees F -> degrees C
(2nd) degrees C -> degrees F
"""
def degF_to_degC(t):
    return (t - 32.0) / 1.8

def degC_to_degF(t):
    return 1.8 * t + 32.0


"""
Main
"""
def main():
    print("This module includes functions related to major meteorological parameters.")

if __name__ == "__main__":
    main()
