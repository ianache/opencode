# AGENTS.md

This file contains guidelines and commands for agentic coding agents working in this GraphRAG repository.

## Project Overview

This is a Python-based GraphRAG (Graph Retrieval-Augmented Generation) project that uses Neo4j as the graph database and LangChain for graph operations. The project focuses on building and querying knowledge graphs from structured data.

## Development Environment

- **Python Version**: 3.12+
- **Package Manager**: uv (based on uv.lock file)
- **Virtual Environment**: .venv (activated automatically)
- **Project Structure**: Single-file application (main.py) with pyproject.toml

## Build and Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Activate virtual environment (if needed manually)
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Running the Application
```bash
# Run the main application
python main.py

# Alternative with uv
uv run python main.py
```

### Testing
```bash
# No test framework currently configured
# To add tests, install pytest and create test_*.py files
# uv add pytest
# uv run pytest
```

### Code Quality
```bash
# No linting/formatting tools currently configured
# Recommended additions:
# uv add black isort flake8 mypy
# uv run black .
# uv run isort .
# uv run flake8 .
# uv run mypy .
```

## Code Style Guidelines

### Import Organization
- Standard library imports first (os, sys, etc.)
- Third-party imports next (pandas, langchain_*)
- Local imports last (if any)
- Use `from` imports for specific modules when appropriate
- Comment out alternative imports with explanation (see main.py:2)

### Naming Conventions
- **Variables**: snake_case (e.g., `news_data`, `graph_connection`)
- **Functions**: snake_case with descriptive names
- **Constants**: UPPER_SNAKE_CASE (e.g., `NEO4J_URI`)
- **Classes**: PascalCase (if added later)
- **Files**: snake_case.py

### Code Structure
- Environment variable setup at the top
- Import statements organized and grouped
- Main execution logic in sequential order
- Print statements for debugging/verification are acceptable

### Error Handling
- Use try-except blocks for external connections
- Handle database connection errors gracefully
- Validate data sources before processing
- Log errors appropriately (add logging if needed)

### Type Hints
- Add type hints for function signatures
- Use pandas DataFrame types where appropriate
- Consider adding mypy for static type checking

### Documentation
- Use docstrings for functions and classes
- Add inline comments for complex logic
- Explain environment variable requirements
- Document data source formats and expectations

## Dependencies and Libraries

### Core Dependencies
- `langchain-community`: Graph operations and community integrations
- `langchain-core`: Core LangChain functionality
- `langchain-neo4j`: Neo4j graph database integration
- `neo4j`: Neo4j Python driver
- `pandas`: Data manipulation and analysis

### Recommended Additions
- `python-dotenv`: Environment variable management
- `pytest`: Testing framework
- `black`: Code formatting
- `mypy`: Static type checking
- `loguru`: Enhanced logging

## Security Best Practices

- Never commit credentials or environment variables
- Use environment variables for sensitive data (Neo4j credentials)
- Consider using `.env` files with python-dotenv
- Validate external data sources before processing
- Use secure connection strings for databases

## Database Configuration

- Neo4j connection uses Bolt protocol
- Default port: 7687
- Schema refresh disabled for performance (`refresh_schema=False`)
- Consider adding connection pooling for production

## Data Handling

- Use pandas for CSV data processing
- Validate data structure before graph insertion
- Consider data cleaning and preprocessing steps
- Handle missing values appropriately

## Testing Strategy

When adding tests:
- Create `tests/` directory
- Use pytest fixtures for database connections
- Mock external data sources for unit tests
- Test graph operations with sample data
- Add integration tests for end-to-end workflows

## Git Workflow

- Use conventional commit messages
- Create feature branches for new functionality
- Ensure main.py runs successfully before commits
- Consider adding pre-commit hooks for code quality
