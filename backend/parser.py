import re
import io
import fitz  # PyMuPDF  # type: ignore
import docx  # python-docx
from typing import Dict, List


def extract_text_from_file(filename: str, data: bytes) -> str:
    """
    Extracts text from uploaded files (PDF, DOCX, TXT).
    """
    text = ""
    low_filename = filename.lower()

    try:
        if low_filename.endswith(".pdf"):
            # --- START FIX ---
            # Use PyMuPDF to get text, preserving layout structure better
            with fitz.open(stream=data, filetype="pdf") as pdf_doc:
                for page in pdf_doc:
                    # 'text' block mode preserves paragraphs better
                    text += page.get_text("text") 
            # --- END FIX ---
        elif low_filename.endswith(".docx"):
            with io.BytesIO(data) as stream:
                doc = docx.Document(stream)
                text = "\n".join(para.text for para in doc.paragraphs)
        else:
            text = data.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Parsing error for {filename}: {e}")
        try:
            text = data.decode("latin-1", errors="ignore")
        except Exception:
            text = ""

    return text.strip()


def extract_contacts(text: str) -> Dict[str, str]:
    """
    Extract name, email, phone, LinkedIn, and address info.
    """
    contacts = {
        "name": "",
        "email": "",
        "phone": "",
        "links": "",
        "address": ""
    }
    
    # --- START FIX: Improve Name detection ---
    # Look for the first few lines that are not all caps and look like a name
    for line in text.strip().split("\n")[:3]:
        line = line.strip()
        if re.search(r'\d|@|http|:|Profile|Contact', line, re.I):
            continue
        if len(line.split()) > 1 and len(line.split()) < 5:
            contacts["name"] = line.strip().title()
            break
    # Fallback if still no name
    if not contacts["name"]:
        first_line = text.strip().split("\n")[0]
        if len(first_line.split()) <= 4 and not re.search(r'\d|@', first_line):
            contacts["name"] = first_line.strip().title()
    # --- END FIX ---

    # Email
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if email_match:
        contacts["email"] = email_match.group()

    phone_match = re.search(r"([\+\[\(\s]?\d[\d\s\-\.\]\(\)]{8,18}\d)", text)
    if phone_match:
        contacts["phone"] = phone_match.group(1).strip()
    # --- END PHONE NUMBER FIX ---

    # LinkedIn or portfolio links
    link_match = re.findall(r"(https?://[^\s]+)", text)
    if link_match:
        contacts["links"] = ", ".join([l for l in link_match if "linkedin" in l or "github" in l])

    # Address (optional heuristic)
    addr_match = re.search(r"(Address|House|Road|Dhaka|Bangladesh|City):?\s*([A-Za-z0-9,.\-\s]+)", text)
    if addr_match:
        contacts["address"] = addr_match.group(0)

    return contacts


