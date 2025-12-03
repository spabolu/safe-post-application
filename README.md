# SafePost

Check if your images contain personally identifiable information (PII) before posting on social media.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file with your Google Gemini API key:
```env
GEMINI_API_KEY=your-api-key-here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

## Run

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## What it checks

- Email addresses
- Addresses
- Phone numbers
- License plates

## Testing

Run the test script to analyze multiple images:

```bash
python main.py
```

Create a `test_images` folder and add your test images there.

## Analysis

Generate confusion matrices and performance charts from test results:

```bash
# Install analysis dependencies
pip install -r requirements_analysis.txt

# Run analysis
python analyze_results.py
```

This will generate charts and metrics from the CSV results in `test_results_output/analysis/`.
