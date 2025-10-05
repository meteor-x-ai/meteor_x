def in_ranges(val, ranges_list):
    for start, end in ranges_list:
        if start <= val <= end:
            return True
    return False

group1_ranges = [
    (1,3), (10,12), (25,27), (34,36), (49,51), (58,60),
    (73,75), (82,84), (97,99), (106,108), (121,123), (130,132),
    (145,147), (154,156), (169,171), (178,180), (193,195), (202,204),
    (217,219), (226,228), (241,243), (250,252), (265,267), (274,276),
    (289,291), (298,300), (313,315), (322,324), (337,339), (346,348)
]
group2_ranges = [
    (4,6), (13,15), (19,21), (28,30), (37,39), (43,45),
    (52,54), (61,63), (67,69), (76,78), (85,87), (91,93),
    (100,102), (109,111), (115,117), (124,126), (133,135), (139,141),
    (148,150), (157,159), (163,165), (172,174), (181,183), (187,189),
    (196,198), (205,207), (211,213), (220,222), (229,231), (235,237),
    (244,246), (253,255), (259,261), (268,270), (277,279), (283,285),
    (292,294), (301,303), (307,309), (316,318), (325,327), (331,333),
    (340,342), (349,351), (355,357)
]
group3_ranges = [
    (7,9), (16,18), (22,24), (31,33), (40,42), (46,48),
    (55,57), (64,66), (70,72), (79,81), (88,90), (94,96),
    (103,105), (112,114), (118,120), (127,129), (136,138), (142,144),
    (151,153), (160,162), (166,168), (175,177), (184,186), (190,192),
    (199,201), (208,210), (214,216), (223,225), (232,234), (238,240),
    (247,249), (256,258), (262,264), (271,273), (280,282), (286,288),
    (295,297), (304,306), (310,312), (319,321), (328,330), (334,336),
    (343,345), (352,354), (358,360)
]

with open('def_4_scenarios.csv', 'w') as f:
    f.write("generated_scenario;speed (km/s);composition;distance (km);weight (g);angle (degrees)\n")
    
    counter = 1
    for generated_scenario in range(1, 361):
        block = ((generated_scenario - 1) // 120) + 1
        if block == 1:
            lower_speed = 10
            upper_speed = 30
        elif block == 2:
            lower_speed = 31
            upper_speed = 50
        else:
            lower_speed = 51
            upper_speed = 70
        speeds = [lower_speed]

        local120 = ((generated_scenario - 1) % 120) + 1
        if 1 <= local120 <= 24:
            composition = "ICE"
        elif 25 <= local120 <= 48:
            composition = "ICE_STONE"
        elif 49 <= local120 <= 72:
            composition = "STONE"
        elif 73 <= local120 <= 96:
            composition = "STONE_IRON"
        else:
            composition = "IRON"

        local24 = ((generated_scenario - 1) % 24) + 1
        if 1 <= local24 <= 9:
            lower_dist = 20
            upper_dist = 1000
        elif 10 <= local24 <= 18:
            lower_dist = 1001
            upper_dist = 4000
        else:
            lower_dist = 100000000
            upper_dist = 300000000
        mid_dist = (lower_dist + upper_dist) // 2
        dists = [lower_dist, mid_dist, upper_dist]

        if in_ranges(generated_scenario, group1_ranges):
            lower_weight = 1
            upper_weight = 20000
        elif in_ranges(generated_scenario, group2_ranges):
            lower_weight = 20001
            upper_weight = 40000
        else:
            lower_weight = 40001
            upper_weight = 60000
        mid_weight = (lower_weight + upper_weight) // 2
        weights = [lower_weight, mid_weight, upper_weight]

        local3 = generated_scenario % 3
        if local3 == 0:  
            local3 = 3
        if local3 == 1:
            lower_angle = 1
            upper_angle = 30
        elif local3 == 2:
            lower_angle = 31
            upper_angle = 60
        else:
            lower_angle = 61
            upper_angle = 90
        mid_angle = (lower_angle + upper_angle) // 2
        angles = [lower_angle, mid_angle, upper_angle]

        for s_val in speeds:
            for d_val in dists:
                for w_val in weights:
                    for a_val in angles:
                        f.write(f"{counter};{s_val};{composition};{d_val};{w_val};{a_val}\n")
                        counter += 1

print("CSV файл 'def_4_scenarios.csv' згенеровано! Всього записів:", counter - 1)