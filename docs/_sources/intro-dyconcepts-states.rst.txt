.. _sec-intro-states:

States
------

To store information locally, every participant has a *state*.
This state consists of several *sessions*
that contain some information.

In the simplest case,
one session in a state corresponds to
one run of a protocol.

.. _ex-states-twomessage:

.. example:: States in *one* run of the Two-Message Protocol

   We look at the states of Alice and Bob
   in one run of the Two-Message protocol.

   When Alice initiated a run her state looks like this:

   .. code:: none

      State Alice:
        Session 0: SentPing n_A to Bob

   There is one session where she stores the status of the protocol
   run.
   Here she stores that she initiated a run
   with Bob sending the nonce :math:`n_A`.

   When Bob received such a ping and replied, his state looks like this:

   .. code:: none
             
      State Bob:
        Session 0: SentAck n_A to Alice

   He also has one session for keeping track of the protocol status.

   Finally, when Alice received the Ack of Bob, her state changes to:

   .. code:: none
             
      State Alice:
        Session 0: ReceivedAck n_A from Bob

   In this case, Alice considers Session 0 to be finished.


To illustrate the concept of
one session per run at each participant even more,
we look at a slightly more complex example,
where we consider several *interleaving* runs
of the Two-Message protocol.
   
.. example:: States in *interleaving* runs of the Two-Message Protocol

   Alice, Bob and Charlie are running several runs
   of the Two-Message Protocol in parallel.
   These runs are stored in different sessions in their states.

   At some point, their states could look like this:

   .. code:: none

      State Alice:
        Session 0: ReceivedAck n_A1 from Bob
        Session 1: SentPing n_A2 to Bob
        Session 2: SentPing n_A3 to Charlie

      State Bob:
        Session 0: SentPing n_B1 to Charlie
        Session 1: SentAck n_A1 to Alice

      State Charlie:
        Session 0: SentAck n_A3 to Alice
        Session 1: SentAck n_B1 to Bob

   At this point, we have the following situation:

   * Alice has 3 ongoing runs of the protocol:

     * in Session 0 she finished a run with Bob
     * in Sessions 1 and 2, she initiated two more runs
       with Bob and Charlie resp.
   * Bob has 2 ongoing runs:

     * in Session 0 he initiated a run with Charlie
     * in Session 1 he replied to Alice
       (this corresponds to Alice's Session 0
       since they are both identified by the nonce :math:`n_{A1}`)
   * Charlie has also 2 ongoing runs:

     * in Session 0 he replied to Alice 
       (which in turn correspond to
       Alice's Session 2 (:math:`n_{A3}`))
     * in Session 1 he replied to Bob
       (corresponding to Bob's Session 0 (:math:`n_{B1}`))


       
In the simple Two-Message protocol,
we only have sessions keeping track of protocol runs.
However, sessions can also be used to store
global information at a participant that is independent of
the individual protocol runs.
Such global information are for example
private keys for decryption and public encryption keys.
We see this in the Online? protocol:

.. _ex-online-global-sessions-for-keys:

.. example:: Sessions with global Information in the Online? Protocol

   After the first step of one run of the Online? protocol,
   Alice's state looks like this:

   .. code:: none

      State Alice:
        Session 0: private decryption key k_A
        Session 1: public encryption key pk_B of Bob
        Session 2: SentPing n_A to Bob


   We see, that Session 2 is the session keeping track of the
   protocol run. Just as in the previous examples for the Two-Message protocol.

   New are the first two sessions that now store some global information:
   Session 0 contains Alice's private decryption key :math:`k_A`
   and Session 1 a public encryption key :math:`k_B` for Bob.

   The state of Bob at the same time (before receiving the first message from Alice) is:

   .. code:: none

      State Bob:
        Session 0: private decryption key k_B
        Session 1: public encryption key pk_A of Alice

   He just stores his private key and the public key of Alice.

To keep track of the current state of a protocol run,
participants need to be able to *update* existing sessions.
Consider the previous example:
When Alice receives the Ack from Bob,
she needs to update her Session 2 to store this progress in the run.

On the other hand, participants must also be able to *create* new sessions.
Again, in the previous example, we see that Bob
does not yet have any session for the started run.
Once he receives the Ping from Alice and replies with an Ack,
he needs to store the progress of the run.
So he must be able to create a new session.

And indeed, these are the two operations on session that are available:

* add a new session to a state
* update an existing session

Comparing the different sessions for protocol runs and global information
in terms of how often they are upated,
we observe,
that we update protocol sessions frequently,
usually after every protocol step of the participant.
In contrast, the sessions containing global information
are mostly set up at the very beginning and don't change after that.

This intuition of one session per protocol run that is updated after every protocol step and some sessions for global information that are only set up in the beginning is sufficient for now.


.. remember:: 

   A session in a state of a principal can store
   
   * global information like private or public keys
   * the current state of a protocol run

   New sessions can be added to a state
   and existing sessions can be updated.
     
You should now be able to explain how the states of Alice and Bob look like in a run of the Needham-Schroeder protocol:

.. _ex-states-ns:

.. exercise:: States in the Needham-Schroeder Protocol

   How do the states of Alice and Bob look like in a run of the Needham-Shroeder
   protocol?
   
   Show them at the beginning of the run, and after each protocol step.
   Look back at :ref:`Exercise: Local View of Needham-Shroeder<exercise-local-view-ns>` to recall the information that needs to be stored in the states.

   .. toggle-answer::

      The initial states of Alice and Bob
      before the run begins,
      just contain the corresponding private and public keys:

      .. code:: none

         State Alice:
           Session 0: private decryption key k_A
           Session 1: public encryption key pk_B of Bob

         State Bob:
           Session 0: private decryption key k_B
           Session 1: public encryption key pk_A of Alice


      After Alice started the run,
      she adds a new session for the state of this run:

      .. code:: none

         State Alice:
           ...
           Session 2: SentMsg1 n_A to Bob

      When Bob replied to this 1st message,
      he also creates a new session:

      .. code:: none

         State Bob:
           ...
           Session 2: SentMsg2 (n_A, n_B) to Alice

      When Alice receives this response and
      in turn responded with the last message,
      she updates Session 2:

      .. code:: none

         State Alice:
           ...
           Session 2: The run for (n_A, n_B) with Bob has finished
             and I sent Msg3 n_b to Bob

      And finally, after Bob received this message,
      he also updates his session for this run:

      .. code:: none

         State Bob:
           ...
           Session 2: The run for (n_A, n_B) with Alice has finished
             as I received Msg3 (n_B) from Alice
