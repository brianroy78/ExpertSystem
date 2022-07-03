# Expert System

## Glossary
* Rule: Has Premises and Conclusion
* Premise: It is a hypothetical fact that can be true or false depending on the users responses or other conclusions.
* Conclusion: It is a hypothetical fact that can be true or false depending if the premises are met.
* Fact: It's a true event depending on the users's input ot triggered rules

## Functionality
 * This is an Expert System for Quoting Solar Panels
 * Is Base on Rules
 * Options
   * Also called Premises
   * The Premises are linked with the AND behavior in the rules
 * Variable:
   * A Variable has multiples options
   * All variables have the empty option
   * Variables support scalar values, just set the is_scalar = True
   * If is_scalar is set to True and the given value is different from EMPTY, the value of the option will be replaced with the given value.
 * Rule
   * If all the values match with the given ones the conclusions becomes facts
   * A rule could trigger multiple facts
   * If a given value contradicts a premise the rule is removed
   * A rule can be a formula
   * if a rule is a formula, it only conclude one variable
 * The inference's steps are stored in a dictionary of lists, so It's possible to go backwards

## Features
 * If you want to emulate ruling out variables just set it to the empty option the variable
so multiples rules will be removed

## To Dos

* Make the final conclusion downloadable from an endpoint
* Store the selected devices in the database linked to a client
* put and order to orphan vars
* Group var trees which share some children 
* Refactor code
* Create an endpoint to remove a cached inference
* Create a class group of deduction and a function that interprets them, since it starts to take a lot of code to do so
* Create and endpoint that shows an overview of a quotation
* make possible to store a scalar value in the option table