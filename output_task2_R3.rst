===============
ECU_Requirement
===============

General Overview / Document Scope
*********************************

Document Scope
**************

.. sw_req::
   :Identifier: 629016
   :Attribute Type: Information

<put below a first description of the scope for ECU requirement
specification>

Document Specific Glossary
**************************

.. sw_req::
   :Identifier: 629013
   :Attribute Type: Information

<put below a definition of first glossary specific terms>

System Requirements
*******************

.. sw_req::
   :Identifier: 629017
   :Attribute Type: Information

<infos relevant for the complete chapter>
| Note to the template:
| \- the example requirements below are independent of each other and
are
| showing the different possibilities of the requirements structure

ECU 1st Requirement
*******************

.. sw_req::
   :Status: New/Changed
   :id: 629015
   :safety_level: asil a
   :artifact_type: MO_FUNC_REQ
   :crq: RQONE03587423

<description of the requirement in requirements language>
**VEHICLE_SYSTEM_BEHAVIOUR**
| <Optional: description of desired vehicle behaviour ("development
target")>
| **CONSTRAINT**
| <Optional: constraints on the solution space for the requirement>
|  **IMPACT**
| <Optional: description of possible cross-functional impact of the
requirement,
| or impact on other components>
|  **INFO**
| <Optional: additional informations about the requirement:
| \- know-how
| \- background
| \- HW dependencies related to the system requirement
| \- internal signals
| \- etc>
|  **ASSUMPTION**
| <Optional: assumptions on the requirement>

.. verify::

   Test Environment: Test Bench/Lab-car with hardware setup  Success
   Criteria: Verify whether the signal value is correct or not


System Non Functional Requirements
**********************************

.. sw_req::
   :Status: New/Changed
   :id: 629014
   :safety_level: asil b
   :artifact_type: MO_NON_FUNC_REQ
   :crq: RQONE03587423

<description of the non functional requirement in requirements language>

.. verify::

   Non Func Test Environment: Test Bench/Lab-car with hardware setup
   Success Criteria: Verify whether the signal value is correct or not


