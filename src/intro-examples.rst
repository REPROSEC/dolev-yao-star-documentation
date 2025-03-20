.. _sec-intro_examples:

Example Protocols
=================

.. _sec-intro-TwoMessageP:

Two-message Protocol
--------------------

In the two-message protocol (see Fig. :ref:`fig-2msg`), Alice generates a nonce :math:`n_A` and sends this nonce together with her name to Bob.
Bob then confirms that he received the message, by replying with the nonce :math:`n_A` he received.

.. _fig-2msg:
.. figure:: ../images/annex-flows/2msg_example_.*
    :width: 70%

    A simple Two Message Protocol


This very simple protocol does not guarantee any security properties, 
we will use it just as illustrating example for the first part of the tutorial.

The two-message protocol can be made a bit more secure by encrypting the messages for the corresponding recipients.
This is then called the Online? protocol.


.. _sec-intro-online:

Online?
-------

With the Online? protocol (see Fig. :ref:`fig-online`) Alice wants to figure out whether Bob is online.
She creates a nonce :math:`n_A` and sends it together with her name to Bob. This message is encrypted with Bob's public key.
If Bob is online and receives this message, he'll reply by sending back the nonce :math:`n_A` encrypted for Alice.

.. _fig-online:
.. figure:: ../images/annex-flows/online_example_.*
   :width: 70%

   The Online? Protocol

Using encryption gives us a one-sided *secrecy property*:
A nonce :math:`n_A` that Alice generates for (and sends to) some honest other party Bob,
is only known to Alice and Bob.

..
   If Alice sends a nonce :math:`n_A` to some honest other party Bob,




However, we don't have secrecy of a nonce that Bob receives,
i.e., it is not true that any nonce Bob receives from Alice,
is only known to Alice and Bob.
An attacker can do a MitM attack, sitting between Alice and Bob (see Fig. :ref:`fig-online-mitm`):

.. _fig-online-mitm:
.. figure:: ../images/annex-flows/online_example_mitm_.*
   :width: 70%

   A MitM attack on the Online? Protocol breaking Bob-sided secrecy

In this attack, Bob thinks that he is talking to Alice,
and hence that the nonce is only known to Alice and Bob.
However, the nonce is also known to the attacker Eve.

Note: The secrecy property from Alice's perspective is satisfied!
The property only talks about *honest* parties.
Intuitvely speaking:
If you send something willingly to the attacker (as Alice does in this case),
it is no longer a secret.

As a second property, we consider *responder authentication*:
If Alice at the end of a run believes,
she talks with Bob,
then this Bob must have been involved in the run,
i.e., Bob must have sent a response.

Note, that we don't have *initiator authentication*:
In the MitM attack,
Bob believes to be talking with Alice,
but instead he is talkin with Eve
and Alice is not involved in the run with Bob.

.. _sec-intro-NS:

Needham - Schroeder Protocol
-----------------------------

As a second example we consider the Needham-Schroeder (NS) protocol (see Fig. :ref:`fig-ns`) used to agree on a shared secret between two participants.

First, Alice creates a new nonce :math:`n_A` and sends it encrypted for Bob.
Now Bob also creates a new nonce :math:`n_B` and replies to Alice's message with both nonces :math:`n_A` and :math:`n_B`, encrypted for Alice.
Finally, Alice sends back :math:`n_B` encrypted to Bob.
The nonce :math:`n_B` can now be used as a shared secret between Alice and Bob.

.. _fig-ns:
.. figure:: ../images/annex-flows/ns_.*
   :width: 70%

   The NS protocol

We would like to have a secrecy property stating that :math:`n_B` is only known to Alice and Bob after a successful run of the NS protocol.
Unfortunately, there is a man-in-the-middle attack destroying the secrecy of :math:`n_B` (see Fig. :ref:`fig-ns-attack`).
   
Attack on NS Protocol
---------------------

