Feature: Bulk discount for teachers
  As a teacher I want to receive a bulk discount on my order
  So that I can save money on my purchases

  Scenario: Teacher receives a discount on a bulk order
    Given the teacher is logged in
    And the teacher has more than 10 units of items in their basket
    When the teacher clicks the "Checkout" button
    Then a bulk discount of 15% should be applied