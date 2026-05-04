import argparse
import base64
import csv
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Mapping features to their URLs
FEATURES = {
    "Document Conversion (Image to PDF)": "https://www.pixelssuite.com/image-to-pdf",
    "Image Resizing": "https://www.pixelssuite.com/resize-image",
    "Cropping": "https://www.pixelssuite.com/crop-image",
    "Compression": "https://www.pixelssuite.com/compress-image",
    "Image Format Conversion (to PNG)": "https://www.pixelssuite.com/convert-to-png",
    "Meme Generation": "https://www.pixelssuite.com/meme-generator",
    "Color Picker": "https://www.pixelssuite.com/color-picker",
    "Image Rotation": "https://www.pixelssuite.com/rotate-image",
    "Image Flipping": "https://www.pixelssuite.com/flip-image",
    "PDF Editing": "https://www.pixelssuite.com/edit-pdf"
}

def check_preview_visible(page):
    script = """
    () => {
        const visible = (el) => !!(el && el.getClientRects && el.getClientRects().length);
        const previewLabels = Array.from(document.querySelectorAll("body *"))
            .filter(el => el.childElementCount === 0)
            .filter(el => (el.textContent || "").trim().toLowerCase().includes("preview"))
            .filter(el => visible(el));

        for (const label of previewLabels) {
            let parent = label;
            for (let i = 0; i < 6 && parent; i++) {
                const media = Array.from(parent.querySelectorAll("img, canvas, svg, video"))
                    .filter(el => visible(el));
                if (media.length > 0) return true;
                parent = parent.parentElement;
            }
        }
        return false;
    }
    """
    return page.evaluate(script)

def save_individual_csv(feature_name, result):
    safe_name = feature_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    csv_path = Path(f"execution_results_{safe_name}.csv")
    fieldnames = ["feature", "url", "input_used", "expected_output", "actual_output", "status", "screenshot"]
    
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            "feature": feature_name,
            "url": result["url"],
            "input_used": "sample.png",
            "expected_output": "The uploaded file should be displayed in the preview section.",
            "actual_output": "The preview was detected." if result["preview_detected"] else "No preview was detected.",
            "status": result["status"],
            "screenshot": result["screenshot"]
        })

def run_all_tests():
    png_path = Path("sample.png").resolve()
    out_dir = Path("all_results").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    master_csv_path = Path("all_automated_execution_results.csv")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for feature_name, url in FEATURES.items():
            print(f"Testing: {feature_name} at {url}")
            page = context.new_page()
            
            status = "FAIL"
            screenshot_path = ""
            preview_found = False

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(3)

                # Try to find file input
                file_input = page.locator('input[type="file"]').first
                if file_input.count() > 0:
                    file_input.set_input_files(str(png_path))
                    
                    # Wait for preview (max 15s)
                    for _ in range(30):
                        if check_preview_visible(page):
                            preview_found = True
                            break
                        time.sleep(0.5)

                status = "PASS" if preview_found else "FAIL"
                
                # Sanitize filename
                safe_name = feature_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
                screenshot_path = out_dir / f"{safe_name}_{status.lower()}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)

            except Exception as e:
                print(f"Error testing {feature_name}: {e}")
                status = "ERROR"
            
            res_obj = {
                "feature": feature_name,
                "url": url,
                "input_used": "sample.png",
                "expected_output": "The uploaded file should be displayed in the preview section.",
                "actual_output": "The preview was detected." if preview_found else "No preview was detected.",
                "preview_detected": preview_found,
                "status": status,
                "screenshot": str(screenshot_path.relative_to(Path.cwd())) if screenshot_path else ""
            }
            results.append(res_obj)
            save_individual_csv(feature_name, res_obj)
            page.close()

        browser.close()

    # Write to Master CSV
    with master_csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["feature", "url", "input_used", "expected_output", "actual_output", "status", "screenshot"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "feature": r["feature"],
                "url": r["url"],
                "input_used": r["input_used"],
                "expected_output": r["expected_output"],
                "actual_output": r["actual_output"],
                "status": r["status"],
                "screenshot": r["screenshot"]
            })

    print(f"\nAll tests completed. Results saved to {master_csv_path} and individual CSVs.")

if __name__ == "__main__":
    run_all_tests()
