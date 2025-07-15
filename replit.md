# replit.md

## Overview

This repository contains a Python-based multi-agent browser automation system designed to interact with Ajio.com (an Indian e-commerce platform) as a human user would. The system uses Playwright for browser automation and implements a modular agent-based architecture to handle different aspects of e-commerce interaction including login, order management, returns/replacements, and deadline reminders.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The system follows a multi-agent architecture pattern where specialized agents handle different aspects of the automation workflow:

### Backend Architecture
- **Language**: Python 3.7+
- **Browser Automation**: Playwright (headless/headful modes)
- **Web Scraping**: crawl4ai + BeautifulSoup for content extraction
- **Database**: SQLite for local data persistence
- **CLI Interface**: Typer for command-line interactions
- **Testing**: pytest for unit and integration tests

### Agent-Based Design
The system implements a specialized agent pattern where each agent has a specific responsibility:
- **LoginAgent**: Handles authentication flow
- **OrderAgent**: Scrapes order information
- **ReturnAgent**: Processes return/replace requests
- **ReminderAgent**: Manages deadlines and notifications

## Key Components

### 1. Multi-Agent System
- **LoginAgent** (`agents/login_agent.py`): Manages browser initialization, popup dismissal, and Ajio.com authentication flow including OTP verification
- **OrderAgent** (`agents/order_agent.py`): Navigates to orders page and extracts product details, prices, delivery status, and return information
- **ReturnAgent** (`agents/return_agent.py`): Processes natural language commands to execute return/replace actions via browser automation
- **ReminderAgent** (`agents/reminder_agent.py`): Tracks return deadlines and manages SQLite database operations

### 2. Utility Components
- **PopupHandler** (`utils/popup_handler.py`): Intelligent popup detection and dismissal using multiple selector strategies
- **CrawlHelper** (`utils/crawl4ai_helper.py`): Enhanced web scraping capabilities with BeautifulSoup integration
- **Database** (`utils/database.py`): SQLite operations with connection management and table initialization

### 3. Data Models
- **Order** (`models/order.py`): Dataclass-based model for order information with validation and serialization

### 4. Configuration Management
- **Config** (`config.py`): Centralized configuration for URLs, timeouts, selectors, and API settings

## Data Flow

1. **Initialization**: Database tables are created/verified, agents are instantiated
2. **Authentication Flow**: LoginAgent launches browser → dismisses popups → handles login modal → processes OTP verification
3. **Order Extraction**: OrderAgent navigates to orders page → scrapes order cards → extracts structured data
4. **Data Persistence**: ReminderAgent saves order information to SQLite database
5. **Action Processing**: ReturnAgent processes natural language commands → finds matching orders → executes browser actions
6. **Deadline Management**: ReminderAgent checks return deadlines and displays notifications

### Database Schema
- **orders**: Stores order details including return options and deadlines
- **sessions**: Manages login session persistence
- **reminders**: Tracks deadline notifications

## External Dependencies

### Core Dependencies
- **Playwright**: Browser automation framework for realistic user interaction
- **crawl4ai**: Advanced web scraping with AI-enhanced content extraction
- **BeautifulSoup4**: HTML parsing and content extraction
- **Typer**: Modern CLI framework for user interaction
- **SQLite3**: Built-in Python database for local persistence

### Optional Integrations
- **Groq API**: Natural language processing for command interpretation (requires GROQ_API_KEY environment variable)
- **aiohttp**: Async HTTP client for enhanced scraping capabilities

### Browser Requirements
- Chromium browser (automatically installed by Playwright)
- Multiple user agent strings for realistic browsing simulation

## Deployment Strategy

### Local Development
- Environment setup via pip/conda with requirements.txt
- SQLite database auto-initialization on first run
- Configurable headless/headful browser modes for development and production

### Configuration Management
- Environment variables for sensitive data (API keys)
- Centralized config.py for all system parameters
- Separate test configuration for isolated testing

### Data Management
- Local SQLite database with automatic backup capabilities
- 30-day retention policy for old data
- Database migration support for schema updates

### Testing Strategy
- pytest-based test suite with mocked browser interactions
- Separate test database for isolation
- Mock fixtures for Playwright page objects and order data

### Security Considerations
- No credential storage (user enters OTP manually)
- Realistic user agent rotation
- Rate limiting through configurable delays
- Popup handling to avoid detection as automation