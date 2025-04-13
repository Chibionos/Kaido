# Sauce Demo Shopping Cart Test

This test performs a complete shopping flow on saucedemo.com including login, adding items to cart, and checkout.

## Test Steps

1. Navigate to saucedemo.com
2. Login with standard user credentials
   - Username: standard_user
   - Password: secret_sauce
3. Add multiple items to cart
   - Sauce Labs Backpack ($29.99)
   - Sauce Labs Bike Light ($9.99) 
   - Sauce Labs Bolt T-Shirt ($15.99)
4. View shopping cart
5. Proceed to checkout
6. Fill in checkout information
   - First Name: Test
   - Last Name: User
   - Zip Code: 12345
7. Complete checkout process
8. Verify successful order completion

## Expected Results
- Login should be successful
- Items should be added to cart correctly
- Cart total should reflect added items
- Checkout process should complete without errors
- Order confirmation page should be displayed
- "Thank you for your order" message should appear

## Notes
- Uses standard_user account which has full shopping capabilities
- Tests core e-commerce functionality including:
  - User authentication
  - Product selection
  - Cart management
  - Checkout flow
  - Order confirmation