def split_sections(text: str) -> Dict[str, str]:
    """
    Extracts resume sections (summary, skills, experience, education, information).
    """
    if not text:
        return {}

    # --- START MODIFICATION ---
    # Keep newlines, just reduce multiple spaces to one
    text = re.sub(r"[ \t]+", " ", text)
    # --- END MODIFICATION ---

    # Extract contact info
    contacts = extract_contacts(text)

    sections = {
        "contacts": contacts,
        "summary": "",
        "skills": "",
        "experience": "",
        "education": ""
    }

    # --- START MODIFICATION ---
    # --- Make pattern more robust to capture all key sections ---
    # Added: profile, projects, technical skills, soft skills, languages, contact
    pattern_str = r"(?im)^[\s\-\*]*(summary|profile|skills|technical skills|soft skills|spoken languages|experience|work experience|professional experience|projects|education|contact)[\s:\-]*"
    pattern = re.compile(pattern_str)
    matches = list(pattern.finditer(text))
    
    if matches:
        # --- Capture the text BEFORE the first match as summary ---
        first_match_start = matches[0].start()
        summary_text = text[:first_match_start].strip()
        
        # Clean up summary text (remove contact info that's already parsed)
        if contacts.get("name"):
            summary_text = summary_text.replace(contacts["name"], "")
        if contacts.get("email"):
            summary_text = summary_text.replace(contacts["email"], "")
        if contacts.get("phone"):
            summary_text = summary_text.replace(contacts["phone"], "")

        # Remove titles that might be mixed in
        summary_text = re.sub(r"Computer Science & Engineering Undergraduate", "", summary_text, flags=re.I)
        
        sections["summary"] = " ".join(summary_text.split()) # Re-normalize whitespace

        for i, m in enumerate(matches):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            section_text = text[start:end].strip()
            
            # Clean section text by removing other headers that might be inside
            section_text = pattern.split(section_text)[0]
            
            key = m.group(1).lower()

            # Map variations to standard keys
            if key in ["profile"]:
                key = "summary"
            elif key in ["technical skills", "soft skills", "spoken languages"]:
                key = "skills"
            elif key in ["work experience", "professional experience", "projects"]:
                key = "experience"
            elif key in ["contact"]:
                continue # We already parsed contacts

            sections[key] += section_text + "\n" # Append text
    
    else:
        # --- Heuristic fallback (unchanged, but less likely to be used) ---
        sentences = re.split(r'(?<=[.!?])\s+', text)

        skill_keywords = [
            "skill", "tools", "technologies", "proficient", "languages",
            "frameworks", "expertise", "experienced in", "familiar with",
            "python", "java", "sql", "react", "aws", "gcp", "azure", "docker"
        ]
        edu_keywords = [
            "university", "college", "bachelor", "master", "degree", "b.s.", "m.s.",
            "diploma", "education", "institute", "school", "ph.d."
        ]
        exp_keywords = [
            "experience", "worked", "developed", "managed", "responsible",
            "intern", "position", "role", "company", "organization", "project"
        ]

        skills_sent, edu_sent, exp_sent, summary_sent = [], [], [], []

        for sent in sentences:
            low = sent.lower()
            if any(k in low for k in edu_keywords):
                edu_sent.append(sent)
            elif any(k in low for k in exp_keywords):
                exp_sent.append(sent)
            elif any(k in low for k in skill_keywords):
                skills_sent.append(sent)
            else:
                summary_sent.append(sent)

        sections["skills"] = " ".join(skills_sent).strip()
        sections["education"] = " ".join(edu_sent).strip()
        sections["experience"] = " ".join(exp_sent).strip()
        
        # Don't overwrite summary if it's already populated
        if not sections["summary"]:
             sections["summary"] = " ".join(summary_sent[:3]).strip()
    
    # --- END MODIFICATION ---

    # Cleanup
    for k in sections:
        if k == "contacts":
            continue
        sections[k] = re.sub(r"\s{2,}", " ", sections[k]).strip()

    return sections

# ... (rest of the file is unchanged) ...

def format_education_summary(text: str) -> str:
    """
    Formats education text as bullet points.
    """
    if not text:
        return ""

    entries = []
    edu_lines = re.split(r'(?i)(?:,|;|\.|\n)', text)
    for line in edu_lines:
        if re.search(r"(university|college|institute|school)", line, re.I):
            degree_match = re.search(r"(B\.?Sc\.?|M\.?Sc\.?|Bachelor|Master|Diploma|HSC|SSC)", line, re.I)
            year_match = re.search(r"\b(19|20)\d{2}\b", line)
            degree = degree_match.group(1) if degree_match else ""
            year = year_match.group(0) if year_match else ""
            entry = f"• {degree.strip()} — {line.strip()}"
            if year:
                entry += f" ({year})"
            entries.append(entry)
    return "\n".join(entries) if entries else text.strip()


def format_skills_list(text: str) -> str:
    """
    Converts skills text into bullet keyword style.
    """
    if not text:
        return ""
    # Remove emails/phones accidentally captured
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "", text)
    text = re.sub(r"\+?\d[\d\s\-]{7,}", "", text)

    parts = re.split(r"[,;•\n]", text)
    keywords = []
    for p in parts:
        word = p.strip()
        if 1 < len(word) < 30 and not any(c.isdigit() for c in word):
            keywords.append(f"• {word}")
    return "\n".join(sorted(set(keywords)))


def format_experience_points(text: str) -> str:
    """
    Converts experience text into short bullet points.
    """
    if not text:
        return ""
    points = re.split(r'(?<=[.!?])\s+', text)
    clean_points = []
    for p in points:
        p = p.strip()
        if len(p.split()) > 3 and len(p) < 200:
            clean_points.append(f"• {p}")
    return "\n".join(clean_points[:6])