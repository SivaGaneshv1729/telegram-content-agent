# Contributing to Telegram Content Agent

First off, thank you for considering contributing to the Telegram Content Agent! It's people like you that make open-source software such a great community.

## How Can I Contribute?

### Reporting Bugs
This section guides you through submitting a bug report. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.
- **Ensure the bug was not already reported** by searching on GitHub under Issues.
- If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements
This section guides you through submitting an enhancement suggestion, including completely new features and minor improvements to existing functionality.
- Open a new Issue detailing the enhancement.
- Provide a clear and detailed explanation of the feature you want and why it's important.

### Pull Requests
The process described here has several goals:
- Maintain project quality
- Fix problems that are important to users
- Engage the community in working toward the best possible agent

Please follow these steps to have your contribution considered by the maintainers:
1. **Fork** the repository and clone it locally.
2. **Create a branch** for your edits (`git checkout -b feature/AmazingFeature`).
3. **Set up the development environment**: Ensure you have Python 3.11 installed, create a virtual environment, and run `pip install -r requirements.txt`.
4. **Make your changes**. Ensure your code is clean and well-documented.
5. **Test** your changes locally.
6. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).
7. **Push** to the branch (`git push origin feature/AmazingFeature`).
8. **Open a Pull Request** against the `main` branch.

## Code Style
- Please follow standard PEP-8 style guidelines for Python code.
- Ensure all new functions have appropriate docstrings detailing parameters and return values.
- Keep the system architecture clean; do not tightly couple the extraction, LLM orchestration, and storage logic.
