import json
import os
import re
from typing import List, Dict, Tuple
from html.parser import HTMLParser
from html import unescape

# Patterns to detect multi-choice questions
MULTI_CHOICE_PATTERNS = [
    r"\(Choose\s+TWO\)",
    r"\(Choose\s+two\)",
    r"\(Select\s+TWO\)",
    r"\(Select\s+two\)",
    r"\(Choose\s+\d+\)",
    r"\(Select\s+\d+\)",
    r"Choose\s+TWO",
    r"Select\s+TWO",
    r"Choose\s+two",
    r"Select\s+two"
]


def is_multi_choice_question(question_text: str) -> bool:
    """Check if a question is multi-choice based on patterns in the question text."""
    for pattern in MULTI_CHOICE_PATTERNS:
        if re.search(pattern, question_text, re.IGNORECASE):
            return True
    return False


def clean_html_text(text: str) -> str:
    """Remove HTML tags and decode entities."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = unescape(text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_html_exam(html_text: str, missed_only: bool = False) -> Tuple[str, List[Dict]]:
    """Parse HTML quiz page and extract questions.
    
    Args:
        html_text: HTML content
        missed_only: If True, only extract questions that were answered incorrectly
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("BeautifulSoup4 (bs4) is required. Install with: pip install beautifulsoup4")
    
    soup = BeautifulSoup(html_text, 'html.parser')
    title = "Practice Exam 5"
    
    # Try to extract title from page title or h1
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
        if 'AWS Certified Cloud Practitioner' in title_text:
            title = "AWS Certified Cloud Practitioner Practice Exam 5"
    
    questions: List[Dict] = []
    
    # Find all table rows
    rows = soup.find_all('tr')
    
    # Track sequential question ID (starts at 1)
    next_question_id = 1
    
    i = 0
    while i < len(rows):
        row = rows[i]
        th_elements = row.find_all('th')
        
        # Check if this is a question row (has at least 2 th elements, first is a number)
        if len(th_elements) >= 2:
            first_th = th_elements[0]
            question_num_text = first_th.get_text(strip=True)
            
            # Check if first th is a question number
            if question_num_text.isdigit():
                # Check if this question was missed (look for red count in th elements)
                # Structure: [number, question_text, points, green_count, red_count, ...]
                is_missed = False
                if missed_only and len(th_elements) >= 5:
                    red_th = th_elements[4]  # 5th element is red count
                    red_text = red_th.get_text(strip=True)
                    # Extract number from text like "1" or "1 (9.09%)"
                    red_match = re.search(r'(\d+)', red_text)
                    if red_match:
                        red_count = int(red_match.group(1))
                        is_missed = red_count > 0
                
                second_th = th_elements[1]
                
                # Extract question text from paragraphs
                question_paragraphs = second_th.find_all('p')
                question_text_parts = []
                for p in question_paragraphs:
                    text = p.get_text(strip=True)
                    if text and not text.startswith('(view)'):
                        question_text_parts.append(text)
                
                if question_text_parts:
                    question_text = ' '.join(question_text_parts)
                    
                    # Skip if missed_only is True and this question wasn't missed
                    if missed_only and not is_missed:
                        i += 1
                        continue
                    
                    q_id = next_question_id
                    next_question_id += 1
                    
                    # Look for the next row with options (hidden row)
                    if i + 1 < len(rows):
                        next_row = rows[i + 1]
                        options_list = next_row.find('ul', class_='wpProQuiz_questionList')
                        
                        if options_list:
                            # Extract options
                            option_items = options_list.find_all('li')
                            options_dict: Dict[str, str] = {}
                            correct_answers = []
                            
                            # Check if it's multi-choice by input type
                            first_input = options_list.find('input')
                            is_checkbox = first_input and first_input.get('type') == 'checkbox'
                            
                            # Determine question type
                            is_multi = is_checkbox or is_multi_choice_question(question_text)
                            
                            option_index = 0
                            for li in option_items:
                                # Extract option text
                                label = li.find('label')
                                if label:
                                    option_text = clean_html_text(label.get_text())
                                    if option_text:
                                        # Generate option letter dynamically
                                        option_letter = chr(ord('A') + option_index)
                                        options_dict[option_letter] = option_text
                                        
                                        # Check if this is a correct answer
                                        if 'wpProQuiz_answerCorrect' in li.get('class', []):
                                            correct_answers.append(option_letter)
                                        
                                        option_index += 1
                            
                            # Create question object
                            question_obj = {
                                "id": q_id,
                                "question": clean_html_text(question_text),
                                "options": options_dict,
                                "type": "multiChoice" if is_multi else "singleChoice"
                            }
                            
                            # Set answer(s)
                            if is_multi:
                                question_obj["answer"] = correct_answers if correct_answers else ["A"]
                            else:
                                question_obj["answer"] = correct_answers[0] if correct_answers else "A"
                            
                            questions.append(question_obj)
        
        i += 1
    
    # Sort by id
    questions.sort(key=lambda q: q.get("id", 0))
    return title, questions


def convert_file(input_path: str, output_path: str, missed_only: bool = False) -> None:
    """Convert HTML exam file to JSON format.
    
    Args:
        input_path: Path to input HTML file
        output_path: Path to output JSON file
        missed_only: If True, only extract questions that were answered incorrectly
    """
    with open(input_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    title, questions = parse_html_exam(html_content, missed_only=missed_only)
    
    # Sanitize questions to match schema
    sanitized: List[Dict] = []
    for q in questions:
        sanitized.append({
            "id": int(q["id"]),
            "question": q["question"].strip(),
            "options": q.get("options", {}),
            "type": q.get("type", "singleChoice"),
            "answer": q.get("answer", "A" if q.get("type") == "singleChoice" else ["A"]),
        })
    
    data = {"title": title, "questions": sanitized}
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(sanitized)} questions to {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert exam HTML to JSON schema format")
    parser.add_argument("input", help="Input HTML file")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--outdir", default="exams", help="Output directory for JSON files")
    parser.add_argument("--missed-only", action="store_true", help="Only extract questions that were answered incorrectly")
    args = parser.parse_args()
    
    if args.output:
        output_path = args.output
    else:
        base = os.path.splitext(os.path.basename(args.input))[0]
        suffix = "_missed" if args.missed_only else ""
        output_path = os.path.join(args.outdir, f"{base}{suffix}.json")
    
    convert_file(args.input, output_path, missed_only=args.missed_only)


if __name__ == "__main__":
    main()

