# Traceability Matrix — OpenCart Automated UI Testing

This matrix provides a high-level view of automated test coverage
for the OpenCart storefront UI.

The purpose is to show which application features are validated
by the automated test suite, without listing every individual test case.

---

## Feature-level traceability

| Feature | Behaviour validated | Coverage type | Status |
|-------|---------------------|---------------|--------|
| Registration | Valid and invalid user registration flows | Automated UI | Covered |
| Login / Logout | Successful login and authentication failures | Automated UI | Covered |
| Product browsing | Product list display and navigation | Automated UI | Covered |
| Cart management | Add, update, and manage cart items | Automated UI | Covered |
| Checkout | End-to-end checkout and validation handling | Automated UI | Covered |

---

## Notes

- A total of **66 automated UI tests** were executed for the features above.
- Multiple test cases exist per feature, covering:
  - positive scenarios
  - negative scenarios
  - edge cases
- Detailed test logic is maintained within the automation codebase.
- This matrix is intentionally kept at feature level to remain readable
  and maintainable as the test suite grows.
