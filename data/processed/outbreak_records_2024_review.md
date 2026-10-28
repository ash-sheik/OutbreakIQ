# Outbreak records 2024: data-quality review log

Source: `outbreak_records_2024_clean.csv`. This report records source values only. It does not change the source CSV. The seven date-conflict records were imported with both dates unchanged and the data-quality note: `Source reporting date precedes outbreak start date; both source dates were retained unchanged.`

## Reporting date before outbreak start date

| Unique ID | State | District | Disease | Cases | Deaths | Outbreak start | Reporting date | Source location |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| KL/MLP/2024/12/535 | Kerala | Malappuram | Hepatitis A | 254 | 0 | 2024-03-26 | 2024-03-25 | week 13, page 9, table 1 |
| HR/FTB/2024/20/935 | Haryana | Fatehabad | Chickenpox | 37 | 0 | 2024-05-18 | 2024-05-17 | week 20, page 11, table 1 |
| MH/SGL/2024/24/1220 | Maharashtra | Sangli | Dengue | 8 | 1 | 2024-06-12 | 2024-06-11 | week 24, page 20, table 1 |
| MH/SGL/2024/24/1221 | Maharashtra | Sangli | Food Poisoning | 20 | 0 | 2024-06-12 | 2024-06-11 | week 24, page 20, table 1 |
| OR/MBJ/2024/25/1293 | Odisha | Mayurbhanj | Acute Diarrheal Disease | 26 | 0 | 2024-06-20 | 2024-06-19 | week 25, page 17, table 1 |
| GJ/AHM/2024/28/1462 | Gujarat | Ahmadabad | Acute Diarrheal Disease | 27 | 0 | 2024-07-10 | 2024-07-09 | week 28, page 9, table 1 |
| MZ/AZL/2024/29/1615 | Mizoram | Aizawl | Food Poisoning | 38 | 0 | 2024-07-27 | 2024-07-20 | week 29, page 22, table 1 |

## Repeated source ID

`GJ/BKT/2024/29/1638` appears four times. The four records differ, so they must not be silently collapsed into one database record.

| Week | Page | District summary | Disease | Cases | Deaths | Outbreak start | Reporting date |
| ---: | ---: | --- | --- | ---: | ---: | --- | --- |
| 29 | 30 | Banaskantha | Acute Encephalitic Syndrome | 84 | 41 | 2024-07-09 | blank |
| 31 | 28 | Ahmedabad, AMC, Arvalli, Banaskanth, Bharuch, Bhavnagar, Chhotaudepur, Dahod, Devbhumi Dwarka, Gandhinagar, Gir Somnath, GMC, Jamnagar, JMC, Kheda, Kutch, Mahisagar, Mahesana, Morbi, Narmada, Panch Mahal, Patan, Porbandar, Rajkot, RMC, Sabar Kantha, SMC, Surendranagar, Vadodara, VMC | Acute Encephalitic Syndrome (Chandipura Virus) | 153 | 66 | 2024-07-09 | blank |
| 32 | 38 | Ahmedabad, AMC, Arvalli, Banaskanth, Bharuch, Bhavnagar, Chhotaudepur, Dahod, Devbhumi Dwarka, Gandhinagar, Gir Somnath, GMC, Jamnagar, JMC, Kheda, Kutch, Mahisagar, Mahesana, Morbi, Narmada, Panch Mahal, Patan, Porbandar, Rajkot, RMC, Sabar Kantha, SMC, Surendranagar, Vadodara, VMC | Acute Encephalitic Syndrome (Chandipura Virus) | 153 | 66 | 2024-07-09 | blank |
| 33 | 26 | Ahmedabad, AMC, Amreli, Arvalli, Banaskanth, Bharuch, Bhavnagar, Chhotaudepur, Dahod, Dang, Devbhumi Dwarka, Gandhinagar, Gir Somnath, GMC, Jamnagar, JMC, Kheda, Kutch, Mahisagar, Mahesana, Morbi, Narmada, Panch Mahal, Patan, Porbandar, Rajkot, RMC, Sabar Kantha, SMC, Surendranagar, Vadodara, VMC | Acute Encephalitic Syndrome (Chandipura Virus) | 164 | 73 | 2024-07-09 | blank |
