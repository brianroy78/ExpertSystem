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

## Features
 * If you want to emulate ruling out variables just set it to the empty option the variable
so multiples rules will be removed

## To Dos

* Store number values that can't be classified in a variable like the amount of electrical consumption
* convert to manageable/normalized variable name for later use in formulas
* Make the final conclusion downloadable from an endpoint
* Store the conclusions in the database linked to a client
* put and order to orphan vars
* Group var trees which share some children 
* Refactor code