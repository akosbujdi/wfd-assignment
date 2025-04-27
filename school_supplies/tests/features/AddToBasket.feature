Feature: Add item to basket
   As a student I want to add items to my basket
   So that I can purchase them

  Scenario: Add an available item to the basket
    Given the student is logged in
    And is on the "Items" page
    When the user selects quantity "3" for item "Pencil"
    And clicks the "Add to Basket" button
    Then the item "Pencil" with quantity "3" should be added to the basket