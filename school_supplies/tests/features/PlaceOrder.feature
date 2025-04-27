Feature: Student placing an order
  As a student I want to place an order
  So that I can purchase items

  Scenario: Student places and order successfully
    Given the student is logged in
    And has items in their basket
    And is on the "Checkout" page
    When submits valid shipping and payment details
    And the user clicks the "Place Order" button
    Then an order should be created
    And the basket should be cleared