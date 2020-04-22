"""
======================================
 Weather Parameters | Python module
======================================

気象に関する関数を集めたpythonモジュールです。
- 気象要素の計算
- 単位変換

Copyright (c) Yoshiki Kato @ Weather Data Science

-*- coding: utf-8 -*-
"""
import numpy as np
import copy


"""
*----------*
 風を扱う関数
*----------*

風のUV成分[m/s, kt, ...etc]から風向風速を計算する
真北は0ではなく、360とする
風速が0だった場合、風向も0とする
"""
def UV_to_SpdDir(u,v):
    wspd = np.sqrt( u**2 + v**2 )
    wdir = np.rad2deg( np.arctan2(u,v) ) + 180.0

    wdir[ wdir==0 ] = 360.0
    wdir[ wspd==0 ] = 0.0
    return wspd, wdir

"""
風向[degree]風速[m/s, kt, ...etc]からUV成分を計算する
"""
def SpdDir_to_UV(wspd, wdir):
	u = - wspd * np.sin( np.deg2rad(wdir) )
	v = - wspd * np.cos( np.deg2rad(wdir) )
	return u, v

"""
風向を360度から8方位に変換する
戻り値はN, NE, E...など方位を表すアルファベットとなる
風向0の場合は指定した文字列に変換される（デフォルトはNone）
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
風向を360度から16方位に変換する
戻り値はN, NNE, NE...など方位を表すアルファベットとなる
風向0の場合は指定した文字列に変換される（デフォルトはNone）
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
空港の滑走路における横風成分(Cross Wind), 追い風成分(Tail Wind), 向かい風成分(Head Wind)を計算
インプットは風速[m/s, kt, ...etc]、風向[degree]
滑走路は2桁のRWY番号ではなく、360度でインプットする
"""
def Cross_Wind(wspd, wdir, rwy):
    return np.abs( wspd * np.sin( np.deg2rad(wdir - rwy) ) )

def Tail_Wind(wspd, wdir, rwy):
    return - wspd * np.cos( np.deg2rad(wdir - rwy) )

def Head_Wind(wspd, wdir, rwy):
    return - Tail_Wind(wspd, wdir, rwy)


"""
*-------------------*
 大気中の水分量を扱う関数
*-------------------*

気温[C]と相対湿度[%]から、露点温度[C]を計算する
飽和水蒸気圧[hPa]の計算は、デフォルトBoltonの式を使用
オプションでTetensの式、WMO近似式も指定可能
相対湿度0%だと計算ができないので、0.1%を最小値としている
"""
def RH_to_Td(t, rh, formula="Bolton"):
    rh = rh.clip(0.1, None)
    es = T_to_WVP(t, formula)
    e = es * rh / 100
    return WVP_to_T(e, formula)

"""
気温[C]と露点温度[C]から、相対湿度[%]を計算する
飽和水蒸気圧の計算は、デフォルトBoltonの式を使用
オプションでTetensの式、WMO近似式も指定可能
"""
def Td_to_RH(t, td, formula="Bolton"):
    es = T_to_WVP(t, formula)
    e = T_to_WVP(td, formula)
    return 100 * e / es

"""
気温[C]から飽和水蒸気圧[hPa]を計算する
露点温度[C]を入力すれば水蒸気圧[hPa]が計算される
デフォルトはBoltonの式を使う
(上) Tetensの式
(中) WMO近似式
(下) Boltonの式
"""
def T_to_WVP(t, formula="Bolton"):
    if formula == "Tetens":
        return 6.1078 * 10 ** (7.5 * t / (t + 237.3))
    elif formula == "WMO":
        return np.exp(19.482 - 4303.4 / (t + 243.5))
    else:
        return 6.112 * np.exp( 17.67 * t / (t + 243.5) )

"""
飽和水蒸気圧[hPa]から気温[C]を計算する
水蒸気圧[hPa]を入力すれば露点温度[C]が計算される
デフォルトはBoltonの式を使う
(上) Tetensの式
(中) WMO近似式
(下) Boltonの式
"""
def WVP_to_T(es, formula="Bolton"):
    if formula == "Tetens":
        return 237.3 * np.log10(6.1078/es) / ( np.log10(es/6.1078) - 7.5 )
    elif formula == "WMO":
        return 4303.4 / (19.482 - np.log(es)) - 243.5
    else:
        return 243.5 / ( 17.67/np.log(es/6.112) - 1 )

"""
気温と露点温度から、湿数を計算する
"""
def T_Td(t, td):
    return t - td

"""
露点温度[C]と気圧[hPa]から、混合比[g/g]を計算する
"""
def mixing_ratio(td, p, formula="Bolton"):
    e = T_to_WVP(td, formula)
    return 0.622 * e / (p - e)


"""
*----------------*
 大気安定度に係る関数
*----------------*

温位[K]を計算する
インプットする気温は[C]単位、気圧は[hPa]単位
"""
def Theta(t, p):
    abs_t = 273.15
    R_div_Cp = 0.2857
    return (t + abs_t) * ( (1000./p) ** R_div_Cp )

"""
持ち上げ凝結高度の温度[K]を計算する
インプットする気温・露点温度とも[K]単位
"""
def Tlcl(t, td):
    return 1 / ( 1 / (td - 56) + np.log(t/td) / 800 ) + 56

"""
相当温位[K]を計算する
インプットする気温・露点温度は[C]単位、気圧は[hPa]単位
計算式は気象庁が採用した算出方法に準ずる
https://www.data.jma.go.jp/add/suishin/jyouhou/pdf/371.pdf
"""
def Theta_e(t, td, p, formula="Bolton"):
    abs_t = 273.15
    R_div_Cp = 0.2857

    e = T_to_WVP(td, formula)
    m = mixing_ratio(td, p, formula)

    t = t + abs_t
    td = td + abs_t
    t_lcl = Tlcl(t, td)

    return t * (1000./(p-e))**R_div_Cp * (t/t_lcl)**(0.28*m) * np.exp( (3036./t_lcl - 1.78) * m * (1 + 0.448 * m ) )

"""
SSIを計算する
インプットする気温・露点温度は[C]単位、気圧は[hPa]単位
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
K-Index
850hPaの気温[C]、露点温度[C]、700hPaの気温[C]、露点温度[C]、500hPaの気温[C]から計算
"""
def K_Index(T850, Td850, T700, Td700, T500):
	return ( T850 - T500 ) + Td850 - ( T700 - Td700 )


"""
*-------*
 単位変換
*-------*

速度の単位変換
(上) m/s  -> knot
(下) knot -> m/s
"""
def MPS_to_KT(x):
    return x / 0.51444

def KT_to_MPS(x):
    return x * 0.51444

"""
速度の単位変換
(上) meter -> feet
(下) feet  -> meter
"""
def M_to_FT(x):
    return x / 0.3048

def FT_to_M(x):
    return x * 0.3048


"""
Main
"""
def main():
    print("This module includes functions related to major meteorological parameters.")

if __name__ == "__main__":
    main()
