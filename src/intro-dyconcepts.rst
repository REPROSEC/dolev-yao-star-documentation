.. _`sec:main-concepts-dystar`:

Main Concepts in DY*
====================

.. include:: intro-dyconcepts-communicationmodel.rst
.. include:: intro-dyconcepts-localview.rst
.. include:: intro-dyconcepts-states.rst
.. include:: intro-dyconcepts-trace.rst

Capabilities of Honest Participants
-----------------------------------

Honest participants can read and write sessions of their own state, send
and receive messages, create events, and generate nonces.

Attacker Capabilities
---------------------

Recall that we consider a Dolev-Yao network attacker, who controls the
network (handling of messages) and can corrupt participants. In we model
this by specifying how the attacker can access the trace.

Messages
   The attacker can read all message entries on the trace. He also acts
   as the postal service delivering messages. Recall, that receiving a
   message is reading a specific message entry from the trace. The
   attacker chooses which message entry is to be read by whom at what
   point (if at all). He can also create and send messages on his own.

States
   The attacker can corrupt single sessions of a participant state by
   adding a corruption event to the trace. He can then read the content
   of all corrupted sessions.

From this information that the attacker can directly read off the trace,
he can also derive new information and use this to create own messages
or state sessions. For example, if he knows two values :math:`x` and
:math:`y` from some messages on the trace, he can produce a new message
containing both values. We give full details on deriving new values
later, for now the intuition that the attacker can do anything an honest
participant can do with information he knows, should suffice. Most
notably, no one (not even the attacker) can break cryptography. For
example, if the attacker sees a message that is encrypted with some key
that the attacker doesn’t know, he can’t access the plain text of the
message.

..
   NS Example
   ^^^^^^^^^^

   -  steps

   -  protocol flow consisting of the steps

   -  trace output of successful run

   -  attack on protocol

   -  show trace

Stating Security Properties
---------------------------

Our security properties are trace-based properties and talk about all
traces that follow the protocol specification. For example, secrecy
properties are often of the form “In any trace following the protocol
specification, a secret value between Alice and Bob is not known to the
attacker, if neither Alice nor Bob are corrupted.”

.. example:: Secrecy Property for NSL

   For the NSL protocol we want to show secrecy of the shared secret key
   :math:`n_B`. The property is stated in in the following simplified
   form:

   For all traces following the protocol specification and all values
   :math:`n_B` the following holds: if Bob finishes a flow with Alice
   and :math:`n_B`, then the attacker does not know :math:`n_B` or one
   of Alice and Bob is corrupted.

In
`[chap:labelingsystem,chap:proofmethod] <#chap:labelingsystem,chap:proofmethod>`__,
we give more details on security properties in DY* and in particular, how to state that a trace follows the protocol specification.
