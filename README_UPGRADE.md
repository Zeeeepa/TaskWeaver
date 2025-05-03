# TaskWeaver Dependency Upgrade

This document outlines the dependency upgrades made in version 0.0.13.

## Updated Dependencies

### Main Requirements
- injector: 0.19.0 → 0.22.0
- tiktoken: 0.3.3 → 0.9.0
- pyyaml: 6.0 → 6.0.2
- typing-extensions: 4.4.0 → 4.13.2
- PyQt5: 5.15.0 → 5.15.11
- openai: 1.0.0 → 1.77.0
- python-dotenv: 1.0.0 → 1.1.0
- requests: 2.28.0 → 2.32.3

### UI Requirements
- fastapi: 0.68.0 → 0.115.12
- uvicorn: 0.15.0 → 0.34.2
- jinja2: 3.0.1 → 3.1.6
- python-multipart: 0.0.5 → 0.0.20
- requests: 2.26.0 → 2.32.3
- pygithub: 1.55 → 2.6.1
- pyngrok: 5.1.0 → 7.2.5
- injector: 0.19.0 → 0.22.0
- pydantic: 1.8.2 → 2.11.4

## Compatibility Notes

### Pydantic v2
The upgrade to Pydantic v2 (2.11.4) may require code changes if your project uses Pydantic models. Key differences include:
- Different import paths for some features
- Changes to validation behavior
- Performance improvements

### OpenAI SDK
The upgrade to OpenAI SDK 1.77.0 includes significant API changes from the 1.0.0 version:
- Updated client methods
- New model support
- Enhanced streaming capabilities

## Testing Recommendations
After upgrading, it's recommended to:
1. Test all UI components thoroughly
2. Verify OpenAI API integration
3. Check any code that relies on Pydantic models
4. Ensure PyQt5 UI elements render correctly

## Version History
- 0.0.12: Previous release
- 0.0.13: Current release with dependency upgrades

