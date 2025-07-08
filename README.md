Input your units stats and get the DPS calculations :D (code not made by me, i am dumb in code, it was all made by chatgpt)
https://www.virustotal.com/gui/file/d18aa2bab026084ef659a06e36850aa855fe986ebaa8f67ed8a90277b1c58322/detection (8 false positives, but if you are really concerned that this contains virus, I have uploaded the .py file for you to download and you may look through the source code and run that file)

To use the .py file instead of the exe, download [Python](https://www.python.org/downloads/), open a command prompt within the directory that you have downloaded it in and then run the command "python astdx_dps_calculator.py"

Cons:
- You must know the unit's max upgrade DMG/RNG/SPD, I highly suggest you use the [DPS Sheet for this](https://docs.google.com/spreadsheets/d/1kvBkC8vM9Nn2RprL37sz_ANf4b4hAeH6JisewHw11oM/htmlview?gid=0#gid=0)
- Fire may not be accurate as I copied over the Bleed DoT description and math to fire, so take that with a grain of salt (I don't know what fire does)
- Time simulations are not included in this, meaning effects over time (such as marking or again DoT) are not included within the overall DPS calculation, but they will be included as if they have all occured 
- Commas don't work. (for example: don't type 15,000 or else you won't get your calculation)

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
