"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng pdfminer.six để convert PDF.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.
"""

from pathlib import Path
import json
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def extract_pdf_text_pdfminer(pdf_path):
    """Extract text from PDF using pdfminer.six."""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(str(pdf_path))
        return text if text else ""
    except Exception as e:
        return f"[Error extracting PDF with pdfminer: {e}]"


def extract_pdf_text_pymupdf(pdf_path):
    """Extract text from PDF using PyMuPDF."""
    try:
        import pymupdf
        doc = pymupdf.open(str(pdf_path))
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text if text else ""
    except Exception as e:
        return f"[Error extracting PDF with pymupdf: {e}]"


def extract_pdf_text(pdf_path):
    """Try multiple methods to extract text from PDF."""
    # Try pdfminer.six first
    text = extract_pdf_text_pdfminer(pdf_path)
    if text and len(text.strip()) > 100:
        return text
    
    # Try PyMuPDF as fallback
    text = extract_pdf_text_pymupdf(pdf_path)
    if text and len(text.strip()) > 100:
        return text
    
    return text if text else ""


def convert_legal_docs() -> int:
    """Convert PDF/DOCX vào standardized/legal."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
            try:
                print(f"  Converting: {path.name}")
                content = ""
                
                if path.suffix.lower() == ".pdf":
                    content = extract_pdf_text(path)
                
                content = content.strip()
                if content and len(content) > 100:
                    output_path = output_dir / f"{path.stem}.md"
                    output_path.write_text(content, encoding="utf-8")
                    count += 1
                    print(f"    -> Saved: {output_path.name} ({len(content)} chars)")
                else:
                    print(f"    -> Warning: Empty or too short content ({len(content)} chars), skipped")
            except Exception as e:
                print(f"    -> Error: {e}")
    
    print(f"  Converted {count} legal documents")
    return count


def convert_news_articles() -> int:
    """Convert JSON vào standardized/news."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for path in sorted(news_dir.glob("*.json")):
        try:
            print(f"  Converting: {path.name}")
            data = json.loads(path.read_text(encoding="utf-8"))
            
            # Create header with metadata
            header = (
                f"# {data.get('title', 'Untitled')}\n\n"
                f"**Source:** {data.get('url', 'N/A')}\n\n"
                f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n"
                f"---\n\n"
            )
            
            content = data.get("content_markdown", "").strip()
            if content:
                output_path = output_dir / f"{path.stem}.md"
                output_path.write_text(header + content, encoding="utf-8")
                count += 1
                print(f"    -> Saved: {output_path.name} ({len(content)} chars)")
            else:
                print(f"    -> Warning: Empty content, skipped")
        except Exception as e:
            print(f"    -> Error: {e}")
    
    print(f"  Converted {count} news articles")
    return count


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("\n=== Task 3: Chuẩn hóa Markdown ===\n")
    print("Converting legal documents...")
    legal_count = convert_legal_docs()
    print("\nConverting news articles...")
    news_count = convert_news_articles()
    print(f"\n✓ Hoàn thành! Đã convert {legal_count} legal + {news_count} news = {legal_count + news_count} files")
    print(f"  Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
