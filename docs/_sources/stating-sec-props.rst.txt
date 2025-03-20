Stating Security Properties
===========================

In this chapter, we learn how to state security properties in DY* and what they mean.

In DY*, properties are expressed as properties on all traces complying with the protocol of interest.
As an example,
recall the intuitive description of the secrecy property for the Online? protocol from the `introduction<sec-intro-online>`:

  A nonce :math:`n_A` that Alice generates for (and sends to) some honest other party Bob,
  is only known to Alice and Bob.

.. 
  If Alice sends a nonce :math:`n_A` to some honest Bob,
  the nonce is only known to Alice and Bob.

In the trace-based view this is expressed as:

  For every trace complying with the Online? protocol,
  the attacker does not get to know the nonce :math:`n_A`
  that Alice generated for Bob,
  as long as both Alice and Bob are honest.

This raises the immediate questions:

1. How does the attacker get to know values?
2. What does it mean for participants to be honest?
3. How can we express that a trace complies with the protocol?

We answer the first two questions in this chapter,
by describing DY*'s `attacker model <sec-attacker-knowledge>`.
The detailed answer to the last question is deferred to the next chapter.
   
After these preliminaries,
we show how to formally state security properties in DY*
using the most common properties of
`secrecy <sec-secrecy>` and `authentication <sec-authentication>` as examples.


.. include:: sec-props-attacker-knowledge.rst

Now that we have a good intuition for security properties and the attacker capabilities,
we turn to formally stating the two most common security properties in DY*:
Secrecy and Authentication.
             
.. include:: sec-props-secrecy.rst
.. include:: sec-props-authentication.rst
.. include:: sec-props-howto.rst

