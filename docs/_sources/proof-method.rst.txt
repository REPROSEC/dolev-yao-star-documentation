Proving Security Properties
===========================

The Proof
---------

* two independent parts of the proof:
  
  * trace invariants ==> security property
  * steps maintain invariants

.. include:: proof-labeling.rst

.. include:: proof-invariants.rst


Proof of Secrecy for Online? Protocol
-------------------------------------

* invariants + relevant changes to code (nonce label)

Proof of Responder Authentication for Online? Protocol
------------------------------------------------------

* introducing events
* one event per protocol step / per state
* state predicate refers to event predicate

Proving Security Properties for NSL
-----------------------------------

How To: Prove Security Properties in DY*
----------------------------------------
