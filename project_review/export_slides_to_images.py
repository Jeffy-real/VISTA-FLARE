import os
import sys
from pathlib import Path

def export_slides():
    pptx_path = Path("project_review/Vista_Flare_Deep_Learning_Project_Review_2.pptx").resolve()
    output_dir = Path("project_review/slides_png").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Opening {pptx_path} with PowerPoint COM...")
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        # Open invisible/minimized if possible
        deck = powerpoint.Presentations.Open(str(pptx_path), WithWindow=False)
        print(f"Presentation opened. Total slides: {deck.Slides.Count}")

        for i, slide in enumerate(deck.Slides, start=1):
            out_file = output_dir / f"slide_{i:02d}.png"
            # Export(Path, FilterName, ScaleWidth, ScaleHeight)
            # 1920x1080 for HD review
            slide.Export(str(out_file), "PNG", 1920, 1080)
            print(f"Exported Slide {i:02d} -> {out_file.name}")

        deck.Close()
        powerpoint.Quit()
        pythoncom.CoUninitialize()
        print(f"Successfully exported all {deck.Slides.Count} slides to {output_dir}")
        return True
    except Exception as exc:
        print("PowerPoint COM export error:", exc)
        return False

if __name__ == "__main__":
    export_slides()

