Intro
===

* general intro on symbolic formal securtiy analysis of protocols
* example protocols:
  * Two-message
  * Online?
  * NS + NSL
  * Login
* main concepts
  * communicaiton model
  * global vs local view on protocols
  * states
  * trace
  * attacker
  * maybe something on stating security properties ?
* How To: Prepare Protocols Model for DY*

Modelling Protocols
===

* wire-format and abstract formats for messages and sessions
* traceful monad

* Implementation of 2-Message
* Implementation of Online?
* Example Protocol run of NSL with trace printing
* A First Implementation of NSL 
  * (without Events)


* How To: Model a Protocol in DY*
  * abstract message and state types
  * types of protocol steps
  * general structure of one step


Stating Security Properties
===

* trace-based
* only for "valid" traces
* give example of abstract NSL Security properties

* labeling system
* Attacker model (corruption)

Proving Security Properties -- Proof Method
===

* invariants

