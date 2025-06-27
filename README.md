# Job Genie - AI-Powered Job Application Assistant

JobGenie helps job seekers by generating tailored cover letters, resume highlights, and interview preparation materials using AI.

## Features
- Generate customized cover letters
- Extract key resume highlights
- Create interview Q&A based on job listings
- PDF generation for application materials

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/JobGenie.git
cd JobGenie
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up your OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage
```python
from jobgenie_app import generate_cover_letter, generate_highlights, generate_interview_prep

# Example usage
cover_letter = generate_cover_letter(resume_text, job_listing_text)
highlights = generate_highlights(resume_text)
interview_prep = generate_interview_prep(resume_text, job_listing_text)
```

## Configuration
Create a `.env` file with:
- `OPENAI_API_KEY`: Your OpenAI API key
- (Add any other config variables here)

## Contributing
Pull requests are welcome! For major changes, please open an issue first.

## License
[MIT](https://choosealicense.com/licenses/mit/)
