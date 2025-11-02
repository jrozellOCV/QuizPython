# Question Schema

[← Back to Documentation Index](index.md)

## Overview

The question schema defines the structure and validation rules for quiz questions. The schema is defined in `question_schema.json` and follows JSON Schema Draft 07.

**Code Reference:**
```1:61:question_schema.json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "AWS Mock Exam",
    "type": "object",
    "required": ["title", "questions"],
    "properties": {
      "title": {
        "type": "string"
      },
      "questions": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["id", "question", "options", "answer"],
          "properties": {
            "id": {
              "type": "integer"
            },
            "question": {
              "type": "string"
            },
            "options": {
              "type": "object",
              "minProperties": 2,
              "maxProperties": 5,
              "additionalProperties": {
                "type": "string"
              },
              "patternProperties": {
                "^[A-E]$": {
                  "type": "string"
                }
              }
            },
            "type": {
              "type": "string",
              "enum": ["singleChoice", "multiChoice"],
              "default": "singleChoice"
            },
            "answer": {
              "oneOf": [
                {
                  "type": "string",
                  "pattern": "^[A-E]$"
                },
                {
                  "type": "array",
                  "items": {
                    "type": "string",
                    "pattern": "^[A-E]$"
                  },
                  "minItems": 1,
                  "maxItems": 5
                }
              ]
            }
          }
        }
      }
    }
  }
```

### Required vs Optional Fields

**Required Fields:**
- `title`: Exam title (string)
- `questions`: Array of question objects (array)
- `id`: Question identifier (integer)
- `question`: Question text (string)
- `options`: Answer choices (object, 2-5 properties)
- `answer`: Correct answer (string or array)

**Optional Fields:**
- `type`: Question type, defaults to "singleChoice"

### Question Types

#### Single Choice (`singleChoice`)

Default question type. Only one answer is correct.

**Answer Format:** Single string: `"A"`, `"B"`, `"C"`, etc.

**Example:**
```json
{
    "id": 1,
    "question": "What is AWS Lambda?",
    "options": {
        "A": "A virtual machine service",
        "B": "A serverless compute service",
        "C": "A database service",
        "D": "A storage service"
    },
    "type": "singleChoice",
    "answer": "B"
}
```

#### Multi-Choice (`multiChoice`)

Multiple answers can be correct. User must select all correct answers (exact match required).

**Answer Format:** Array of strings: `["A", "C"]`

**Example:**
```json
{
    "id": 2,
    "question": "Which services are compute services? (Choose TWO)",
    "options": {
        "A": "Amazon EC2",
        "B": "Amazon S3",
        "C": "AWS Lambda",
        "D": "Amazon RDS"
    },
    "type": "multiChoice",
    "answer": ["A", "C"]
}
```

### Field Specifications

#### `id` (Required)
- **Type**: Integer
- **Purpose**: Unique identifier within exam
- **Example**: `1`, `42`, `100`

#### `question` (Required)
- **Type**: String
- **Purpose**: Question text displayed to user
- **Example**: `"What is AWS Lambda?"`

#### `options` (Required)
- **Type**: Object (dictionary)
- **Constraints**: 
  - Minimum 2 properties, maximum 5
  - Keys must be single letters A-E (pattern: `^[A-E]$`)
  - Values must be strings
- **Example**:
```json
{
    "A": "Option A text",
    "B": "Option B text",
    "C": "Option C text",
    "D": "Option D text"
}
```

#### `type` (Optional)
- **Type**: String enum
- **Values**: `"singleChoice"` or `"multiChoice"`
- **Default**: `"singleChoice"`

#### `answer` (Required)
- **Single Choice**: String matching option key (`"A"`, `"B"`, etc.)
- **Multi-Choice**: Array of strings, each matching option keys
- **Constraints**:
  - Must match pattern `^[A-E]$`
  - Multi-choice: minimum 1 item, maximum 5 items
  - All values must exist in options
- **Examples**:
  - Single: `"B"`
  - Multi: `["A", "C"]`

### Validation Rules

1. **Option Count**: 2-5 options required
2. **Option Keys**: Must be A-E (case-sensitive, single letter)
3. **Answer Format**: 
   - Single: string matching option key
   - Multi: array of strings matching option keys
4. **Answer Validity**: All answer values must exist in options
5. **Multi-Choice Constraints**: 1-5 answers required

### Complete Examples

**Single Choice Example:**
```json
{
    "id": 1,
    "question": "What is AWS?",
    "options": {
        "A": "A cloud computing platform",
        "B": "A programming language",
        "C": "An operating system",
        "D": "A database"
    },
    "type": "singleChoice",
    "answer": "A"
}
```

**Multi-Choice Example:**
```json
{
    "id": 2,
    "question": "Which AWS services provide storage? (Choose TWO)",
    "options": {
        "A": "Amazon S3",
        "B": "Amazon EC2",
        "C": "Amazon EBS",
        "D": "AWS Lambda"
    },
    "type": "multiChoice",
    "answer": ["A", "C"]
}
```

---
