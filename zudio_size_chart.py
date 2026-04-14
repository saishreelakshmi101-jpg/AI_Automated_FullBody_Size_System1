# zudio_size_chart.py
# small helper to create or print the zudio sizes csv (sample values)
import pandas as pd

def create_sample_csv(path='zudio_sizes.csv'):
    data = [
        {'Size':'S','Chest_cm':86,'Waist_cm':76,'Hip_cm':88,'Shoulder_cm':42,'HeightMin_cm':155,'HeightMax_cm':165},
        {'Size':'M','Chest_cm':96,'Waist_cm':82,'Hip_cm':96,'Shoulder_cm':44,'HeightMin_cm':165,'HeightMax_cm':175},
        {'Size':'L','Chest_cm':102,'Waist_cm':90,'Hip_cm':102,'Shoulder_cm':46,'HeightMin_cm':175,'HeightMax_cm':183},
        {'Size':'XL','Chest_cm':108,'Waist_cm':96,'Hip_cm':108,'Shoulder_cm':48,'HeightMin_cm':183,'HeightMax_cm':190},
        {'Size':'XXL','Chest_cm':114,'Waist_cm':102,'Hip_cm':114,'Shoulder_cm':50,'HeightMin_cm':188,'HeightMax_cm':195},
    ]
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    print(f"Sample Zudio CSV saved to {path}")
