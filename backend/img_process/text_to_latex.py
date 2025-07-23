import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def convert_to_latex(text_content):
    """
    Convert a string of text to a LaTeX document using the Gemini API.
    """
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
            
        genai.configure(api_key=gemini_api_key)
        
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        prompt = f"""
Please convert the following text into a complete, well-structured LaTeX document.
- The document class should be 'article'.
- Use appropriate LaTeX packages like 'graphicx' and 'amsmath' if needed.
- Ensure package versions are not too old or expired.
- Identify and format tables using the 'tabular' environment.
- Identify and format lists using 'itemize' or 'enumerate'.
- Format headings, titles, and captions appropriately.
- Escape any special LaTeX characters.
- Ensure the entire output is a single, valid LaTeX document ready for compilation.

Here is the text to convert:
---
{text_content}
---
"""
        
        response = model.generate_content(prompt)
        
        latex_code = response.text
        if "```latex" in latex_code:
            latex_code = latex_code.split("```latex")[1].split("```")[0]
        elif "```" in latex_code:
            latex_code = latex_code.split("```")[1].split("```")[0]

        return latex_code.strip()

    except Exception as e:
        print(f"An error occurred while converting to LaTeX with Gemini: {e}")
        return f"""\\documentclass{{article}}
\\usepackage{{amsmath}}
\\begin{{document}}
An error occurred during LaTeX conversion: {str(e)}
\\end{{document}}
"""
