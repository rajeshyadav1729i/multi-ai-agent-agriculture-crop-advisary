import os
import re
from pathlib import Path
from typing import List, Dict, Any
from app.config import settings

class DocumentChunk:
    def __init__(self, scheme_id: str, title: str, section: str, content: str, source: str, portal: str):
        self.scheme_id = scheme_id
        self.title = title
        self.section = section
        self.content = content
        self.source = source
        self.portal = portal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scheme_id": self.scheme_id,
            "title": self.title,
            "section": self.section,
            "content": self.content,
            "source": self.source,
            "portal": self.portal
        }

def load_scheme_documents(kb_dir: Optional[Path] = None) -> List[DocumentChunk]:
    if kb_dir is None:
        kb_dir = settings.KNOWLEDGE_BASE_DIR
        
    chunks: List[DocumentChunk] = []
    if not os.path.exists(kb_dir):
        return chunks

    for file_name in os.listdir(kb_dir):
        if not (file_name.endswith(".txt") or file_name.endswith(".md")):
            continue
            
        file_path = os.path.join(kb_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        scheme_id = file_name.replace(".txt", "").replace(".md", "")
        
        # Parse title and portal from document header
        title_match = re.search(r"#\s*SCHEME REFERENCE:\s*(.+)", text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else scheme_id.replace("_", " ")
        
        portal_match = re.search(r"Official Portal:\s*(https?://[^\s\n]+)", text, re.IGNORECASE)
        portal = portal_match.group(1).strip() if portal_match else "https://agricoop.nic.in"
        
        source_match = re.search(r"(MINISTRY OF [^\n]+|GOVERNMENT OF [^\n]+)", text, re.IGNORECASE)
        source = source_match.group(1).strip() if source_match else "Government of India - Department of Agriculture"

        # Break into sections based on numbered headers (1. OBJECTIVE, 2. BENEFITS, etc.)
        sections = re.split(r"\n(?=\d+\.\s+[A-Z\s/&]+:)", text)
        
        for sec in sections:
            sec_clean = sec.strip()
            if not sec_clean:
                continue
                
            sec_header_match = re.match(r"(\d+\.\s+[A-Z\s/&]+):", sec_clean)
            sec_title = sec_header_match.group(1).strip() if sec_header_match else "Overview"
            
            chunk = DocumentChunk(
                scheme_id=scheme_id,
                title=title,
                section=sec_title,
                content=sec_clean,
                source=source,
                portal=portal
            )
            chunks.append(chunk)

    return chunks
