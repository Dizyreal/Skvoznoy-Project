precipitation_mm = 12.0

precipitation_m = precipitation_mm / 1000
precipitation_mm_wrong = precipitation_m * 1000 * 1000

print(f"Wrong: {precipitation_mm_wrong} mm")

# precipitation_mm = 12.0

# precipitation_m = precipitation_mm / 1000
# precipitation_mm_back = precipitation_m * 1000

# assert abs(precipitation_mm_back - precipitation_mm) < 1e-9, "Unit conversion mismatch!"
# print(f"Correct: {precipitation_mm_back} mm")