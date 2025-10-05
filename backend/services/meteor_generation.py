#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "backend"))

def test_meteor_generation():
    try:
        from services.gemini_service import generate_random_meteor, is_valid_meteor
        
        print("Testing meteor generation")
        print("=" * 50)
        
        for i in range(3):
            print(f"\nGenerating meteor #{i+1}...")
            
            try:
                meteor = generate_random_meteor()
                
                print(f"Generated:")
                print(f"   Mass: {meteor['mass']} kg")
                print(f"   Speed: {meteor['speed']} m/s")
                print(f"   Angle: {meteor['angle']}°")
                print(f"   Location: {meteor['latitude']:.3f}, {meteor['longitude']:.3f}")
                print(f"   Type: {meteor['type']} ({meteor['material']})")
                print(f"   Weather: {meteor['weather']}")
                
                if is_valid_meteor(meteor):
                    print(f"   Valid data")
                else:
                    print(f"   Invalid data!")
                    
            except Exception as e:
                print(f"   Error: {e}")
        
        print("\n" + "=" * 50)
        print("Testing complete")
        
    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_meteor_generation()