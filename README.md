# SauceDemo QA Assignment

[![CI](https://github.com/sahanadvg11/saucedemo-qa-assignment/actions/workflows/ci.yml/badge.svg)](https://github.com/sahanadvg11/saucedemo-qa-assignment/actions/workflows/ci.yml)

Manual test design, bug reports, UI automation (Selenium + pytest) and API tests (requests + pytest) for
[SauceDemo](https://www.saucedemo.com) and [ReqRes](https://reqres.in).

| Part | Deliverable | Location |
|---|---|---|
| 1 | Test plan and 42 test cases | [`docs/test-plan.md`](docs/test-plan.md), [`docs/test-cases.md`](docs/test-cases.md) |
| 2 | Bug reports, GitHub Issues, Project board | [`docs/bug-reports/`](docs/bug-reports), [Issues](../../issues), [Project board](../../projects) |
| 3 | UI automation (Selenium, 25+ tests) | [`tests/ui/`](tests/ui) |
| 4 | API tests with status and body-shape assertions | [`tests/api/`](tests/api) |
| Bonus | GitHub Actions CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |

## Run it

Requirements: Python 3.10+ and Google Chrome (Selenium Manager downloads the matching driver automatically).

```bash
pip install -r requirements.txt
export REQRES_API_KEY=<your free key from https://app.reqres.in>   # needed for API tests only
pytest
```

- UI only: `pytest -m ui`  |  API only: `pytest -m api`
- Watch the browser: `HEADED=1 pytest -m ui`
- Failure screenshots are saved to `artifacts/`.

> reqres.in now requires an `x-api-key` header on every request. Without `REQRES_API_KEY`, the API tests are skipped with a clear reason (they do not fail silently). In CI, add the key as a repository secret named `REQRES_API_KEY`.

## What the UI tests cover (`tests/ui/test_saucedemo.py`)

| Test | Manual case | Covers |
|---|---|---|
| `test_tc01_valid_login` | TC01 | Login success, 6 products shown |
| `test_tc02_locked_out_user` | TC02 | Locked-out error message |
| `test_login_negative` (7 params) | TC03-TC09 | Wrong password, unknown user, empty fields, case sensitivity, injection characters |
| `test_tc11_direct_url_requires_login` | TC11 | Access control on direct URL |
| `test_tc12_logout` | TC12 | Logout returns to login |
| `test_tc16`-`test_tc19` | TC16-TC19 | All four sort options |
| `test_tc23_24_add_items_updates_badge_and_cart` | TC23/24 | Badge and cart contents |
| `test_tc25_remove_from_listing` | TC25 | Remove from listing |
| `test_tc26_remove_from_cart_page` | TC26 | Remove from cart page |
| `test_tc27_cart_persists_after_refresh` | TC27 | Cart persistence |
| `test_tc30_happy_path_purchase` | TC30 | End-to-end purchase |
| `test_checkout_required_fields` (3 params) | TC31-TC33 | Required-field validation |
| `test_tc35_order_total_math` | TC35 | Subtotal, 8% tax and total arithmetic |
| `test_tc37_empty_cart_checkout_is_blocked` | TC37 | **xfail**: documents BUG-006 |
| `test_tc22_problem_user_sort_works` | TC22 | **xfail**: documents BUG-002 |
| `test_tc41_problem_user_checkout_last_name` | TC41 | **xfail**: documents BUG-004 |

`xfail` tests assert the *correct* behaviour, so they are reported as "expected failures" while the bug exists and will show XPASS once it is fixed.

## What the API tests cover (`tests/api/test_reqres.py`)

- **GET:** list users (pagination keys, per-user field types), single user, 404 for a missing user and unknown resource.
- **POST:** create user (201, echoed fields, `id`, `createdAt`), login (token), register (id and token).
- **Invalid or missing data:** login without password / email, register without password, register with undefined user (all 400 with the exact `error` message).
- **PUT / DELETE:** update (`updatedAt`), delete (204, empty body).
- **Auth gate:** request without an API key is rejected (401/403).

## Bugs found

See [`docs/bug-reports/`](docs/bug-reports) and the Issues tab. Board: Todo / In Progress / Done.
