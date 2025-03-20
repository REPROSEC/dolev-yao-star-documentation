
Communication Model
-------------------

In the Dolev-Yao model, sending and receiving of messages is asynchronous. A message from
:math:`A` to :math:`B` is not sent directly from :math:`A` to :math:`B`,
instead :math:`A` hands the message to the (delivery) network, who takes
care of delivering the message to :math:`B` at some later point. Think
of this in the same way a letter is delivered: If Alice sends a letter
to Bob, she puts the letter in a post box, handing it to the postal
service who delivers the letter to Bob’s letter box.

In this asynchronous model, the delivery network plays a central role in
scheduling the delivery of messages and delivering messages to their
intended receivers.

If we look at the descriptions of our example protocols in
:ref:`sec-intro_examples`, they are given as
a sequence of messages sent from one participant to another. But since
we use asynchronous communication in DY* we need to reformulate these
descriptions to match the communication model.

We split each communication via a message into two steps:
a send step and a *receive-react* step.

.. example:: Asynchronous Description of Two-Message Protocol

   A description of the Two-message protocol (see :ref:`sec-intro-TwoMessageP`)
   in the asynchronous communication model is as follows:

   #. *Initiate flow and send first message:*

      Alice generates a nonce
      :math:`n_A` and sends it together with her name to Bob

   #. *Receive first message and send second message:*

      Bob receives the
      nonce :math:`n_A` from Alice and sends it back to Alice

   #. *Receive last message:*

      Alice receives :math:`n_A` from Bob and
      finishes the protocol flow

.. example:: Asynchronous Description of Online? Protocol

   A description of the Online? protocol (see :ref:`sec-intro-online`) in the asynchronous
   communication model:

   #. *Initiate flow and send first message:*

      Alice generates a nonce
      :math:`n_A`, encrypts the nonce together with her name for Bob,
      and sends the message to Bob

   #. *Receive first message and send second message:*

      Bob receives the
      nonce :math:`n_A` from Alice, encrypts it for Alice and sends it
      back to Alice

   #. *Receive last message:*

      Alice receives :math:`n_A` from Bob and
      finishes the protocol flow

.. exercise:: Asynchronous Description of Needham-Schroeder Protocol
           
   Adapt the description of the Needham-Schroeder
   protocol from :ref:`sec-intro-NS` to
   match the asynchronous communication model.

   .. toggle-answer::

       #. *Initiate flow and send first message:*
          
          Alice generates a nonce
          :math:`n_A` and sends it (together with her name) encrypted for
          Bob

       #. *Receive first message and send second message:*

          Bob receives the
          nonce :math:`n_A` from Alice, generates a new nonce :math:`n_B`
          and sends both nonces encrypted for Alice

       #. *Receive second message and send third message:*

          Alice receives
          the two nonces :math:`n_A` and :math:`n_B` from Bob and sends back
          :math:`n_B` encrypted for Bob

       #. *Receive last message:*

          Bob receives :math:`n_B` and finishes the
          protocol flow