.. _fig-ns-attack:
.. figure:: ../images/annex-flows/ns-attack_.*
   :width: 90%

   Attack on the NS Protocol

In this flow, Bob thinks he is talking with Alice and he doesn't notice anything wrong from his point of view,
but the nonce :math:`n_B` he generates (intended for Alice) leaks to Eve.

.. _sec-intro-NSL:

Needham - Schroeder - Lowe Protocol
-----------------------------------

The previous attack can be prevented by a small change to the protocol.
Instead of just sending the two nonces, Bob also sends his name.
This is then the Needham-Schroeder-Lowe (NSL) protocol (see Fig. :ref:`fig-nsl`):

Alice generates a nonce :math:`n_A` and sends it together with her name encrypted to Bob.
Bob then generates his own nonce :math:`n_B` and sends the two nonce :math:`n_A` and :math:`n_B` together with his name to Alice. This message is encrypted for Alice.
Finally, Alice sends the nonce :math:`n_B` back to Bob.

.. _fig-nsl:
.. figure:: ../images/annex-flows/nsl_.*
   :width: 70%

   The NSL protocol

The MitM attack is prevented, since Eve can not just forward Message 4 to Alice.
Alice expects to see Eve's name in there and not Bob.
So Alice would stop the protocol run at that point.
Note that Eve can not change the name in the message, since Bob sends this message encrypted *for Alice*.

Indeed, this protocol guarantees secrecy of both nonces :math:`n_A` and :math:`n_B`,
i.e., the attacker does not get to know the nonces as long as both Alice and Bob are honest.

Additionally,
the NSL protocol also provides *responder authentication*,
similar to the Online? protocol:
If Alice at the end of a run believes to be talking with Bob,
then this Bob must indeed be involved in the run.

The Online? protocol did not provide the reverse direction of
*initiator authentication*.
The NSL protocol does:
If Bob at the end of a run believes to be talking with Alice,
then this Alice must indeed be involved in the run.

.. _sec-intro-login:

Login
-----

Our final example is a simple registration and login protocol (just called Login protocol) shown in Fig. :ref:`fig-login`.
It has two phases: a registration and a login phase. 

.. _fig-login:
.. figure:: ../images/annex-flows/login_.*
   :width: 70%

   The Login Protocol


For registration, the client first chooses and stores a new password.
It then generates a nonce :math:`N_C` and sends a message containing the tag "42", the nonce :math:`N_C` and the password together with the name of the client.
This message is sent asymmetrically encrypted to the server.

The server now checks whether it already has a client with name :math:`C` and the password in its database.
If not, it creates a new account by storing the name and password, and a newly generated cookie.
It then replies with a message containing the tag "1337" and the string "ok".
This message is symmetrically encrypted with the nonce :math:`N_C`.
The client now knows that it has an account at the server and can log in.


For logging in, the client generates a new nonce :math:`N'_C` and sends a message containing the tag "42", the nonce :math:`N'_C` and the password together with its name.
If the server already has a client with the password in its database, it reads the corresponding cookie from the account
and replies with a message containing the tag "23" and the cookie.
This message is symmetrically encrypted with the nonce :math:`N'_C`.
The client stores the cookie and the protocol ends.

Note that the messages sent by the client (Message 2 and Message 6) are the same for registration and log in.
For registration the client chooses a new password and for log in it chooses some existing password.
The server expects only one type of message and can't immediately see whether this is a registration or a log in message.
To react correctly, it has to check the stored accounts.

For this protocol we want to show a secrecy property for the cookie from the server's point of view:
A cookie stored at the server is only known to the server and the client it was created for.


.. admonition:: Goals of the Course

   * Model and Implement the Two-Message protocol
   * Model and Implement the Online? protocol and show Alice-sided secrecy
   * Model and Implement the NS Protocol and the Attack of Lowe
   * Model and Implement the NSL Protocol and show the secrecy property
   * Model and Implement the Login Protocol and show the secrecy property
