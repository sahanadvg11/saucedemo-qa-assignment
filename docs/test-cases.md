# Test Cases — SauceDemo

SU = `standard_user`, PW = `secret_sauce`. Preconditions: browser open on the login page unless stated.
"Auto" shows the automated test in `tests/ui/test_saucedemo.py`.

| ID | Title | Preconditions | Steps | Expected Result | Priority | Auto |
|---|---|---|---|---|---|---|
| TC01 | Valid login | None | Enter SU / PW, click Login | Redirected to `/inventory.html`, products shown | High | Yes |
| TC02 | Locked-out user | None | Login with locked_out_user / PW | Error "Epic sadface: Sorry, this user has been locked out."; stays on login | High | Yes |
| TC03 | Wrong password | None | SU / wrong password | Error "Username and password do not match any user in this service" | High | Yes |
| TC04 | Unknown username | None | Invalid user / PW | Same mismatch error | Med | Yes |
| TC05 | Empty username | None | Blank username, enter PW | Error "Username is required" | High | Yes |
| TC06 | Empty password | None | Enter SU, blank password | Error "Password is required" | High | Yes |
| TC07 | Both fields empty | None | Click Login | Error "Username is required" | Med | Yes |
| TC08 | Case sensitivity / spaces | None | Try `Standard_User`, then ` standard_user ` | Login rejected with mismatch error | Med | Partly |
| TC09 | Special characters / injection | None | Username `' OR 1=1 --`, `<script>alert(1)</script>` | Rejected, no script execution, no crash | Med | Partly |
| TC10 | Error banner dismissal | Error shown | Click X on banner | Banner closes, red field highlights clear | Low | No |
| TC11 | Direct URL without login | Logged out | Open `/inventory.html` | Redirect to login with "You can only access '/inventory.html' when you are logged in." | High | Yes |
| TC12 | Logout | Logged in as SU | Menu → Logout | Login page, fields empty | High | Yes |
| TC13 | Back button after logout | Just logged out | Press Back | Inventory not accessible | High | No |
| TC14 | performance_glitch_user login delay | None | Login with performance_glitch_user, time it | Login succeeds; delay noted vs SU | Med | No |
| TC15 | Listing content | Logged in as SU | Review inventory | 6 products, each with image, name, description, price, Add to cart | High | Partly |
| TC16 | Sort Name (A to Z) | Logged in as SU | Select option | Ascending alphabetical | High | Yes |
| TC17 | Sort Name (Z to A) | Logged in as SU | Select option | Descending alphabetical | Med | Yes |
| TC18 | Sort Price (low to high) | Logged in as SU | Select option | Ascending by price | High | Yes |
| TC19 | Sort Price (high to low) | Logged in as SU | Select option | Descending by price | Med | Yes |
| TC20 | Sort persistence | SU, sorted by price | Open product, go Back to products | Record whether sort is kept or reset | Low | No |
| TC21 | Product detail page | Logged in as SU | Click product name/image | Correct name, description, price, image; Back to products works | Med | No |
| TC22 | problem_user images and sorting | Logged in as problem_user | Review images, try each sort | Compare with SU; log defects | High | Yes (xfail) |
| TC23 | Add single item | Logged in as SU | Add to cart on one item | Button becomes Remove, badge shows 1 | High | Yes |
| TC24 | Add multiple items | Logged in as SU | Add 3 items | Badge 3; cart lists exactly those items with correct prices | High | Yes |
| TC25 | Remove from listing | Item in cart | Click Remove | Badge decrements/disappears; button reverts | High | Yes |
| TC26 | Remove from cart page | Items in cart | Open cart, Remove | Item removed, badge updated | High | Yes |
| TC27 | Cart persists across navigation | Items in cart | Detail page, refresh, return | Cart and badge unchanged | Med | Yes |
| TC28 | Continue Shopping | On cart page | Click Continue Shopping | Inventory with cart state preserved | Low | No |
| TC29 | problem_user add/remove | Logged in as problem_user | Add and remove items from listing | Compare with SU; log defects | High | No |
| TC30 | Happy path purchase | SU, item in cart | Cart → Checkout → valid info → Continue → Finish | "Thank you for your order!", cart emptied | High | Yes |
| TC31 | Empty first name | Checkout step one | Blank first name, Continue | "First Name is required" | High | Yes |
| TC32 | Empty last name | Checkout step one | Blank last name | "Last Name is required" | High | Yes |
| TC33 | Empty postal code | Checkout step one | Blank postal code | "Postal Code is required" | High | Yes |
| TC34 | Special characters / long input | Checkout step one | `<b>@#$%^&*</b>`, emojis, 256-char string | Handled safely; no layout break; record acceptance | Med | No |
| TC35 | Order overview totals | Items in cart | Reach step two | Item total = sum of prices; total = item total + tax (8%) | High | Yes |
| TC36 | Cancel at step one and two | In checkout | Click Cancel on each step | Returns to cart/inventory, items intact | Med | No |
| TC37 | Empty cart checkout | Empty cart | Open cart, click Checkout | Should be blocked or warned; if flow proceeds, log defect | High | Yes (xfail) |
| TC38 | Back button after payment | Order completed | Press Back | Cannot re-submit or see old checkout; cart empty | High | No |
| TC39 | Refresh / direct URL on complete page | Order completed | Refresh, or open `/checkout-complete.html` in new session | No duplicate order; redirect if not logged in | Med | No |
| TC40 | Back Home after order | On complete page | Click Back Home | Inventory, badge cleared | Low | No |
| TC41 | problem_user checkout | problem_user with item | Fill first, last, postal; Continue | Compare with SU; log defects | High | Yes (xfail) |
| TC42 | Reset App State | Items in cart | Menu → Reset App State | Cart emptied, buttons reset | Low | No |
