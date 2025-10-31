# Contributing to Advanced YouTube Downloader

Thank you for your interest in contributing to the Advanced YouTube Downloader! We welcome contributions from developers of all skill levels.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Guidelines](#code-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Feature Requests](#feature-requests)
- [Bug Reports](#bug-reports)

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Git installed on your system
- Basic knowledge of Python and web development
- Familiarity with Streamlit framework (helpful but not required)

### First Steps
1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

### 1. Fork and Clone
```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/Advanced-YouTube-Downloader.git
cd Advanced-YouTube-Downloader
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy
```

### 4. Run the Application
```bash
streamlit run app.py
```

### 5. Set Up Pre-commit Hooks (Optional but Recommended)
```bash
pip install pre-commit
pre-commit install
```

## Code Guidelines

### Python Style Guide
We follow PEP 8 with some modifications:

- **Line length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Naming conventions**:
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Variables: `snake_case`

### Code Formatting
Use Black for automatic code formatting:
```bash
black app.py scheduler_service.py
```

### Import Organization
```python
# Standard library imports
import os
import sys
import time

# Third-party imports
import streamlit as st
import yt_dlp

# Local imports
from utils import helper_function
```

### Documentation Standards
- Use docstrings for all functions and classes
- Follow Google docstring format
- Include type hints where possible

Example:
```python
def download_video(url: str, quality: str, audio_choice: str) -> dict:
    """Download a single YouTube video.
    
    Args:
        url: YouTube video URL
        quality: Video quality setting
        audio_choice: Audio inclusion option
        
    Returns:
        Dictionary containing download result and file path
        
    Raises:
        ValueError: If URL is invalid
        ConnectionError: If network issues occur
    """
    pass
```

### Error Handling
- Always handle exceptions appropriately
- Use specific exception types
- Provide meaningful error messages
- Log errors for debugging

Example:
```python
try:
    result = download_video(url, quality, audio_choice)
except ValueError as e:
    st.error(f"Invalid URL: {e}")
    return None
except ConnectionError as e:
    st.error(f"Network error: {e}")
    return None
```

## Project Structure

### Key Files and Directories
```
├── app.py                    # Main Streamlit application
├── scheduler_service.py      # Background scheduler service
├── requirements.txt          # Python dependencies
├── docs/                     # Documentation
│   ├── API.md
│   ├── USER_GUIDE.md
│   └── INSTALLATION.md
├── downloads/                # Downloaded files (created at runtime)
├── test_downloads/           # Test download directory
└── __pycache__/             # Python cache (ignore)
```

### Adding New Features

When adding new features:

1. **Plan the feature** - Create an issue describing the feature
2. **Design the UI** - Sketch out Streamlit interface changes
3. **Implement backend logic** - Add core functionality
4. **Create UI components** - Add Streamlit interface
5. **Add error handling** - Handle edge cases and errors
6. **Write tests** - Create unit tests for new functionality
7. **Update documentation** - Add to user guide and API docs

### Code Organization

#### Main Application (app.py)
- Keep UI logic separate from business logic
- Use helper functions for complex operations
- Organize code in logical sections with clear comments

#### Helper Functions
Create separate functions for:
- Video download operations
- File management
- History operations
- Scheduler operations
- Utility functions

#### State Management
Use Streamlit session state appropriately:
```python
if 'download_progress' not in st.session_state:
    st.session_state.download_progress = {}
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_downloads.py
```

### Writing Tests
Create tests for:
- Download functions
- URL validation
- File operations
- Time parsing
- Error handling

Example test:
```python
import pytest
from app import parse_time_to_seconds

def test_parse_time_to_seconds():
    assert parse_time_to_seconds("1:30") == 90
    assert parse_time_to_seconds("1:30:45") == 5445
    
    with pytest.raises(ValueError):
        parse_time_to_seconds("invalid")
```

### Test Guidelines
- Write tests for all new functions
- Test both success and failure cases
- Use meaningful test names
- Mock external dependencies (yt-dlp, file system)

## Submitting Changes

### Branch Naming
Use descriptive branch names:
- `feature/add-video-preview`
- `bugfix/fix-playlist-loading`
- `docs/update-installation-guide`
- `refactor/improve-error-handling`

### Commit Messages
Follow conventional commit format:
```
type(scope): description

feat(download): add video preview functionality
fix(scheduler): resolve timezone handling bug
docs(readme): update installation instructions
refactor(ui): improve code organization
```

### Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black --check app.py
   flake8 app.py
   
   # Test the application manually
   streamlit run app.py
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat(download): add video preview functionality"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

### Pull Request Template
Include in your PR description:

- **Description**: What does this PR do?
- **Changes**: List of specific changes made
- **Testing**: How was this tested?
- **Screenshots**: For UI changes
- **Breaking Changes**: Any breaking changes?
- **Related Issues**: Link to related issues

## Feature Requests

### Before Requesting a Feature
1. Check existing issues for similar requests
2. Consider if the feature fits the project scope
3. Think about implementation complexity
4. Consider impact on existing users

### Creating Feature Requests
Use the feature request template:

```markdown
## Feature Description
Brief description of the feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What other approaches were considered?

## Additional Context
Any other relevant information
```

### Feature Implementation Priority
Features are prioritized based on:
- User demand and benefit
- Implementation complexity
- Maintenance overhead
- Compatibility with existing features

## Bug Reports

### Before Reporting a Bug
1. Update to the latest version
2. Check if the issue already exists
3. Try to reproduce the bug consistently
4. Gather relevant information

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Environment
- OS: Windows/macOS/Linux
- Python version:
- Application version:
- Browser (if applicable):

## Error Messages
Any error messages or logs

## Screenshots
If applicable, add screenshots
```

## Code Review Process

### For Reviewers
- Be constructive and respectful
- Focus on code quality and functionality
- Test changes when possible
- Provide specific feedback
- Approve when ready

### For Contributors
- Respond to feedback promptly
- Make requested changes
- Ask questions if feedback is unclear
- Be patient with the review process

## Development Guidelines

### Performance Considerations
- Optimize for user experience
- Handle large playlists efficiently
- Use progress indicators for long operations
- Implement proper error recovery

### Security Guidelines
- Validate all user inputs
- Handle URLs safely
- Don't store sensitive information
- Use secure coding practices

### Accessibility
- Use clear, descriptive labels
- Provide keyboard navigation
- Use appropriate color contrasts
- Include alt text for images

### Browser Compatibility
- Test in major browsers
- Use standard web technologies
- Provide fallbacks for newer features
- Consider mobile users

## Release Process

### Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version in appropriate files
- Tag releases in Git
- Write clear release notes

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] Release notes written
- [ ] Breaking changes documented

## Getting Help

### Community Support
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For general questions and help
- **Discord/Chat**: Real-time community support (if available)

### Documentation
- **User Guide**: For end-user help
- **API Documentation**: For technical details
- **Installation Guide**: For setup help

### Mentorship
New contributors are welcome! We're happy to help you:
- Understand the codebase
- Choose appropriate first issues
- Navigate the development process
- Learn best practices

## Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes
- Invited to join the maintainer team (for significant contributions)

## Code of Conduct

### Our Standards
- Be welcoming and inclusive
- Respect different viewpoints
- Focus on constructive feedback
- Help create a positive environment

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing private information

### Enforcement
Violations may result in:
- Warning from maintainers
- Temporary ban from project
- Permanent ban in severe cases

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Advanced YouTube Downloader! Your help makes this project better for everyone.