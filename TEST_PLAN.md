## `TEST_PLAN.md`

# Test Plan — OpenCart Automated UI Testing

## 1. Objective

Define the scope, strategy, and execution approach for automated UI testing of the
OpenCart web application.

The goal is to ensure core user journeys work as expected and remain stable over time.

---

## 2. Scope

### In scope
- Automated UI validation of:
  - registration
  - login / logout
  - product browsing
  - cart operations
  - checkout flow
- Positive and negative scenarios
- Regression-ready automation

### Out of scope
- API-level testing
- Performance testing
- Security testing
- External service integrations

---

## 3. Test strategy

- Tests are written using a Page Object Model structure
- Each page exposes clear, reusable actions
- Test cases focus on behaviour, not UI implementation
- Assertions verify:
  - navigation
  - expected elements
  - error messages
  - successful completion of flows
- Known issues are handled explicitly where required

---

## 4. Test environment

- Application: OpenCart
- Environment type: Local (XAMPP)
- Browser automation: WebDriver
- Primary browser: Chrome
- Execution: Local machine

---

## 5. Entry criteria

- Application is accessible
- Test environment configured
- Test data available

---

## 6. Exit criteria

- All planned automated tests executed
- Failures reviewed and documented
- Summary updated

---

## 7. Deliverables

- Automated test scripts
- Execution results
- Test summary and traceability


## 8. Risks and mitigations

- UI changes may break locators and cause test failures  
  Mitigation: Use Page Object Model and reusable locators to reduce maintenance.

- Timing issues may lead to flaky tests  
  Mitigation: Apply explicit waits and proper synchronisation instead of hard delays.

- Test results may depend on existing data  
  Mitigation: Use controlled test data where possible and document assumptions.

- Local execution does not represent production behaviour  
  Mitigation: Clearly document environment limitations and focus on functional validation.