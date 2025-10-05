import random

words = ["ROCKET", "BUNKER", "IGNORE", "EVACUATION"]
chosen_card = random.choice(words)

def get_scenario_params():
    speed_1, speed_2, speed_3, speed_4 = 10, 30, 50, 70
    distance_1, distance_2, distance_3, distance_4, distance_5 = 20, 1000, 4000, 100000000, 300000000
    weight_1, weight_2, weight_3, weight_4 = 1, 20000, 40000, 60000
    angle_1, angle_2, angle_3, angle_4 = 1, 30, 60, 90

    generated_scenario = random.randint(1, 360)

    block = ((generated_scenario - 1) // 120) + 1
    if block == 1:
        speed = random.randint(speed_1, speed_2)
    elif block == 2:
        speed = random.randint(speed_2 + 1, speed_3)
    else:  
        speed = random.randint(speed_3 + 1, speed_4)
    
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
        distance = random.randint(distance_1, distance_2)
    elif 10 <= local24 <= 18:
        distance = random.randint(distance_2 + 1, distance_3)
    else: 
        distance = random.randint(distance_4, distance_5)
    
    if 1 <= local120 <= 40:
        weight = random.randint(weight_1, weight_2)
    elif 41 <= local120 <= 80:
        weight = random.randint(weight_2 + 1, weight_3)
    else:  
        weight = random.randint(weight_3 + 1, weight_4)
    
    local3 = generated_scenario % 3
    if local3 == 1:
        angle = random.randint(angle_1, angle_2)
    elif local3 == 2:
        angle = random.randint(angle_2 + 1, angle_3)
    else: 
        angle = random.randint(angle_3 + 1, angle_4)
    
    return {
        "speed": speed,
        "composition": composition,
        "distance": distance,
        "weight": weight,
        "angle": angle,
        "generated_scenario": generated_scenario
    }

def validate_card_choice(generated_scenario, chosen_card):
    valid_cards = ["IGNORE", "EVACUATION", "BUNKER", "ROCKET"]
    if chosen_card not in valid_cards:
        raise ValueError(f"Невірна карта: {chosen_card}. Очікується одна з {valid_cards}")

    ignore_scenarios = {
        1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 19, 20, 21, 25, 26, 27, 28, 29, 30, 34, 35, 36, 37, 38, 39, 43, 44, 45, 49, 50, 51, 52, 58, 59, 60, 61, 73, 74, 75, 76, 82, 83, 84, 85, 97, 98, 99, 100, 106, 107, 108, 109, 121, 122, 123, 124, 130, 131, 132, 133, 145, 146, 147, 148, 154, 155, 156, 157, 169, 170, 171, 172, 178, 179, 180, 181, 193, 194, 195, 196, 202, 203, 204, 205
    }

    evacuation_scenarios = {
        22, 23, 24, 46, 47, 48, 67, 68, 69, 70, 71, 72, 91, 92, 93, 94, 95, 96, 115, 116, 117, 118, 119, 120, 139, 140, 141, 142, 143, 144, 163, 164, 165, 166, 167, 168, 187, 188, 189, 190, 191, 192, 211, 212, 213, 214, 215, 216, 235, 236, 237, 238, 239, 240, 259, 260, 261, 262, 263, 264, 283, 284, 285, 286, 287, 288, 307, 308, 309, 310, 311, 312, 331, 332, 333, 334, 335, 336, 355, 356, 357, 358, 359, 360
    }

    bunker_scenarios = {
        7, 8, 9, 16, 17, 18, 31, 32, 33, 40, 41, 42, 53, 54, 55, 56, 57, 62, 63, 64, 65, 66, 77, 78, 86, 87, 88, 89, 90, 101, 102, 110, 111, 112, 113, 114, 136, 137, 138, 160, 161, 162, 184, 185, 186, 208, 209, 210, 220, 221, 229, 230, 232, 233, 234, 244, 245, 253, 254, 256, 257, 258, 268, 269, 277, 278, 280, 281, 282, 292, 293, 301, 302, 304, 305, 306, 316, 317, 325, 326, 328, 329, 330, 340, 341, 349, 350, 352, 353, 354
    }

    rocket_scenarios = {
        79, 80, 81, 103, 104, 105, 125, 126, 127, 128, 129, 134, 135, 149, 150, 151, 152, 153, 158, 159, 173, 174, 175, 176, 177, 182, 183, 197, 198, 199, 200, 201, 206, 207, 217, 218, 219, 222, 223, 224, 225, 226, 227, 228, 231, 241, 242, 243, 246, 247, 248, 249, 250, 251, 252, 255, 265, 266, 267, 270, 271, 272, 273, 274, 275, 276, 279, 289, 290, 291, 294, 295, 296, 297, 298, 299, 300, 303, 313, 314, 315, 318, 319, 320, 321, 322, 323, 324, 327, 337, 338, 339, 342, 343, 344, 345, 346, 347, 348, 351
    }
    
    return {
        "is_correct": chosen_card == "IGNORE" and generated_scenario in ignore_scenarios or
                      chosen_card == "EVACUATION" and generated_scenario in evacuation_scenarios or
                      chosen_card == "BUNKER" and generated_scenario in bunker_scenarios or
                      chosen_card == "ROCKET" and generated_scenario in rocket_scenarios,
        "correct_card": "IGNORE" if generated_scenario in ignore_scenarios else
                       "EVACUATION" if generated_scenario in evacuation_scenarios else
                       "BUNKER" if generated_scenario in bunker_scenarios else
                       "ROCKET"
    }

result_params = get_scenario_params()
print("Параметри сценарію:")
print(f"Швидкість: {result_params['speed']} км/с")
print(f"Склад: {result_params['composition']}")
print(f"Відстань: {result_params['distance']} км")
print(f"Вага: {result_params['weight']} кг")
print(f"Кут: {result_params['angle']}°")
print(f"Номер сценарію: {result_params['generated_scenario']}")

validation_result = validate_card_choice(result_params["generated_scenario"], chosen_card)
is_correct = validation_result["is_correct"]
correct_card = validation_result["correct_card"]

print(f"\nВи обрали карту '{chosen_card}'")
if is_correct:
    print("Ваш вибір правильний!")
else:
    print(f"Ваш вибір невірний. Правильна карта: '{correct_card}'")