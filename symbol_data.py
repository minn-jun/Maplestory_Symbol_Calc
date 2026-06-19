from dataclasses import dataclass


MESO_UNIT = 10000


@dataclass(frozen=True)
class SymbolArea:
    key: str
    name: str
    group: str
    required_level: int
    max_level: int
    base_force: int
    force_per_level: int
    costs: dict[int, int]

    @property
    def max_force(self):
        return self.base_force + (self.max_level - 1) * self.force_per_level


SYMBOL_AREAS = {
    "vanishing_journey": SymbolArea("vanishing_journey", "소멸의 여로", "arcane", 200, 20, 30, 10, {
        2: 97, 3: 123, 4: 166, 5: 226, 6: 306, 7: 404, 8: 522, 9: 660, 10: 818,
        11: 999, 12: 1201, 13: 1426, 14: 1674, 15: 1945, 16: 2242, 17: 2563,
        18: 2910, 19: 3283, 20: 3682,
    }),
    "chu_chu_island": SymbolArea("chu_chu_island", "츄츄 아일랜드", "arcane", 210, 20, 30, 10, {
        2: 121, 3: 153, 4: 206, 5: 280, 6: 378, 7: 498, 8: 642, 9: 810, 10: 1002,
        11: 1221, 12: 1465, 13: 1736, 14: 2034, 15: 2359, 16: 2714, 17: 3097,
        18: 3510, 19: 3953, 20: 4426,
    }),
    "lachelein": SymbolArea("lachelein", "레헬른", "arcane", 220, 20, 30, 10, {
        2: 145, 3: 183, 4: 246, 5: 334, 6: 450, 7: 592, 8: 762, 9: 960, 10: 1186,
        11: 1443, 12: 1729, 13: 2046, 14: 2394, 15: 2773, 16: 3186, 17: 3631,
        18: 4110, 19: 4623, 20: 5170,
    }),
    "arcana": SymbolArea("arcana", "아르카나", "arcane", 225, 20, 30, 10, {
        2: 169, 3: 213, 4: 286, 5: 388, 6: 522, 7: 686, 8: 882, 9: 1110, 10: 1370,
        11: 1665, 12: 1993, 13: 2356, 14: 2754, 15: 3187, 16: 3658, 17: 4165,
        18: 4710, 19: 5293, 20: 5914,
    }),
    "morass": SymbolArea("morass", "모라스", "arcane", 230, 20, 30, 10, {
        2: 193, 3: 243, 4: 326, 5: 442, 6: 594, 7: 780, 8: 1002, 9: 1260, 10: 1554,
        11: 1887, 12: 2257, 13: 2666, 14: 3114, 15: 3601, 16: 4130, 17: 4699,
        18: 5310, 19: 5963, 20: 6658,
    }),
    "esfera": SymbolArea("esfera", "에스페라", "arcane", 235, 20, 30, 10, {
        2: 217, 3: 273, 4: 366, 5: 496, 6: 666, 7: 874, 8: 1122, 9: 1410, 10: 1738,
        11: 2109, 12: 2521, 13: 2976, 14: 3474, 15: 4015, 16: 4602, 17: 5233,
        18: 5910, 19: 6633, 20: 7402,
    }),
    "cernium": SymbolArea("cernium", "세르니움", "authentic", 260, 11, 10, 10, {
        2: 3650, 3: 9120, 4: 16070, 5: 24190, 6: 33150, 7: 42620, 8: 52290,
        9: 61820, 10: 70900, 11: 79200,
    }),
    "arcus_island": SymbolArea("arcus_island", "아르크스", "authentic", 265, 11, 10, 10, {
        2: 4170, 3: 10480, 4: 18610, 5: 28220, 6: 39000, 7: 50610, 8: 62740,
        9: 75070, 10: 87260, 11: 99000,
    }),
    "odium": SymbolArea("odium", "오디움", "authentic", 270, 11, 10, 10, {
        2: 4690, 3: 11850, 4: 21150, 5: 32250, 6: 44850, 7: 58600, 8: 73200,
        9: 88320, 10: 103620, 11: 118800,
    }),
    "shangri_la": SymbolArea("shangri_la", "도원경", "authentic", 275, 11, 10, 10, {
        2: 5220, 3: 13220, 4: 23680, 5: 36280, 6: 50700, 7: 66600, 8: 83660,
        9: 101560, 10: 119980, 11: 138600,
    }),
    "arteria": SymbolArea("arteria", "아르테리아", "authentic", 280, 11, 10, 10, {
        2: 5740, 3: 14590, 4: 26220, 5: 40320, 6: 56550, 7: 74590, 8: 94120,
        9: 114810, 10: 136350, 11: 158400,
    }),
    "carcion": SymbolArea("carcion", "카르시온", "authentic", 285, 11, 10, 10, {
        2: 6260, 3: 15960, 4: 28760, 5: 44350, 6: 62400, 7: 82580, 8: 104580,
        9: 128060, 10: 152710, 11: 178200,
    }),
    "tallahart": SymbolArea("tallahart", "탈라하트", "grand_authentic", 290, 11, 10, 10, {
        2: 11360, 3: 29330, 4: 53580, 5: 83770, 6: 119600, 7: 160720, 8: 206830,
        9: 257600, 10: 312690, 11: 371800,
    }),
    "geardock": SymbolArea("geardock", "기어드락", "grand_authentic", 295, 11, 10, 10, {
        2: 13970, 3: 36170, 4: 66270, 5: 103930, 6: 148850, 7: 200680, 8: 259120,
        9: 323840, 10: 394500, 11: 470800,
    }),
}

ARCANE_GROUPS = {"arcane"}
AUTHENTIC_FORCE_GROUPS = {"authentic", "grand_authentic"}

AREA_ORDER = list(SYMBOL_AREAS)
NAME_TO_KEY_MAP = {area.name: key for key, area in SYMBOL_AREAS.items()}
KEY_TO_NAME_MAP = {key: area.name for key, area in SYMBOL_AREAS.items()}


def get_areas_for_mode(mode):
    groups = ARCANE_GROUPS if mode == "arcane" else AUTHENTIC_FORCE_GROUPS
    return [area for area in SYMBOL_AREAS.values() if area.group in groups]


def get_accessible_areas(character_level, mode):
    return [
        area.key
        for area in get_areas_for_mode(mode)
        if character_level >= area.required_level
    ]


def get_area_key_from_symbol_name(symbol_name):
    normalized = symbol_name.split(":", 1)[-1].strip()
    if normalized in NAME_TO_KEY_MAP:
        return NAME_TO_KEY_MAP[normalized]

    for name, key in NAME_TO_KEY_MAP.items():
        if name in symbol_name:
            return key
    return None


def get_area_group_label(area_key):
    group = SYMBOL_AREAS[area_key].group
    if group == "arcane":
        return "아케인"
    if group == "authentic":
        return "어센틱"
    return "그랜드 어센틱"
