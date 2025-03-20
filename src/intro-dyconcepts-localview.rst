
Global vs Local View on Protocols
---------------------------------

A second point where the intuitive description of a protocol differs
from the model in , is that the *order* of the protocol steps is *not*
part of the model. Whereas in :ref:`sec-intro_examples` we describe *one*
flow of a protocol with a fixed sequence of messages, in we want to
model arbitrarily *many*, possibly *interleaving* flows running in
parallel. For this we model each receive-react step from the previous
subsection separately, allowing steps to be executed at any time
(possibly in different flows).

Following this approach we need to think of how to identify flows and
keep track of their state. If we just had the receive-react steps of the
Needham-Schroeder protocol as in the previous subsection, we could, for
example, send several messages to Alice including two nonces, and Alice
would reply to all of those. However, this does not correctly model the
NS protocol. Alice should only react to such a message, if she
previously initiated a flow with one of the nonces. We resolve this
issue by tracking the state of protocol flows *locally* at every
participant. In our example, Alice would keep track of flows she
initiated and respond to a message with two nonces, only if she has a
corresponding ongoing flow.

This is in contrast to the intuitive description of protocols as in :ref:`sec-intro_examples`,
where the state of flows is tracked *globally* by the specified sequence of messages.

.. _example-twomessage-localview:

.. example:: Local View of Two-Message Protocol

   We adapt our description of the Two-message protocol from
   :ref:`sec-intro-TwoMessageP` to match the local
   view on the protocol used in DY*.

   To keep track of the state of protocol
   flows, we store successful completion of each step.
   We identify a flow

   * at the initiator by the nonce contained in the first message and
     the peer it is sent to, and
   * at the responder by the nonce received in
     the initial message and the peer it received the message from.

   With this we adapt the receive-react steps from the previous example as follows:
   
   -  *Initiate flow and send first message:*

      Alice generates a nonce
      :math:`n_A` and sends it together with her name to Bob.

      She stores that she initiated a flow with Bob using :math:`n_A`.

   -  *Receive first message and send second message:*

      Bob receives a message of the form :math:`(n_A, \text{Alice})`.
      He sends the nonce :math:`n_A` back to Alice.

      Bob stores that he received :math:`n_A` in a first message from Alice
      and replied.

   -  *Receive last message:*

      Alice receives a nonce :math:`n_A`.

      If she previously initiated a flow using :math:`n_A`, she
      stores that she received a response and finishes this
      protocol flow.

.. example:: Local View of Online? Protocol
      
   We get the local view description of the Online? protocol from
   :ref:`sec-intro-online` in the same
   way as for the two-message protocol.

.. _exercise-local-view-ns:

.. exercise:: Local View of Needham-Schroeder Protocol

   Adapt the description of the
   Needham-Schroeder protocol in :ref:`sec-intro-NS` to match the local
   view on the protocol used in .

   .. toggle-answer::
               
       To keep track of the state of protocol
       flows, we store successful completion of each step. We identify a
       flow at the initiator by the nonce contained in the first message and
       the peer it is sent to, and at the responder by the two nonces sent
       in response to the initial message.

       -  *Initiate flow and send first message:*

          Alice generates a nonce
          :math:`n_A` and sends it encrypted for Bob.

          She stores that she
          initiated a flow with Bob using :math:`n_A`.

       -  *Receive first message and send second message:*

          Bob receives a message of the form :math:`(n_A, \text{Alice})`.
          He generates a new nonce :math:`n_B`
          and sends both nonces encrypted for Alice.

          Bob stores that he
          received a first message from Alice and replied with :math:`n_A` and
          :math:`n_B`.

       -  *Receive second message and send third message:*

          Alice receives two nonces :math:`n_A` and :math:`n_B`.

          If she previously
          initiated a flow using :math:`n_A` with a corresponding Bob,
          she sends back
          :math:`n_B` encrypted for Bob and stores that she received two
          nonces and replied.

       -  *Receive last message:*

          Bob receives a nonce :math:`n_B`.

          If he previously
          received a first message and replied with :math:`n_B`, he finishes the
          protocol flow.

A key task when modeling protocols in the local view, is to figure out
what information is needed at each participant to continue with
subsequent steps.

For example, consider the “Initiate Flow” step above.
The first idea might have been to just store the nonce :math:`n_A` at
Alice. But, when she later receives the response, she needs to send the
third message with :math:`n_B` to someone. Recall that in the
asynchronous communication model, she does not get information about the
sender of the second message. So she can not directly reply. Thus, she
needs to store who she sent the initial message to, to now send the
third message to the same participant.

.. remember:: 

   A protocol model in DY*

   -  ... is split into several receive-react steps.

   -  ... does not contain information about the *order* of these steps.

   So don’t think of the *global* protocol flow as given in an intuitive
   description, but rather think of each receive-react step *locally* at
   each participant.

We will now take a closer look at the main concepts used in DY* for tracking
the state of protocol flows and sending and receiving of messages.
