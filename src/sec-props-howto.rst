How To: State Security Properties in DY*
----------------------------------------

.. howto:: Stating Security Properties in DY*

   * Security properties in DY* are *trace-based*
     and as such talk about traces that *comply* with the protocol of interest.
   
   * The attacker can read any message on the trace
     and contents of states he corrupted.
     From those values, he can build more terms with cryptographic functions.
     The *attacker knowledge* is the set of all terms the attacker can construct.

   * *Secrecy* properties talk about values
     that stay secret (unknown to the attacker)
     during runs of a protocol.
     They look like:

     .. code::

        val secrecy:
            tr:trace -> alice:principal -> bob:principal -> secret_value:bytes ->
            Lemma
            (requires
              complies_with_protocol tr /\
              ( (state_was_set_some_id tr alice (SomeState1 bob secret_value ...)) \/
                (state_was_set_some_id tr alice (SomeState2 bob secret_value ...)) \/
                ...
              ) /\
              attacker_knows tr secrect_value
            )
            (ensures principal_is_corrupt tr alice \/ principal_is_corrupt tr bob)


   * *Authentication* properties talk about a sequence of actions.
     They are expressed with *events*.
     We usually have one event per protocol step.
     The authentication property then looks like:

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

