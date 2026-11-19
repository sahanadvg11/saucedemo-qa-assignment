# Test Plan — SauceDemo (https://www.saucedemo.com)

## 1. Objective
Verify that login, product listing/sorting, cart and checkout work correctly, and find functional, UI, negative and edge-case defects across the seeded user types.

## 2. Scope
- **In scope:** login (all seeded users), inventory listing and sorting, product detail, cart, checkout (steps one, two, complete), logout, session/URL access control.
- **Out of scope:** load/performance benchmarking, security penetration testing, third-party footer links.

## 3. Approach
Functional, UI/visual, negative, boundary/edge and exploratory testing. `standard_user` is the baseline; `problem_user` and `performance_glitch_user` are compared against it. Selected cases are automated (Selenium + pytest); the rest are executed manually.

## 4. Environment and test data
- Browsers: Chrome (primary), Firefox, Edge; desktop 1920x1080 plus one responsive check at about 375px.
- Users (password `secret_sauce`): `standard_user`, `locked_out_user`, `problem_user`, `performance_glitch_user`, plus `error_user` and `visual_user` if listed on the login page.

## 5. Entry / exit criteria
- **Entry:** site reachable, test data available.
- **Exit:** all High-priority cases executed; no open Critical/High defects without a documented decision; at least 95% of cases executed.

## 6. Risks
Public shared demo that can change or reset without notice. Some behaviours are intentionally broken for the problem users, so baseline comparison with `standard_user` is needed to classify defects.

## 7. Deliverables
This plan, `test-cases.md`, bug reports (`docs/bug-reports/` and GitHub Issues), automation suite, execution summary.

## 8. Defect severity / priority
- **Severity:** Critical (blocks a core flow), Major (feature broken, workaround exists), Minor (cosmetic or low impact).
- **Priority:** High (fix first), Medium, Low.
