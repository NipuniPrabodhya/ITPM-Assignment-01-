# IT3040 – ITPM Assignment 1: Option 2
## Functional and Usability Testing of PixelsSuite

### Overview
This project contains the automated and manual test artifacts for the functional and usability testing of [PixelsSuite](https://www.pixelssuite.com/).

### Project Structure
- `image_preview_test.py`: Playwright script to automate the preview functionality test.
- `execution_results.csv`: Results of the automated test execution.
- `Manual Test Cases for Option 2.xlsx`: Excel file containing 35 manual test scenarios (36 total including the automated one).
- `results/`: Directory containing screenshots of the automated test execution.
- `sample.png`: Sample image used for the automated test.
- `generate_excel.py`: Utility script used to generate the manual test cases.

### Prerequisites
- Python 3.11 or 3.12
- Google Chrome browser (or Chromium installed via Playwright)

### Installation
1. Clone the repository or extract the project folder.
2. Navigate to the project directory:
   ```bash
   cd test_automation_ui
   ```
3. Install the required dependencies:
   ```bash
   pip install -U pip
   pip install playwright openpyxl
   playwright install
   ```

### Running the Automated Test
To run the automated preview functionality test for the "Image format conversion" feature:
```bash
python image_preview_test.py --url "https://www.pixelssuite.com/convert-to-png" --slow-mo-ms 2000
```
The script will:
1. Navigate to the specified URL.
2. Upload the `sample.png` file.
3. Verify if the preview is displayed.
4. Save a screenshot in the `results/` folder.
5. Record the result in `execution_results.csv`.

### Master Automation (Advanced)
A master script `automate_all.py` is included that automates all 10 features mentioned in the assignment.
To run the full suite:
```bash
python automate_all.py
```
This will generate `all_automated_execution_results.csv` and store all screenshots in the `all_results/` folder.

### Manual Test Cases
The `Manual Test Cases for Option 2.xlsx` file contains 50 scenarios covering 10 features.
1. Document conversion
2. PDF editing
3. Image resizing
4. Cropping
5. Compression
6. Image format conversion
7. Meme generation
8. Color picker
9. Image rotation
10. Image flipping

Each feature includes at least one positive and two negative test cases.

### Git Repository
Public repository link: https://github.com/NipuniPrabodhya/ITPM-Assignment-01-
*(Note: Ensure the repository is publicly accessible as per assignment requirements.)*
