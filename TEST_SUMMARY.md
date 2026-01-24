# Test Summary — OpenCart Automated UI Testing

## Test execution overview

Automated UI tests were executed against a local OpenCart instance.
The focus was on validating core customer journeys and common failure paths.

---

## Coverage summary

- Registration
- Login and logout
- Product browsing
- Cart management
- Checkout flow

Both positive and negative scenarios were included.

---

## Results

- Total automated tests: (66)
- Passed: (64)
- Failed: (2)
- Skipped: (0)

Failures were reviewed and matched against expected behaviour or known issues.

---

## Observations

- Core flows are stable under automation
- Some UI interactions are sensitive to timing
- Proper waits are critical for reliability

---

## Limitations

- Local execution only
- UI behaviour depends on browser and machine performance
- Not representative of production traffic

---

## Conclusion

The automated test suite provides reliable regression coverage for OpenCart UI behaviour.
It complements manual testing and improves confidence during changes and refactoring.

Author: George Petre
