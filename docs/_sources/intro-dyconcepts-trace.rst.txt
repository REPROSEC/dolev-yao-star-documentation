.. _sec-intro-trace:


The Global Trace
----------------

The overall state of the system, including all messages sent so far and
the states of participants across all parallel flows, are captured on
**the trace**, which is a log of observable protocol actions. The trace is
an ordered collection of **entries** of the following types:

-  **messages** sent between participants

-  **states** of participants

-  **events** logged by participants (for example, “Alice initiated a flow
   with Bob”)

-  generation of **random values** (for example, keys and nonces)

-  **corruption** (more on the attacker model and corruption later)

Since the trace acts as a log, entries can only be *appended* to the end
of the trace, but not removed from the trace or changed later on.

.. _ex-run-two-messagep :

.. example:: Trace of Run of Two-Message Protocol

   The trace after a successful run of the Two-Message protocol
   looks like this:
   
   .. code:: none

      1. Generate nonce n_A
      2. Message: Ping (Alice, n_A)
      3. Session 0 of Alice: SentPing n_A to Bob
      4. Message: Ack n_A
      5. Session 0 of Bob: SentAck n_A to Alice
      6. Session 0 of Alice: ReceivedAck n_A from Bob


.. example:: Key Setup for Online? Protocol

   The key setup phase for the Online? Protocol
   is captured on the trace like this:

   .. code:: none

      1. Generate private key k_A for Alice
      // Alice stores this private key
      2. Session 0 of Alice: Private Key k_A
         
      3. Generate private key k_B for Bob
      // Bob stores his private key
      4. Session 0 of Bob: Private Key k_B
         
      // Alice stores the public key of Bob
      5. Session 1 of Alice: Public Key pk_B of Bob
      // Bob stores the public key of Alice
      6. Session 1 of Bob: Public Key pk_A of Alice
         
         
Observe from the previous example,
that a trace entry only contains *one* action and not the complete global
state where relevant parts are updated.
In particular for states that means that
a trace entry contains only one state (:todo:`state vs session vs version: What terms to use?`),
and not the full state of a principal.
For example, in Step 5, Alice adds a new Session 1 to her state.
The corresponding trace entry captures only the new state,
and not the *full* state of Alice.
         
.. example:: Trace for Attack on Needham-Schroeder Protocol

   The beginning of the trace corresponding to the attack flow for the
   Needham-Schroeder protocol looks like this (simplified):

   .. code-block:: none
      
      // Setup Phase: Key generation and compromising Eve
      0.  Generate a private decryption key for Alice
      1.  Store the private key in Alice's state
      2.  + 3. Generate and store a private decryption key for Bob
      4.  + 5. Generate and store a private decryption key for Eve
      6.  Compromise the state session where Eve stores her private key
      7.  Store the public encryption key of Alice in Bob's state
      8.  Store the public encryption key of Bob in Eve's state
      9.  Store the public encryption key of Eve in Alice's state
      10. Compromise the state session where Eve stores Alice's encryption key

      // Actual Flow - Step 1: Alice starts a flow with Eve and sends a nonce $n_a$ encrypted to Eve
      11. Generate nonce n_a
      12. Event: Alice initiated flow with Eve using n_a
      13. Store (Eve, n_a) in Alice's state
      14. Generate a nonce n_pke used for encryption
      15. Message from Alice to Eve: encrypted (n_a, Alice) with Eve's key and used n_pke
      ...

   In the above trace part we see trace entries of all 5 types:

   * messages: entry 15,
   * states of participants: entries 1,3,5,7,8,9,13,
   * an event: entry 12,
   * generation of random values: entries 0,2,4,11,14, and
   * corruption: entries 6 and 10.

Sending and Receiving of Messages
.................................

Among other things, the trace is used as post and letter box for our
asynchronous communication model. To send a message, a new message entry
is added to the trace and receiving a message is just reading the
corresponding message entry. Delivery of the message by the postal
service corresponds to telling the receiver which message entry to read.
