.. _sec-authentication:

Authentication
--------------

In contrast to secrecy properties,
authentication properties do not talk about attacker knowledge,
but about the order of things happening on the trace.
They are usually phrased as:

  If y happens,
  then x must have previously happend.

For example,
recall, the responder authentication property for the Online? protocol:

  If Alice at the end of a run believes,
  she talks with Bob,
  then this Bob must have been involved in the run,
  i.e., Bob must have previously sent an acknowledgement as response.

To state this property in DY*,
we use *events*,
which are a type of trace entries, that we did not discuss so far.
Inutitively, those entries log observable protocol actions.
Usually, we have one event for every protocol step to log
that the respective participant is executing the step.

For example, in the Online? protocol,
we will add one event for each of the three protocol steps:

* An "Initiating" event, that Alice triggers,
  when she starts a new run with some nonce :math:`n_A` and Bob.
* A "Responding" event, that Bob triggers, when he replies with an acknowledgement :math:`n_A` to Alice.
* A "Finishing" event, that Alice triggers, when she finishes a run with Bob and the nonce :math:`n_A`, i .e., when she receives the acknowledgement.
  
With these events,
we can then express responder authentication as:

  If Alice triggered a Finishing event,
  then Bob previously triggered a corresponding Responding event,
  as long as both Alice and Bob are honest.

As for secrecy,
the properties only talk about traces complying with the underlying protocol.

.. example:: Responder Authentication for the Online? protocol

   Responder Authentication for the Online? protocol is stated in DY* as the following Lemma:
   
   .. code::

     val responder_authentication:
       tr:trace -> ts:timestamp ->
       alice:principal -> bob:principal ->
       n_a:bytes ->
       Lemma
       (requires
          complies_with_online_protocol tr /\
          event_triggered_at tr ts alice (Finishing {alice; bob; n_a})
       )
       (ensures
          principal_is_corrupt tr alice \/ principal_is_corrupt tr bob \/
          event_triggered_before tr ts bob (Responding {alice; bob; n_a})
       )

.. exercise:: Responder Authentication for the NSL protocol

   Write down the responder authentication property for the NSL protocol as a Lemma.
   The textual description of the property is:

     If Alice at the end of a run believes to be talking with Bob,
     then this Bob must indeed be involved in the run.

   1. What events do we need to introduce to state the property?
      Give them speaking names and explain, what they should express/when they are triggered.

      .. toggle-answer::
         
         As for the Online? protocol,
         we add one event for every protocol step.
         That is, we have

         * an "Initiating" event,
           that Alice triggers, when she starts a new run with a nonce :math:`n_A` and Bob,
         * a "Responding to Message 1" event,
           that Bob triggers, when he replies to Alice with a second message containing
           the nonces :math:`n_A` and :math:`n_B`,
         * a "Responding to a Message 2" event,
           that Alice triggers, when seh replies to Bob with a third message containing the nonce :math:`n_B`, and
         * a "Finishing" event,
           that Bob triggers, when he receives the final third message from Alice.

   2. Using your events,
      describe the responder authentication property as a text.

      .. toggle-answer::
      
         If Alice triggers a "Responding to a Message 2" event,
         then Bob previously triggerd a corresponding "Responding to a Mesage 1" event,
         as long as both Alice and Bob are honest.

   3. Finally, express your property as an F* lemma.
      (You can again use ``complies_with_nsl`` as blackbox.)

      .. toggle-answer::

         .. code::

            val responder_authentication:
              tr:trace -> ts:timestamp ->
              alice:principal -> bob:principal -> n_a:bytes -> n_b:bytes ->
              Lemma
              (requires
                complies_with_nsl tr /\
                event_triggered_at tr ts alice (Responding2 {alice; bob; n_a; n_b})
              )
              (ensures
                principal_is_corrupt tr alice \/
                principal_is_corrupt tr bob \/
                event_triggered_before tr ts bob (Responding1 {alice; bob; n_a; n_b})
              )

.. exercise:: Initiator Authentication for the NSL protocol

   Write down the following initiator authentication property for the NSL protocol as an F* lemma:

     If Bob at the end of a run believes to be talking with Alice,
     then this Alice must indeed be involved in the run.

   .. toggle-answer::
     
      .. code::

         val initiator_authentication:
           tr:trace -> ts:timestamp ->
           alice:principal -> bob:principal -> n_a:bytes -> n_b:bytes ->
           Lemma
           (requires
             complies_with_nsl tr /\
             event_triggered_at tr ts bob (Finishing {alice; bob; n_a; n_b})
           )
           (ensures
             principal_is_corrupt tr alice \/
             principal_is_corrupt tr bob \/
             event_triggered_before tr ts alice (Responding2 {alice; bob; n_a; n_b})
           )

.. remember:: General Structure of Authentication Property

   Authentication properties in DY* usually look like the following:
           
   .. code::

      val bob_authentication:
        tr:trace -> ts:timestamp ->
        alice:principal -> bob:principal ->
        Lemma
        (requires
          complies_with_protocol tr /\
          event_triggered_at tr ts alice (Event2 alice bob ...)
        )
        (ensures
           principal_is_corrupt tr alice \/
           principal_is_corrupt tr bob \/
           event_triggered_before tr ts bob (Event1 alice bob ...)
        )
