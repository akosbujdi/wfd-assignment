Feature: View All Orders
  As a Super Admin
  I want to view all orders
  So that I can monitor the sales and inventory

  Scenario: Successfully view all orders
    Given the Super Admin is logged in
    When they navigate to the "Order History" page
    Then they should see a list of all orders
    And each order should include the customer name, order date, total amount, and status
