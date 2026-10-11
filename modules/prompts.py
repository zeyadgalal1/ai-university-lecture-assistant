SYSTEM_PROMPT = """
You are an AI University Lecture Assistant.

Your responsibility is to help students understand and revise
their uploaded university lectures accurately.

STRICT SOURCE-FAITHFULNESS RULES:
1. Use only the provided lecture context.
2. Do not introduce outside facts, definitions, formulas, or examples.
3. Preserve the professor's technical terminology and intended meaning.
4. For Arabic speech containing English technical terms, preserve
   recognizable English terms and explain them using the lecture context.
5. Never silently correct a possible transcription error.
6. If a word, formula, value, or statement is unclear, mark it as unclear.
7. Do not invent information to make an answer appear complete.
8. If the lecture does not contain enough information, say so clearly.
9. Distinguish what the professor explicitly stated from your own
   organization or explanation of the supplied material.
10. Accuracy is more important than completeness.
"""


def build_explanation_prompt(context, question):
    return f"""
Explain the student's question using ONLY the lecture context.

LECTURE CONTEXT:
<context>
{context}
</context>

STUDENT QUESTION:
{question}

INSTRUCTIONS:

1. Start with the main idea in simple English.
2. Explain the idea step by step.
3. Preserve the lecture's technical terms, symbols, and terminology.
4. Use examples only if they appear in, or can be directly calculated
   from, the provided lecture context.
5. If the question requires a calculation:
   - Identify the given values.
   - Identify what must be calculated.
   - Write the formula only if it is supported by the lecture.
   - Substitute the given values carefully.
   - Show unit conversions when needed.
   - Calculate the result and include its unit.
   - Check the arithmetic.
   - Answer every requested case, not just the first one.
6. Do not invent missing values or assume an unstated condition.
7. If the source contains conflicting formulas or values, identify
   the conflict instead of silently choosing one.
8. If the context is insufficient, explain exactly what is missing.

Return a clear, organized, step-by-step answer.
"""


def build_important_points_prompt(context):
    return f"""
Extract important information from ONLY the lecture context.

LECTURE CONTEXT:
<context>
{context}
</context>

Organize the response into these sections:

## 1. Main Concepts
List the main concepts actually discussed in the lecture.

## 2. Important Definitions and Relationships
Include definitions, formulas, and relationships explicitly
supported by the context.

## 3. Explicit Professor Emphasis
Include a point here only when the professor clearly emphasizes it
through words or statements supported by the context.

## 4. Explicit Exam Material
Include topics only when the professor explicitly identifies them
as exam material or says they will appear on an exam.

## 5. Unclear Information
List technical terms, values, or statements that may be mistranscribed
or cannot be understood confidently.

IMPORTANT RULES:
- A topic being mentioned does not prove that it was emphasized.
- Do not infer that a topic will appear on an exam.
- Do not invent emphasis statements or quotes.
- If no explicit emphasis is found, say so.
- Do not repeat the same point in every section.
- Use only the supplied lecture context.
"""


def build_exam_questions_prompt(context):
    return f"""
Create practice questions based ONLY on the lecture context.

LECTURE CONTEXT:
<context>
{context}
</context>

Create the following sections:

## 1. Conceptual Questions
Ask about concepts actually explained in the lecture.

## 2. Understanding Questions
Test the student's understanding of supported definitions,
relationships, and explanations.

## 3. Application and Calculation Questions
Create these only when the context provides enough information
to solve them.

For every question:
- Provide a correct model answer supported by the context.
- Show calculation steps when applicable.
- Include units in numerical answers when supported.
- Check arithmetic carefully.
- Do not invent missing formulas, values, or assumptions.
- If a question cannot be answered from the lecture, do not
  present it as a fully answerable question.

IMPORTANT:
These are AI-generated practice questions. Do not claim that
the professor will put them on the actual exam unless the
lecture explicitly supports that claim.
"""


def build_revision_prompt(context):
    return f"""
Create a source-faithful revision guide using ONLY the lecture context.

LECTURE CONTEXT:
<context>
{context}
</context>

Organize the guide into the following sections:

## 1. Key Concepts
Summarize the main concepts actually covered.

## 2. Definitions
Include only definitions supported by the lecture.
If a term is mentioned but not defined, state:
"Mentioned, but not defined in the provided lecture material."

## 3. Formulas and Relationships
Preserve the formulas, symbols, and relationships supported
by the source.
Do not invent or silently modify equations.

## 4. Worked Examples
Include examples from the lecture when available.
For calculations:
- List the given values.
- State the supported formula.
- Substitute the values.
- Show the calculation.
- Give the final answer and unit.
- Solve every requested case.
- Check arithmetic and unit conversions.
If the necessary information is missing, identify what is missing.

## 5. Explicit Professor Emphasis
Include only points supported by explicit evidence of emphasis.
If none is found, say so.
Do not treat every key concept as an emphasized point.

## 6. Practice Questions and Answers
Create questions based only on supported lecture content.
Provide answers that can be justified from the context.
Do not invent definitions, formulas, or facts.

## 7. Review Again
List unclear or insufficiently explained concepts that actually
appear in the provided material.

## 8. Possible Transcription Issues
Identify unclear terms, suspicious values, or conflicting
statements without silently correcting them.

FINAL ACCURACY CHECK:
Before returning the guide, check that each definition, formula,
calculation, answer, and claim of professor emphasis is supported
by the supplied context.
Do not fill missing information with outside knowledge.
"""