import json
import os
from typing import Dict, List, Any

class MeteorMatcher:
    WEIGHTS = {'mass': 0.3, 'speed': 0.2, 'diameter': 0.25, 'angle': 0.15, 'year': 0.1}
    BONUSES = {'material': 0.1, 'type': 0.1, 'weather': 0.05}
    
    def __init__(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'meteors.json')
        self.meteors_data = self._load_data(data_path)
        self._precompute_ranges()
    
    def _load_data(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading meteors data: {e}")
            return []
    
    def _precompute_ranges(self):
        if not self.meteors_data:
            return
        self.ranges = {}
        for key in self.WEIGHTS.keys():
            values = [m[key] for m in self.meteors_data]
            self.ranges[key] = (min(values), max(values))
    
    def _normalize(self, value: float, key: str) -> float:
        min_val, max_val = self.ranges[key]
        return 0.0 if max_val == min_val else (value - min_val) / (max_val - min_val)
    
    def _calculate_similarity(self, input_params: Dict[str, Any], meteor: Dict[str, Any]) -> float:
        total_diff = sum(
            abs(self._normalize(input_params.get(key, 0), key) - self._normalize(meteor[key], key)) * weight
            for key, weight in self.WEIGHTS.items()
        )
        
        bonuses = sum(
            bonus for key, bonus in self.BONUSES.items()
            if input_params.get(key, '').upper() == meteor.get(key, '').upper()
        )
        
        return max(0, 1 - total_diff + bonuses)
    
    def find_closest_meteor(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.meteors_data:
            return {"error": "No meteors data available"}
        
        self._print_search_params(input_params)
        
        best_meteor, best_similarity = max(
            ((meteor, self._calculate_similarity(input_params, meteor)) for meteor in self.meteors_data),
            key=lambda x: x[1],
            default=(None, -1)
        )
        
        if best_meteor:
            self._print_result(best_meteor, best_similarity)
            result = best_meteor.copy()
            result['similarity_score'] = best_similarity
            return result
        
        return {"error": "No matching meteor found"}
    
    def _print_search_params(self, params: Dict[str, Any]):
        print(f"\nSearching for closest meteor:")
        for key, label in [('year', 'Year'), ('mass', 'Mass'), ('speed', 'Speed'), 
                          ('diameter', 'Diameter'), ('angle', 'Angle'), ('material', 'Material'), 
                          ('type', 'Type'), ('weather', 'Weather')]:
            value = params.get(key, 'N/A')
            unit = {'mass': ' kg', 'speed': ' m/s', 'diameter': ' m', 'angle': '°'}.get(key, '')
            print(f"   {label}: {value}{unit}")
        print(f"\nAnalyzing {len(self.meteors_data)} meteors...")
    
    def _print_result(self, meteor: Dict[str, Any], similarity: float):
        print(f"\nClosest meteor: {meteor['name']}")
        for key, label in [('year', 'Year'), ('mass', 'Mass'), ('speed', 'Speed'), 
                          ('diameter', 'Diameter'), ('angle', 'Angle'), ('material', 'Material'),
                          ('type', 'Type'), ('weather', 'Weather'), ('location', 'Location'),
                          ('craterDiameter', 'Crater Diameter')]:
            value = meteor[key]
            unit = {'mass': ' kg', 'speed': ' m/s', 'diameter': ' m', 'angle': '°', 'craterDiameter': ' m'}.get(key, '')
            print(f"   {label}: {value}{unit}")
        print(f"   Similarity: {similarity:.2%}")
        print(f"   Description: {meteor['description']}")

def main():
    matcher = MeteorMatcher()
    print("Meteor-X: Find closest matching meteor\n" + "=" * 40)
    
    try:
        params = {}
        inputs = [
            ("year", "Year (e.g., 2023)", int, 2023),
            ("mass", "Mass in kg (e.g., 1000000)", float, 1000000),
            ("speed", "Speed in m/s (e.g., 20000)", float, 20000),
            ("diameter", "Diameter in meters (e.g., 50)", float, 50),
            ("angle", "Impact angle in degrees (e.g., 45)", float, 45)
        ]
        
        print("\nEnter search parameters:")
        for key, prompt, cast_func, default in inputs:
            value = input(f"{prompt}: ").strip()
            params[key] = cast_func(value) if value else default
        
        choices = {
            'material': (["STONE", "IRON", "MIXED"], "material"),
            'type': (["STONY", "IRON", "STONY_IRON"], "type"),
            'weather': (["CLEAR", "RAIN", "SNOW", "STORM"], "weather")
        }
        
        for key, (options, label) in choices.items():
            print(f"\n{label.title()}:")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            choice = input(f"Select {label} (1-{len(options)}): ").strip()
            params[key] = options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(options) else options[0]
        
        result = matcher.find_closest_meteor(params)
        if 'error' in result:
            print(f"\nError: {result['error']}")
        else:
            print(f"\nResult found successfully!")
        
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
