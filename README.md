# Vumit - AI-powered Git Analysis Tool

Vumit is a command-line tool that uses Google's Gemini AI to analyze Git changes and generate merge request descriptions.

Version: 0.1.0

## Installation

```bash
pip install -e .
```

## Configuration

Vumit requires a Google Gemini API key to function. There are several ways to configure this:

1. Environment Variable (Recommended for Development):
   ```bash
   export GEMINI_API_KEY='your-api-key'
   ```

2. Configuration File (Recommended for Production):
   Create a file at `~/.config/vumit/config.ini`:
   ```ini
   [gemini]
   api_key = your-api-key
   ```

Never commit your API key to version control or include it directly in your code.

## Usage

### Commands

1. Check code changes:
```bash
vumit check
```
or
```bash
vumit check --target <target-branch> # Default: dev
```

Analyzes diff commits (compared with target branch) in your Git repository and provides AI-powered recommendations.

2. Generate merge request description:
```bash
vumit report
```
or

```bash
vumit report --target <target-branch> # Default: dev
```
Generates a detailed merge request description based on your changes and repository context.

## Requirements

- Python 3.9 or higher
- Git repository
- Google Gemini API key

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.