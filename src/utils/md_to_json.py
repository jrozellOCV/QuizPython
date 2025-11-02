import json
import os
import re
from typing import List, Dict, Tuple


QUESTION_PATTERN = re.compile(r"^\s*(\d+)\.\s+(.*)")
OPTION_PATTERN = re.compile(r"^\s*-\s+([A-E])\.\s+(.*)")
ANSWER_PATTERN = re.compile(r"^\s*Correct answer:\s*(.+)\s*$", re.IGNORECASE)

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


def parse_markdown_exam(md_text: str) -> Tuple[str, List[Dict]]:
    lines = md_text.splitlines()
    title = "Untitled Exam"
    questions: List[Dict] = []

    # Extract title from a line starting with '# '
    for i, line in enumerate(lines[:20]):
        if line.strip().startswith("# "):
            title = line.strip().lstrip("# ").strip()
            break

    i = 0
    current_q = None
    options: Dict[str, str] = {}
    while i < len(lines):
        line = lines[i]

        q_match = QUESTION_PATTERN.match(line)
        if q_match:
            # Flush previous question if any
            if current_q is not None and options:
                current_q["options"] = options
                questions.append(current_q)
            q_id = int(q_match.group(1))
            q_text = q_match.group(2).strip()
            
            # Determine if this is a multi-choice question
            is_multi = is_multi_choice_question(q_text)
            current_q = {
                "id": q_id, 
                "question": q_text,
                "type": "multiChoice" if is_multi else "singleChoice"
            }
            options = {}
            i += 1
            continue

        opt_match = OPTION_PATTERN.match(line)
        if opt_match and current_q is not None:
            letter = opt_match.group(1)
            text = opt_match.group(2).strip()
            options[letter] = text
            i += 1
            continue

        ans_match = ANSWER_PATTERN.match(line)
        if ans_match and current_q is not None:
            raw = ans_match.group(1).strip()
            
            # Handle multi-choice vs single-choice answers
            if current_q.get("type") == "multiChoice":
                # For multi-choice, parse comma-separated answers
                answers = [ans.strip() for ans in raw.split(",")]
                # Clean up each answer (remove any trailing text)
                clean_answers = []
                for ans in answers:
                    clean_ans = ans.split()[0] if ans.split() else ans
                    if clean_ans in ("A", "B", "C", "D", "E"):
                        clean_answers.append(clean_ans)
                current_q["answer"] = clean_answers if clean_answers else ["A"]
            else:
                # For single-choice, take first answer
                first_letter = raw.split(",")[0].strip()
                first_letter = first_letter.split()[0]
                current_q["answer"] = first_letter if first_letter in ("A", "B", "C", "D", "E") else "A"
            
            i += 1
            continue

        i += 1

    # Flush last question
    if current_q is not None and options:
        current_q["options"] = options
        # Ensure answer exists; if not found, set default
        if "answer" not in current_q:
            if current_q.get("type") == "multiChoice":
                current_q["answer"] = ["A"]
            else:
                current_q["answer"] = "A"
        questions.append(current_q)

    # Sort by id to be safe
    questions.sort(key=lambda q: q.get("id", 0))
    return title, questions


def convert_file(input_path: str, output_path: str) -> None:
    with open(input_path, "r") as f:
        md = f.read()
    title, questions = parse_markdown_exam(md)

    # Conform to schema: preserve type and answer format
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
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert exam markdown to JSON schema format")
    parser.add_argument("inputs", nargs="+", help="Input markdown files")
    parser.add_argument("--outdir", default="exams", help="Output directory for JSON files")
    args = parser.parse_args()

    for input_path in args.inputs:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(args.outdir, f"{base}.json")
        convert_file(input_path, output_path)
        print(f"Converted {input_path} -> {output_path}")


if __name__ == "__main__":
    main()


