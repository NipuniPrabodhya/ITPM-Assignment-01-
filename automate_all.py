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

def run_all_tests():
    png_path = Path("sample.png").resolve()
    out_dir = Path("all_results").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = Path("all_automated_execution_results.csv")

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
                time.sleep(2) # Give it a moment to render

                # Try to find file input
                file_input = page.locator('input[type="file"]').first
                if file_input.count() > 0:
                    file_input.set_input_files(str(png_path))
                    
                    # Wait for preview (max 10s)
                    for _ in range(20):
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
            
            results.append({
                "feature": feature_name,
                "url": url,
                "preview_detected": preview_found,
                "status": status,
                "screenshot": str(screenshot_path.relative_to(Path.cwd())) if screenshot_path else ""
            })
            page.close()

        browser.close()

    # Write to CSV
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["feature", "url", "preview_detected", "status", "screenshot"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nAll tests completed. Results saved to {csv_path}")

if __name__ == "__main__":
    run_all_tests()
