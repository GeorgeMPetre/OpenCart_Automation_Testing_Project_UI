# OpenCart Automation Testing Project (UI)

This repository contains an automated UI testing project for the OpenCart e-commerce platform.
The project focuses on validating core customer journeys using automated browser tests,
following a structured Page Object Model approach.

The tests are designed to simulate real user behaviour and to verify both functional
correctness and basic UI behaviour across key flows.

Automation is used to improve repeatability, reduce manual effort, and provide reliable
regression coverage.

---

## Project purpose

The main goals of this project are:

- Automate core OpenCart UI user flows
- Validate functionality through real browser interaction
- Cover both positive and negative scenarios
- Apply clean test design using Page Object Model
- Produce maintainable and readable automation code
- Support future regression testing

---

## System under test

- Application: OpenCart
- Type: Web application (UI)
- Environment: Local instance (XAMPP)
- Browsers: Chrome (primary), others optional depending on setup

---

## Test scope

### In scope
- User registration
- Login and logout
- Product browsing
- Cart functionality
- Checkout flow
- UI validations related to core behaviour

### Out of scope
- API testing
- Performance or load testing
- Security testing
- Third-party integrations

---

## Test approach

- Automated UI testing using a browser driver
- Page Object Model for separation of concerns
- Test cases focused on user behaviour, not implementation details
- Assertions used to validate:
  - page navigation
  - visible elements
  - form validation
  - successful and failed user actions
- Known defects are handled and documented, not hidden

---

## Repository structure

├── tests/                
├── pages/               
├── utils/               
├── README.md
├── TEST_PLAN.md
├── TEST_ROADMAP.md
├── TRACEABILITY.md
├── TEST_SUMMARY.md

How to run the tests
Ensure OpenCart is running locally

Install required dependencies

Configure browser driver if needed

Execute the test suite using the test runner

Exact commands depend on the test framework used and are documented in the project setup.

Documentation included
TEST_PLAN.md – automation scope, strategy, environment

TEST_ROADMAP.md – future improvements and coverage growth

TRACEABILITY.md – mapping between features and automated tests

TEST_SUMMARY.md – execution results and observations

Limitations
Tests run against a local environment

UI timing can vary based on machine performance

Some behaviours depend on OpenCart configuration and test data

These limits are documented intentionally.

Author
George Petre
Portfolio: https://georgempetre.github.io