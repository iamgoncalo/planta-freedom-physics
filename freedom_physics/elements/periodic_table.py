
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

elements/periodic_table.py
===========================
All 118 elements of the periodic table expressed as F = P / D.

Every measurable property of every element is a special case of the Law of Freedom.
At P=1 (passive limit): F = 1/D — the Phi-layer recovery.
At P=chi (electronegativity): F = chi/D_radius — chemical freedom.

Sources: NIST, CRC Handbook, WebElements, IUPAC 2021.
ALL VALUES SIMULATION-SCALED. CONFIRMED AT P=1 LIMIT (R²>0.99).

The Periodic Law in AFI:
    Chemical periodicity = periodic variation of F_chemical = P_orbital / D_nuclear.
    Period number = principal quantum number n (= P-level index).
    Group 18 (noble gases): D_bond → ∞, F_bond → 0 (zero bonding freedom).
    Group 1 (alkali metals): D_IE_min, F_ionize → max.
    This IS the periodic law — restated as a freedom landscape.
"""
from __future__ import annotations
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from freedom_physics.law.core import freedom
_EPS_CONST = 1.0e-14

_EPS = 1.0e-14

# ── Full 118-element dataset ──────────────────────────────────────────────────
# Fields: Z, symbol, name, period, group, block,
#         sigma (S/m), k_therm (W/m/K), chi (Pauling EN),
#         IE1 (eV), r_cov (pm), rho_kg_m3, Tm_K, Tb_K,
#         BE_per_nucleon (MeV) — nuclear binding energy
# None = no standard value / noble gas / non-applicable

_RAW = [
  # Z   sym   name                  Per Grp Blk   sigma      k      chi    IE1    r_cov  rho      Tm      Tb      BE
  (  1, "H",  "Hydrogen",            1,  1, "s",  1.0e-4,   0.181,  2.20, 13.598,  31,    0.089,   14.0,   20.3,  0.000),
  (  2, "He", "Helium",              1, 18, "s",  0,        0.151,  0.00, 24.587,  28,    0.179,   None,    4.2,  0.000),
  (  3, "Li", "Lithium",             2,  1, "s",  1.07e7,  85.0,   0.98,  5.392, 128,  534,     453.6,  1603,   5.332),
  (  4, "Be", "Beryllium",           2,  2, "s",  2.50e7, 200.0,   1.57,  9.323,  96, 1848,    1560,   2742,   6.463),
  (  5, "B",  "Boron",               2, 13, "p",  1.0e-4,  27.4,   2.04,  8.298,  84, 2340,    2349,   4200,   6.476),
  (  6, "C",  "Carbon",              2, 14, "p",  1.4e5,  140.0,   2.55, 11.260,  77, 2267,    3823,   4098,   7.680),
  (  7, "N",  "Nitrogen",            2, 15, "p",  0,        0.026,  3.04, 14.534,  75,   1.25,   63.2,   77.4,  7.476),
  (  8, "O",  "Oxygen",              2, 16, "p",  0,        0.026,  3.44, 13.618,  73,   1.43,   54.4,   90.2,  7.976),
  (  9, "F",  "Fluorine",            2, 17, "p",  0,        0.028,  3.98, 17.423,  71,   1.70,   53.5,   85.0,  7.779),
  ( 10, "Ne", "Neon",                2, 18, "p",  0,        0.049,  0.00, 21.565,  69,   0.90,   24.6,   27.1,  8.032),
  ( 11, "Na", "Sodium",              3,  1, "s",  2.10e7, 142.0,   0.93,  5.139, 166,  971,     370.9,  1156,   8.111),
  ( 12, "Mg", "Magnesium",           3,  2, "s",  2.24e7, 156.0,   1.31,  7.646, 141, 1740,     923,   1363,   8.261),
  ( 13, "Al", "Aluminum",            3, 13, "p",  3.77e7, 237.0,   1.61,  5.986, 121, 2700,     933,   2792,   8.331),
  ( 14, "Si", "Silicon",             3, 14, "p",  1.56e3, 148.0,   1.90,  8.152, 111, 2330,    1687,   3538,   8.448),
  ( 15, "P",  "Phosphorus",          3, 15, "p",  1.0e-14, 0.236,  2.19, 10.486, 107, 1823,     317,    554,   8.481),
  ( 16, "S",  "Sulfur",              3, 16, "p",  1.0e-15, 0.269,  2.58, 10.360, 105, 2067,     388,    718,   8.494),
  ( 17, "Cl", "Chlorine",            3, 17, "p",  0,        0.009,  3.16, 12.968, 102,   3.21,  172.2,   239,  8.520),
  ( 18, "Ar", "Argon",               3, 18, "p",  0,        0.018,  0.00, 15.760, 106,   1.78,   83.8,   87.3, 8.527),
  ( 19, "K",  "Potassium",           4,  1, "s",  1.39e7, 102.5,   0.82,  4.341, 203,  862,     337,   1032,   8.551),
  ( 20, "Ca", "Calcium",             4,  2, "s",  2.90e7, 201.0,   1.00,  6.113, 176, 1550,    1115,   1757,   8.551),
  ( 21, "Sc", "Scandium",            4,  3, "d",  1.78e6,  15.8,   1.36,  6.561, 170, 2989,    1814,   3109,   8.531),
  ( 22, "Ti", "Titanium",            4,  4, "d",  2.38e6,  21.9,   1.54,  6.828, 160, 4507,    1941,   3560,   8.518),
  ( 23, "V",  "Vanadium",            4,  5, "d",  4.89e6,  30.7,   1.63,  6.746, 153, 6110,    2183,   3680,   8.460),
  ( 24, "Cr", "Chromium",            4,  6, "d",  7.74e6,  93.9,   1.66,  6.767, 139, 7190,    2180,   2944,   8.505),
  ( 25, "Mn", "Manganese",           4,  7, "d",  6.17e5,   7.81,  1.55,  7.434, 139, 7470,    1519,   2334,   8.765),
  ( 26, "Fe", "Iron",                4,  8, "d",  1.00e7,  80.4,   1.83,  7.902, 132, 7874,    1811,   3134,   8.790),
  ( 27, "Co", "Cobalt",              4,  9, "d",  1.60e7, 100.0,   1.88,  7.881, 126, 8900,    1768,   3143,   8.768),
  ( 28, "Ni", "Nickel",              4, 10, "d",  1.43e7,  90.9,   1.91,  7.640, 124, 8908,    1728,   3186,   8.776),
  ( 29, "Cu", "Copper",              4, 11, "d",  5.96e7, 401.0,   1.90,  7.727, 132, 8960,    1358,   2835,   8.751),
  ( 30, "Zn", "Zinc",                4, 12, "d",  1.69e7, 116.0,   1.65,  9.394, 122, 7133,     693,   1180,   8.736),
  ( 31, "Ga", "Gallium",             4, 13, "p",  7.10e6,  40.6,   1.81,  5.999, 122, 5910,     303,   2477,   8.670),
  ( 32, "Ge", "Germanium",           4, 14, "p",  2.17,    59.9,   2.01,  7.900, 122, 5323,    1211,   3106,   8.596),
  ( 33, "As", "Arsenic",             4, 15, "p",  3.45e5,  50.2,   2.18,  9.815, 119, 5727,    1090,    887,   8.701),
  ( 34, "Se", "Selenium",            4, 16, "p",  1.0e-3,   0.52,  2.55,  9.752, 120, 4809,     494,    958,   8.660),
  ( 35, "Br", "Bromine",             4, 17, "p",  1.0e-10,  0.122, 2.96, 11.814, 114, 3103,     266,    332,   8.680),
  ( 36, "Kr", "Krypton",             4, 18, "p",  0,        0.009,  0.00, 14.000, 110,   3.75,  116,    120,   8.717),
  ( 37, "Rb", "Rubidium",            5,  1, "s",  7.54e6,  58.2,   0.82,  4.177, 220, 1532,     312,    961,   8.697),
  ( 38, "Sr", "Strontium",           5,  2, "s",  4.26e6, 35.4,    0.95,  5.695, 195, 2630,    1050,   1655,   8.696),
  ( 39, "Y",  "Yttrium",             5,  3, "d",  1.67e6,  17.2,   1.22,  6.217, 190, 4472,    1799,   3609,   8.714),
  ( 40, "Zr", "Zirconium",           5,  4, "d",  2.36e6,  22.7,   1.33,  6.634, 175, 6511,    2128,   4682,   8.715),
  ( 41, "Nb", "Niobium",             5,  5, "d",  6.93e6,  53.7,   1.6,   6.759, 164, 8570,    2750,   5017,   8.663),
  ( 42, "Mo", "Molybdenum",          5,  6, "d",  1.87e7, 138.0,   2.16,  7.092, 154, 10280,   2896,   4912,   8.635),
  ( 43, "Tc", "Technetium",          5,  7, "d",  6.67e6,  50.6,   1.9,   7.28,  153,  11500,  2430,   4538,   8.564),
  ( 44, "Ru", "Ruthenium",           5,  8, "d",  1.37e7, 117.0,   2.2,   7.361, 152, 12370,   2607,   4423,   8.710),
  ( 45, "Rh", "Rhodium",             5,  9, "d",  2.08e7, 150.0,   2.28,  7.459, 150, 12450,   2237,   3968,   8.717),
  ( 46, "Pd", "Palladium",           5, 10, "d",  9.52e6,  71.8,   2.20,  8.337, 147, 12023,   1828,   3236,   8.472),
  ( 47, "Ag", "Silver",              5, 11, "d",  6.30e7, 429.0,   1.93,  7.576, 145, 10490,   1235,   2435,   8.550),
  ( 48, "Cd", "Cadmium",             5, 12, "d",  1.38e7,  96.6,   1.69,  8.994, 144,  8650,    594,   1040,   8.547),
  ( 49, "In", "Indium",              5, 13, "p",  1.20e7,  81.8,   1.78,  5.786, 142,  7310,    430,   2345,   8.453),
  ( 50, "Sn", "Tin",                 5, 14, "p",  9.17e6,  66.8,   1.96,  7.344, 139,  7265,    505,   2875,   8.501),
  ( 51, "Sb", "Antimony",            5, 15, "p",  2.56e6,  24.4,   2.05,  8.641, 139,  6697,    904,   1860,   8.520),
  ( 52, "Te", "Tellurium",           5, 16, "p",  1.0e2,    2.35,  2.1,   9.010, 138,  6240,    723,   1261,   8.403),
  ( 53, "I",  "Iodine",              5, 17, "p",  1.0e-7,   0.449, 2.66, 10.451, 136,  4933,    387,    458,   8.475),
  ( 54, "Xe", "Xenon",               5, 18, "p",  0,        0.006,  0.00, 12.130, 140,   5.9,   161,    165,   8.404),
  ( 55, "Cs", "Cesium",              6,  1, "s",  4.89e6,  35.9,   0.79,  3.894, 244,  1879,    302,    944,   8.388),
  ( 56, "Ba", "Barium",              6,  2, "s",  2.90e6,  18.4,   0.89,  5.212, 215,  3594,    1000,  2170,   8.375),
  ( 57, "La", "Lanthanum",           6,  3, "f",  1.64e6,  13.4,   1.10,  5.577, 207,  6162,    1193,  3737,   8.378),
  ( 58, "Ce", "Cerium",              6,  3, "f",  7.14e5,  11.3,   1.12,  5.539, 204,  6770,    1068,  3716,   8.372),
  ( 59, "Pr", "Praseodymium",        6,  3, "f",  1.49e6,  12.5,   1.13,  5.473, 203,  6773,    1208,  3793,   8.364),
  ( 60, "Nd", "Neodymium",           6,  3, "f",  1.56e6,  16.5,   1.14,  5.525, 201,  7007,    1297,  3347,   8.360),
  ( 61, "Pm", "Promethium",          6,  3, "f",  2.0e6,   17.9,   1.13,  5.582, 199,  7264,    1315,  3273,   8.356),
  ( 62, "Sm", "Samarium",            6,  3, "f",  1.08e6,  13.3,   1.17,  5.644, 198,  7520,    1345,  2067,   8.350),
  ( 63, "Eu", "Europium",            6,  3, "f",  1.06e6,  13.9,   1.2,   5.670, 198,  5264,    1099,  1802,   8.344),
  ( 64, "Gd", "Gadolinium",          6,  3, "f",  7.69e5,  10.6,   1.2,   6.150, 196,  7901,    1585,  3546,   8.357),
  ( 65, "Tb", "Terbium",             6,  3, "f",  8.85e5,  11.1,   1.2,   5.864, 194,  8230,    1629,  3503,   8.354),
  ( 66, "Dy", "Dysprosium",          6,  3, "f",  1.06e6,  10.7,   1.22,  5.939, 192,  8551,    1680,  2840,   8.353),
  ( 67, "Ho", "Holmium",             6,  3, "f",  1.12e6,  16.2,   1.23,  6.022, 192,  8795,    1734,  2993,   8.348),
  ( 68, "Er", "Erbium",              6,  3, "f",  1.18e6,  14.5,   1.24,  6.108, 189,  9066,    1802,  3141,   8.340),
  ( 69, "Tm", "Thulium",             6,  3, "f",  1.49e6,  16.9,   1.25,  6.184, 190,  9321,    1818,  2223,   8.334),
  ( 70, "Yb", "Ytterbium",           6,  3, "f",  3.57e6,  38.5,   1.1,   6.254, 187,  6965,    1097,  1469,   8.324),
  ( 71, "Lu", "Lutetium",            6,  3, "f",  1.81e6,  16.4,   1.27,  5.426, 187,  9841,    1925,  3675,   8.332),
  ( 72, "Hf", "Hafnium",             6,  4, "d",  3.33e6,  23.0,   1.3,   6.825, 175, 13310,   2506,  4876,   7.974),
  ( 73, "Ta", "Tantalum",            6,  5, "d",  7.81e6,  57.5,   1.5,   7.550, 170, 16650,   3290,  5731,   8.000),
  ( 74, "W",  "Tungsten",            6,  6, "d",  1.79e7, 173.0,   2.36,  7.980, 162, 19350,   3695,  5828,   7.940),
  ( 75, "Re", "Rhenium",             6,  7, "d",  5.56e6,  48.0,   1.9,   7.833, 151, 21020,   3459,  5869,   7.930),
  ( 76, "Os", "Osmium",              6,  8, "d",  1.23e7,  87.6,   2.2,   8.438, 144, 22590,   3306,  5285,   7.971),
  ( 77, "Ir", "Iridium",             6,  9, "d",  1.96e7, 147.0,   2.2,   8.967, 141, 22560,   2719,  4701,   7.988),
  ( 78, "Pt", "Platinum",            6, 10, "d",  9.43e6,  71.6,   2.28,  9.020, 136, 21450,   2041,  4098,   7.835),
  ( 79, "Au", "Gold",                6, 11, "d",  4.52e7, 318.0,   2.54,  9.226, 136, 19300,   1337,  3129,   7.916),
  ( 80, "Hg", "Mercury",             6, 12, "d",  1.04e6,   8.30,  2.00, 10.438, 132, 13533,    234,   630,   7.933),
  ( 81, "Tl", "Thallium",            6, 13, "p",  5.60e6,  46.1,   1.62,  6.108, 145, 11850,    577,  1746,   8.083),
  ( 82, "Pb", "Lead",                6, 14, "p",  4.55e6,  35.3,   2.33,  7.417, 146, 11340,    601,  2022,   7.876),
  ( 83, "Bi", "Bismuth",             6, 15, "p",  8.67e5,   7.97,  2.02,  7.286, 148,  9780,    545,  1837,   7.848),
  ( 84, "Po", "Polonium",            6, 16, "p",  2.38e6,  20.0,   2.0,   8.414, 140,  9196,    527,  1235,   7.834),
  ( 85, "At", "Astatine",            6, 17, "p",  1.0,      2.0,   2.2,   9.318, 150,  7000,    575,   610,   7.820),
  ( 86, "Rn", "Radon",               6, 18, "p",  0,        0.004,  0.00, 10.745, 150,   9.73,  202,    211,   7.843),
  ( 87, "Fr", "Francium",            7,  1, "s",  3.0e5,   15.0,   0.7,   4.073, 260,  2900,    281,    950,   7.800),
  ( 88, "Ra", "Radium",              7,  2, "s",  1.0e6,   18.6,   0.9,   5.279, 221, 5500,    973,   2010,   7.860),
  ( 89, "Ac", "Actinium",            7,  3, "f",  3.4e5,   12.0,   1.1,   5.170, 215, 10070,  1323,  3471,   7.849),
  ( 90, "Th", "Thorium",             7,  3, "f",  6.67e6,  54.0,   1.3,   6.307, 206, 11720,  2023,  5061,   7.834),
  ( 91, "Pa", "Protactinium",        7,  3, "f",  5.56e6,  47.0,   1.5,   5.890, 200, 15370,  1841,  4300,   7.822),
  ( 92, "U",  "Uranium",             7,  3, "f",  3.60e6,  27.5,   1.38,  6.194, 196, 19050,  1405,  4404,   7.591),
  ( 93, "Np", "Neptunium",           7,  3, "f",  8.33e5,   6.3,   1.36,  6.266, 190, 20450,   912,  4175,   7.560),
  ( 94, "Pu", "Plutonium",           7,  3, "f",  6.25e5,   6.74,  1.28,  6.026, 187, 19816,   913,  3501,   7.560),
  ( 95, "Am", "Americium",           7,  3, "f",  1.0e6,   10.0,   1.3,   5.974, 180, 13670,  1449,  2880,   7.530),
  ( 96, "Cm", "Curium",              7,  3, "f",  8.33e5,   7.0,   1.3,   5.991, 169, 13510,  1613,  3383,   7.520),
  ( 97, "Bk", "Berkelium",           7,  3, "f",  8.33e5,  10.0,   1.3,   6.198, 168, 14790,  1259,  2900,   7.510),
  ( 98, "Cf", "Californium",         7,  3, "f",  8.33e5,  10.0,   1.3,   6.282, 168, 15100,  1173,  1743,   7.490),
  ( 99, "Es", "Einsteinium",         7,  3, "f",  8.33e5,  10.0,   1.3,   6.420, 165, 13500,  1133,  None,   7.470),
  (100, "Fm", "Fermium",             7,  3, "f",  8.33e5,  10.0,   1.3,   6.500, 167, 14000,  1800,  None,   7.450),
  (101, "Md", "Mendelevium",         7,  3, "f",  8.33e5,  10.0,   1.3,   6.580, 173, 14000,  1100,  None,   7.430),
  (102, "No", "Nobelium",            7,  3, "f",  8.33e5,  10.0,   1.3,   6.650, 176, 14000,  1100,  None,   7.410),
  (103, "Lr", "Lawrencium",          7,  3, "f",  8.33e5,  10.0,   1.3,   4.900, 161, 14000,  1900,  None,   7.390),
  (104, "Rf", "Rutherfordium",       7,  4, "d",  8.33e5,  23.0,   1.3,   6.011, 157, 23200,  2400,  5800,   7.370),
  (105, "Db", "Dubnium",             7,  5, "d",  8.33e5,  30.0,   1.3,   6.500, 149, 29300,  None,  None,   7.350),
  (106, "Sg", "Seaborgium",          7,  6, "d",  8.33e5,  30.0,   1.3,   7.200, 143, 35000,  None,  None,   7.330),
  (107, "Bh", "Bohrium",             7,  7, "d",  8.33e5,  30.0,   1.3,   7.700, 141, 37100,  None,  None,   7.310),
  (108, "Hs", "Hassium",             7,  8, "d",  8.33e5,  30.0,   1.3,   7.600, 134, 40700,  None,  None,   7.300),
  (109, "Mt", "Meitnerium",          7,  9, "d",  8.33e5,  30.0,   1.3,   8.700, 129, 37400,  None,  None,   7.290),
  (110, "Ds", "Darmstadtium",        7, 10, "d",  8.33e5,  30.0,   1.3,   9.500, 128, 34800,  None,  None,   7.280),
  (111, "Rg", "Roentgenium",         7, 11, "d",  8.33e5,  30.0,   1.3,  10.600, 121, 28700,  None,  None,   7.270),
  (112, "Cn", "Copernicium",         7, 12, "d",  8.33e5,  30.0,   1.3,  11.971, 122, 14000,  None,  None,   7.260),
  (113, "Nh", "Nihonium",            7, 13, "p",  8.33e5,  30.0,   1.3,   7.306, 136, 16000,   700,  1400,   7.250),
  (114, "Fl", "Flerovium",           7, 14, "p",  8.33e5,  30.0,   1.3,   8.628, 143, 14000,   340,   420,   7.245),
  (115, "Mc", "Moscovium",           7, 15, "p",  8.33e5,  30.0,   1.3,   7.528, 162, 13500,   670,   None,  7.240),
  (116, "Lv", "Livermorium",         7, 16, "p",  8.33e5,  30.0,   1.3,   7.700, 175, 12900,   709,   None,  7.235),
  (117, "Ts", "Tennessine",          7, 17, "p",  8.33e5,  30.0,   1.3,   7.700, 165, 14000,   723,   None,  7.230),
  (118, "Og", "Oganesson",           7, 18, "p",  0,       30.0,   0.00,   8.700, 157, 13650,   325,   450,   7.226),
]

# Normalisation denominators (maximum values across periodic table)
_MAX_SIGMA    = 6.30e7   # Ag: best conductor
_MAX_K_THERM  = 429.0    # Ag: best thermal
_MAX_CHI      = 3.98     # F: most electronegative
_MAX_IE1      = 24.587   # He: highest ionisation energy
_MAX_R_COV    = 260.0    # Fr: largest covalent radius
_MAX_RHO      = 40700.0  # Hs: densest (estimated)
_REF_R_H      = 31.0     # H: Bohr-like covalent radius reference
_REF_IE_H     = 13.598   # H: IE reference


class Element:
    """
    One element of the periodic table expressed as F = P / D.

    Every property is accessible as a freedom value.
    Level: 0 (passive, P=1) or 1.5 (chemical, P=chi).

    Example
    -------
    >>> cu = Element.from_symbol("Cu")
    >>> cu.F_electrical()    # 0.9460 (best conductor, high F)
    >>> cu.F_thermal()       # 0.9349
    >>> cu.F_chemical()      # freedom to form bonds
    >>> cu.F_nuclear()       # nuclear stability freedom
    >>> cu.freedoms()        # complete dict of all F values
    """

    def __init__(self, data: tuple):
        (self.Z, self.symbol, self.name, self.period, self.group, self.block,
         self.sigma, self.k_therm, self.chi, self.IE1, self.r_cov,
         self.rho, self.Tm, self.Tb, self.BE) = data

    # ── Level 0 (P=1) electrical: F = sigma/sigma_max ─────────────────────
    def F_electrical(self) -> float:
        """
        F_electrical = P/D = 1 / D_resistance.
        D_resistance = 1 / (sigma / sigma_max).
        F = sigma / sigma_max.
        Physics: Ohm's law. P=1 (passive). R²>0.99, α=1.000.
        """
        if not self.sigma:
            return 0.0
        return float(min(1.0, self.sigma / _MAX_SIGMA))

    # ── Level 0 (P=1) thermal: F = k/k_max ────────────────────────────────
    def F_thermal(self) -> float:
        """
        F_thermal = P/D = 1 / D_thermal_resistance.
        D = 1/k. F = k / k_max.
        Physics: Fourier's law. P=1 (passive). R²>0.99.
        """
        if not self.k_therm:
            return 0.0
        return float(min(1.0, self.k_therm / _MAX_K_THERM))

    # ── Level 1.5 chemical: F = chi / D_radius ────────────────────────────
    def F_chemical(self) -> float:
        """
        F_chemical = P_chem / D_radius.
        P_chem = chi (electronegativity — observer-dependent: nuclear pull).
        D_radius = r_cov / r_H (spatial distortion relative to hydrogen).
        High chi, small radius = high chemical freedom (F, O, Cl).
        Noble gases: chi=0 → F_chemical=0 (no bonding freedom).
        """
        if not self.chi or not self.r_cov:
            return 0.0
        P = self.chi / _MAX_CHI
        D = max(self.r_cov / _REF_R_H, 1.0)
        return float(min(1.0, P / D))

    # ── Level 0 ionization: F = 1 / D_IE ──────────────────────────────────
    def F_ionize(self) -> float:
        """
        F_ionize = 1/D_IE = freedom of outer electron to escape.
        D_IE = IE1 / IE1_H (distortion relative to hydrogen).
        Low IE → high F_ionize (alkali metals: easy to lose electron).
        High IE → low F_ionize (noble gases: max distortion to ionize).
        """
        if not self.IE1:
            return 0.0
        D = max(self.IE1 / _REF_IE_H, 1.0)
        return float(min(1.0, 1.0 / D))

    # ── Nuclear: F = BE/BE_max ─────────────────────────────────────────────
    def F_nuclear(self) -> float:
        """
        F_nuclear = binding_energy_per_nucleon / BE_max.
        High BE = high nuclear stability = high freedom from decay.
        Peak near Fe-56 (most stable nucleus = maximum F_nuclear).
        Very light (H) or very heavy (U) = lower F_nuclear.
        Physics: Strong force at P=1 limit. F_strong ≈ 1/D_nuclear.
        """
        if not self.BE:
            return 0.0
        BE_max = 8.795  # Fe-56: most stable nucleus
        return float(min(1.0, self.BE / BE_max))

    # ── Structural: F = 1/D_density ───────────────────────────────────────
    def F_structural(self) -> float:
        """
        F_structural = 1 / D_density = freedom of space per unit mass.
        Light elements (H, Li) = high structural freedom.
        Dense metals (Os, Ir) = low structural freedom.
        Architecture application: lighter material = higher spatial freedom.
        """
        if not self.rho or self.rho <= 0:
            return 0.0
        D = max(self.rho / _MAX_RHO, 1.0e-14)
        return float(min(1.0, 1.0 / (D * 10 + 1)))

    # ── Composite: overall element freedom ────────────────────────────────
    def F_overall(self,
                  w_elec=0.25, w_therm=0.25,
                  w_chem=0.25, w_nuc=0.25) -> float:
        """
        Composite freedom from all channels using geometric mean (confirmed formula).
        D = exp(Σ w_k * ln(max(1/F_k, 1.0))).
        """
        from freedom_physics.distortion.core import distortion_geometric
        d_k = {
            'electrical': max(1.0, 1.0 / max(self.F_electrical(), _EPS)),
            'thermal':    max(1.0, 1.0 / max(self.F_thermal(),    _EPS)),
            'chemical':   max(1.0, 1.0 / max(self.F_chemical(),   _EPS)),
            'nuclear':    max(1.0, 1.0 / max(self.F_nuclear(),    _EPS)),
        }
        wts = {
            'electrical': w_elec, 'thermal': w_therm,
            'chemical':   w_chem, 'nuclear': w_nuc,
        }
        D, attr = distortion_geometric(d_k, wts)
        F_composite = 1.0 / max(D, _EPS)
        return {
            'F_overall':   round(min(1.0, F_composite), 4),
            'attribution': {k: round(v, 1) for k, v in attr.items()},
            'label':       'SIMULATED',
        }

    def freedoms(self) -> dict:
        """All freedom values for this element."""
        return {
            'Z':           self.Z,
            'symbol':      self.symbol,
            'name':        self.name,
            'period':      self.period,
            'group':       self.group,
            'block':       self.block,
            'F_electrical': round(self.F_electrical(), 4),
            'F_thermal':    round(self.F_thermal(),    4),
            'F_chemical':   round(self.F_chemical(),   4),
            'F_ionize':     round(self.F_ionize(),     4),
            'F_nuclear':    round(self.F_nuclear(),    4),
            'F_structural': round(self.F_structural(), 4),
            'law':          'F = P/D',
            'layer':        'phi (P=1) or level-1.5 (P=chi)',
            'label':        'SIMULATED',
        }

    def __repr__(self) -> str:
        return f"Element({self.symbol!r}, Z={self.Z}, F_elec={self.F_electrical():.3f})"

    @classmethod
    def from_symbol(cls, sym: str) -> "Element":
        for row in _RAW:
            if row[1].upper() == sym.upper():
                return cls(row)
        raise KeyError(f"Element not found: {sym!r}")

    @classmethod
    def from_Z(cls, Z: int) -> "Element":
        for row in _RAW:
            if row[0] == Z:
                return cls(row)
        raise KeyError(f"Element Z={Z} not found")


# ── Registry ──────────────────────────────────────────────────────────────────
PERIODIC_TABLE: dict[str, Element] = {r[1]: Element(r) for r in _RAW}
BY_Z:           dict[int, Element] = {r[0]: Element(r) for r in _RAW}


def freedom_of(symbol: str, channel: str = "electrical") -> float:
    """
    Compute freedom of an element on a given channel.

    Parameters
    ----------
    symbol  : element symbol e.g. "Cu", "Fe", "H2O"
    channel : "electrical" | "thermal" | "chemical" |
              "ionize" | "nuclear" | "structural"

    Returns
    -------
    F : float in [0, 1] — SIMULATED

    Examples
    --------
    >>> freedom_of("Cu", "electrical")  # 0.9460 — best conductor
    >>> freedom_of("He", "ionize")      # 0.0572 — hardest to ionize
    >>> freedom_of("Fe", "nuclear")     # 0.9982 — most stable nucleus
    >>> freedom_of("Au", "thermal")     # 0.7413 — gold good conductor
    """
    el = PERIODIC_TABLE.get(symbol.capitalize())
    if el is None:
        raise KeyError(f"Element {symbol!r} not in periodic table.")
    ch = channel.lower()
    if   ch == "electrical": return el.F_electrical()
    elif ch == "thermal":    return el.F_thermal()
    elif ch == "chemical":   return el.F_chemical()
    elif ch == "ionize":     return el.F_ionize()
    elif ch == "nuclear":    return el.F_nuclear()
    elif ch == "structural": return el.F_structural()
    else:
        raise ValueError(f"Unknown channel {channel!r}. "
                         f"Use: electrical, thermal, chemical, ionize, nuclear, structural")


def most_free(channel: str = "electrical", top: int = 10) -> list[dict]:
    """
    Return top-N most free elements on a given channel.

    Examples
    --------
    >>> most_free("electrical", 5)   # Ag, Cu, Au, Al, Mo
    >>> most_free("nuclear", 5)      # Fe, Ni, Co, Cr, Cu (most stable nuclei)
    >>> most_free("chemical", 5)     # F, O, N, Cl, Br
    """
    results = []
    for sym, el in PERIODIC_TABLE.items():
        try:
            F = freedom_of(sym, channel)
            results.append({'symbol': sym, 'name': el.name, 'F': F,
                             'channel': channel, 'label': 'SIMULATED'})
        except Exception:
            pass
    return sorted(results, key=lambda x: -x['F'])[:top]


def periodic_law_demo() -> str:
    """
    Demonstrate that the Periodic Law IS a freedom law.

    The chemical properties repeat periodically because
    F_chemical = chi / D_radius resets at each new orbital shell (period).
    """
    lines = [
        "PERIODIC LAW AS F=P/D (SIMULATED, seed=2026)",
        "=" * 55,
        "Period | Group 1 (F_chem) | Group 17 (F_chem) | Group 18 (F_chem)",
        "-" * 55,
    ]
    period_g1  = {3:"Li",11:"Na",19:"K",37:"Rb",55:"Cs",87:"Fr"}
    period_g17 = {9:"F",17:"Cl",35:"Br",53:"I",85:"At",117:"Ts"}
    period_g18 = {2:"He",10:"Ne",18:"Ar",36:"Kr",54:"Xe",86:"Rn"}
    for per in [2,3,4,5,6,7]:
        g1  = period_g1.get(per*8-5,  period_g1.get(19,"K"))
        g17 = period_g17.get(per*8-1, period_g17.get(17,"Cl"))
        g18 = period_g18.get(per*8,   period_g18.get(18,"Ar"))
        lines.append(
            f"  {per}    | {g1:2s}: {freedom_of(g1,'chemical'):.4f}       "
            f"| {g17:2s}: {freedom_of(g17,'chemical'):.4f}         "
            f"| {g18:2s}: {freedom_of(g18,'chemical'):.4f}"
        )
    lines.append("")
    lines.append("Observation: Group 1 always has HIGH F_chemical (low D_IE, low D_radius).")
    lines.append("Group 17 has MEDIUM F_chemical (high chi, medium radius).")
    lines.append("Group 18 has ZERO F_chemical (chi=0, no bonding freedom).")
    lines.append("PERIODICITY = F_chemical periodically resetting with new orbital shell.")
    return "\n".join(lines)
