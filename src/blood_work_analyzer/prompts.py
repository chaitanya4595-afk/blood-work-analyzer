SECTION_SEPARATOR = "===DIET PLAN==="

EXTRACTION_PROMPT = """
You are a medical data extraction assistant.

From the blood report below, extract ALL test values and classify each one as
HIGH, LOW, or NORMAL based on the reference ranges provided in the report.

Format your response as:
- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range

Blood Report:
{blood_report}
"""

DIET_PROMPT = """
You are a clinical nutritionist specializing in Indian dietary habits.

Based on the blood work analysis below, write:
1. A short health summary in 4-5 lines explaining the patient's condition in simple language
2. A short, practical Indian diet plan having only two sections:
   (1) Foods to avoid
   (2) Foods to eat more of

Do not include any other sections in the diet plan. Use a bold subheading and
bullet points for each section.

Do not add a heading to the health summary or the diet plan. Put a line
containing only {separator} between the health summary and the diet plan.

Blood Work Analysis:
{extracted_values}
"""
