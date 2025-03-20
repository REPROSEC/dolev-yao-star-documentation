A Model of the Online? Protocol
-------------------------------

Let us now turn to the Online? protocol and implement a protocol model in DY*.
The only difference to the Two-Message protocol is
that the messages are *encrypted* for the respective participants.
So the model of the Online? protocol will be very similar
to the previous one of the Two-Message protocol,
and we will here focus on the new differences.

First, we discuss how encryption is modelled in DY*.

Public Key Encryption in DY*
............................

.. _pke-key-storage-model:

Key storage
~~~~~~~~~~~

We don't model a PKI in DY*,
instead we just assume that every participant
has some private decryption keys and
some public encryption keys associated with other principals
in her state.
To easily access the keys,
we collect all private keys in one session
and all public keys in another session.
We already saw this, when we first introduced states
and in particular `sessions for global information<ex-online-global-sessions-for-keys>`.
So states look like this:

.. code:: none

   State Alice:
     Session 0: collection of private decryption keys
     Session 1: collection of public encryption keys
     ...


A participant may have several private keys
for different purposes.
Think of a protocol with several sub-protocols.
For each of the sub-protocols there could be
a separate private key which is only used for this sub-protocol.
All of those keys are stored in the same session (Session 0 in the example above).
To use the correct keys in the protocol steps,
we need to store the information which key is used for which purpose.
We do this, by tagging the keys.
That is, the collection of private keys
is a dictionary with the dictionary key being a tag
and the values are the keys.
So Session 0 in the above example could look like the following
(using the notation ``lookup_key = value``):

.. code:: none

   Session 0: {
       "SubProt1" = priv_key_for_sub_protocol_1
     , "SubProt2" = priv_key_for_sub_protocol_2
     , "Other" = priv_key_for_some_other_purpose
   }

Similarly, a participant may have several public encryption keys
for different purposes.
Additionally, for public keys there are different keys for different
other participants.
For example, Alice could have two public keys
specific to one of the sub-protocols,
one for Bob and one for Charlie.
Hence, to identify the correct key for encryption,
we now use the tag together with the name of the other participant.
Thus, the collection of public keys
is a dictionary with the dictionary key
being the pair of a tag and a participant name.
So Session 1 from above could look like the following:

.. code:: none

   Session 1: {
       ("SubProt1", Bob) = pub_key_for_Bob_for_sub_protocol_1
     , ("SubProt1", Charlie) = pub_key_for_Charlie_for_sub_protocol_1
     , ("SubProt2", Bob) = pub_key_for_Bob_for_sub_protocol_2
   }

In the above examples,
we used Session 0 to store Alice's private keys
and Session 1 for her public keys.
However, the sessions for the keys are not fixed
and can be allocated dynamically.
Usually this happens in a setup phase before any protocol run.

This setup is *not* part of the protocol *model* itself.
Just like protocol runs are not part of the protocol model,
but need to be implemented separately
(recall `the example run for the Two-Message protocol <sec-ex-run-two-message-implementation>`).
But since the protocol steps in the model
need to know where keys are stored
for de- and encryption,
we need to add these session IDs as additional arguments to the steps.
That is, for implementing a protocol step
in which you want to encrypt something,
you can assume that you get the session ID
of the state where public keys are stored
as an argument.
If you then want to implement an actual run of the protocol,
you need to generate those key sessions (and IDs) in a setup phase
and pass them on as arguments to the protocol steps in the run.
We will see how key setup works later,
when we implement an example run for the Online? protocol.

For now, it suffices to remember
that private and public keys are stored in separate sessions
at a principal
and that we use a tag to lookup a private key
and a tag participant pair to lookup a public key.
With this model of the key storage in mind,
we can now look at how encryption and decryption works in DY*.

Encryption
~~~~~~~~~~

If Alice wants to encrypt some plaintext for Bob,
she needs to lookup Bob's public key in her public keys session,
and use this key to encrypt the plaintext.

In ``DY.Simplified`` there is a function ``pke_enc_for`` that does those steps.
It takes as arguments:

* the participant that does the encryption
* the participant whose public key is used for encryption
* the session ID where the active participant stores her known public keys
* the tag of the key (used to lookup the right key in the public keys session)
* the abstract message

and returns the corresponding ciphertext in wire format.
The type is

.. code::

   val pke_enc_for:
     #a:Type -> {| parseable_serializeable bytes a |} ->
     (active: principal) -> (for: principal) ->
     (public_keys_sid: state_id) -> (key_tag: string) -> 
     (abstract_msg: a) -> 
     traceful (option (cipher: bytes))

The function fails if there is no key for the respective participant
with the given tag
stored in the given session of the active participant.

.. _ex-pke-encryption:

.. example:: Encrypting an abstract message

   The ``pke_enc_for`` function from ``DY.Simplified`` can be called like this:

   .. code::

      pke_enc_for #message_t alice bob alices_public_keys_sid key_tag (Ping {alice; n_a})


   Where Alice wants to encrypt the abstract Ping for Bob
   using ``key_tag`` as key to lookup the public key of Bob
   in her session with the ID ``alices_public_keys_sid``,
   where she stores her known public keys.


Decryption
~~~~~~~~~~

Decryption works very similar,
where the active participant now has to lookup her private key
in her private keys session.

Again, there is a function ``pke_dec_with_key_lookup`` in ``DY.Simplified``
for decryption.
It takes as arguments:

* the active (decrypting) participant
* the session ID, where the participant stores her private keys
* the tag of the key (used to lookup the right key in the private keys session)
* the ciphertext

and returns the corresponding abstract plaintext.
The type is:

.. code::

   val pke_dec_with_key_lookup:
     #a:Type -> {| parseable_serializeable bytes a |} ->
     principal -> 
     (private_keys_sid: state_id) -> (key_tag: string) ->
     (cipher: bytes) ->
     traceful (option (abstract_plain: a))

The function may fail if one of the following is true:

* there is no key with the given tag in the given keys session
* the ciphertext was not encrypted with the key
  corresponding to the given tag in the given keys session
* parsing of the decrypted plain text fails

.. _ex-pke-decryption:
  
.. example:: Decrypting a cipher text to an abstract message

   The ``pke_dec_with_key_lookup`` function from ``DY.Simplified`` can be called like this:
   
   .. code::
      
      pke_dec_with_key_lookup #message_t bob bobs_private_keys_sid key_tag cipher

   Here Bob wants to decrypt the ``cipher``
   using the key with tag ``key_tag`` stored in his session with ID ``bobs_private_keys_sid``.      

.. remember:: Public Key Encryption in DY*

   *Key Storage*:

   * .. toggle-header::
        :header: All private keys are stored in *one* session
                 as a dictionary with dictionary key being some tag.

        .. code:: none

           State Alice:
             Session 0: {
                 "SubProt1" = priv_key_for_sub_protocol_1
               , "SubProt2" = priv_key_for_sub_protocol_2
               , "Other" = priv_key_for_some_other_purpose
             }
   * .. toggle-header::
        :header: All public keys are stored in *one* session
                 as a dictionary with the dictionary key being a tag together with the name of a participant.

        .. code:: none

           State Alice:
             Session 1: {
                 ("SubProt1", Bob) = pub_key_for_sub_protocol_1_for_Bob
               , ("SubProt1", Charlie) = pub_key_for_sub_protocol_1_for_Charlie
               , ("SubProt2", Bob) = pub_key_for_sub_protocol_2_for_Bob
             }

   * The session IDs of the key sessions
     are generated in a setup phase outside of the protocol steps.
     Thus, the protocol steps take them as an extra argument.
             
   *Encryption*:

   * .. toggle-header::
        :header: using ``pke_enc_for`` from ``DY.Simplified``
                 
        .. code::

           let*? ping_encrypted = pke_enc_for #message_t alice bob alices_public_keys_sid key_tag (Ping {alice; n_a}) in
   * takes the abstract plain text and returns the cipher text in wire format (i.e., includes serializing)

   *Decryption*:

   * .. toggle-header::
        :header: using ``pke_dec_with_key_lookup`` from ``DY.Simplified``

        
        .. code::

           let*? ping_plain = pke_dec_with_key_lookup #message_t bob bobs_private_keys_sid key_tag cipher in

   * takes the cipher text in wire format and returns the abstract plain text (i.e., includes parsing)


With this, we can now implement the model of the Online? protocol.

Setup
.....

As for the `Two-Message protocol <model-twomessage-setup>`,
create a new folder ``Online`` and add

* .. toggle-header::
     :header: a ``Makefile``

     .. code:: Makefile

        TUTORIAL_HOME ?= ../..

        EXAMPLE_DIRS = path_to/Online

        include $(TUTORIAL_HOME)/Makefile
* .. toggle-header::
     :header: a ``DY.Online.Data`` module

      .. code::

         module DY.Online.Data

         open Comparse
         open DY.Core
         open DY.Lib

* .. toggle-header::
     :header: a ``DY.Online.Protocol`` module.

     .. code::

        module DY.Online.Protocol

        open Comparse
        open DY.Core
        open DY.Lib

        open DY.Simplified
        open DY.Extend

        open DY.Online.Data


The ``Data`` module
...................

The abstract message and state types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We begin the DY* model of the Online? protocol with the abstract message and state types
in the ``DY.Online.Data`` module.

Messages
^^^^^^^^

.. exercise:: Abstract message format

   Define the abstract format for the messages of the Online? protocol
   as records in DY*.

   .. toggle-answer::

      The messages of the Online? protocol have the same content
      as the messages in the Two-Message protocol.
      Hence, we have the same abstract format and
      can use the same records:

      .. code::

         type ping_t = {
           alice: principal;
           n_a : bytes;
         }

         type ack_t = {
           n_a : bytes;
         }

         type message_t =
           | Ping: (ping:ping_t) -> message_t
           | Ack:  (ack:ack_t) -> message_t

           
.. remember::

   The abstract format of messages only defines the *content* of the message.

   In particular, the following are *not* part of the abstract format:

   * the structure of the message (for example: Is it a pair? Is it a 3-tuple where the second component is a pair?)
   * whether the message (or parts of it) are encrypted


.. exercise:: Serializing and Parsing for the abstract message format

   Define serializer and parser for the abstract message format using Comparse.

   .. toggle-answer::

      Add :fstar:`[@@ with_bytes bytes]` to the record types and add
      
      .. code::

         %splice [ps_ping_t] (gen_parser (`ping_t))
         %splice [ps_ack_t] (gen_parser (`ack_t))
         %splice [ps_message_t] (gen_parser (`message_t))

         instance parseable_serializeable_bytes_message_t: parseable_serializeable bytes message_t =
           mk_parseable_serializeable ps_message_t

States
^^^^^^

.. exercise:: Abstract state format

   Completely define the abstract state format for states related to the Online? protocol.
   (You do not need to think about the states where keys are stored.)
   

   .. toggle-answer::

      Again, the content of the states of the Online? protocol
      are the same as the ones in the Two-Message protocol:

      .. code::

         // the record types for the individual states
         // and the combined state_t type
         
         [@@ with_bytes bytes]
         type sent_ping_t = {
           bob : principal;
           n_a : bytes;
         }

         [@@ with_bytes bytes]
         type sent_ack_t = {
           alice: principal;
           n_a : bytes;
         }

         [@@ with_bytes bytes]
         type received_ack_t = {
           bob : principal;
           n_a : bytes;
         }

         [@@ with_bytes bytes]
         type state_t = 
           | SentPing: (ping:sent_ping_t) -> state_t
           | SentAck: (ack:sent_ack_t) -> state_t
           | ReceivedAck: (rack:received_ack_t) -> state_t

         // serializing and parsing using Comparse
           
         %splice [ps_sent_ping_t] (gen_parser (`sent_ping_t))
         %splice [ps_sent_ack_t] (gen_parser (`sent_ack_t))
         %splice [ps_received_ack_t] (gen_parser (`received_ack_t))
         %splice [ps_state_t] (gen_parser (`state_t))

         instance parseable_serializeable_bytes_state_t: parseable_serializeable bytes state_t =
              mk_parseable_serializeable ps_state_t

         // the local_state instance
              
         instance local_state_state_t: local_state state_t = {
           tag = "Online.State";
           format = parseable_serializeable_bytes_state_t;
         }

Summary
^^^^^^^

The content of the messages and states of the Online? protocol
are the same as for the Two-Message protocol.
Hence, the definitions of the abstract formats are the same
and your ``DY.Online.Data`` module should now be the same
as the ``DY.TwoMessage.Data`` module
(except for the tag of the states in the ``local_state`` instance).

Preparation for Public Key Encryption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, we need a tag for the protocol related keys
used for public key en-/decryption of the messages.
We define this tag as a global constant also in the ``Data`` module.

For example:

.. code::

   let key_tag = "Online.Key"


This concludes the ``Data`` module and we can continue
with the implementation of the protocol steps.
   
The protocol steps
..................

Recall again,
that the only difference of the Two-Message and the Online? protocol
is that the messages are now encrypted for the respective participants.
For this, we use
the `encryption function<ex-pke-encryption>` :fstar:`pke_enc_for`
and the `decryption function<ex-pke-decryption>` ``pke_dec_with_key_lookup``.


Sending a Ping
~~~~~~~~~~~~~~

As a first attempt,
you might try to just copy the ``send_ping`` step from the model of the Two-Message protocol:

.. code-block::
   :linenos:
   :emphasize-lines: 8, 9

   val send_ping:
     (alice: principal) -> (bob: principal) ->
     traceful (state_id & timestamp)
   let send_ping alice bob =
     let* n_a = gen_rand in

     let ping = Ping {alice = alice; n_a = n_a} in 
     let ping_wire = serialize message_t ping in
     let* msg_ts = send_msg ping_wire in

     let ping_state = SentPing {bob = bob; n_a = n_a} in
     let* sid = start_new_session alice ping_state in

     return (sid, msg_ts)

Now that we want to encrypt the message before sending it in Line 9,
we need to adapt Line 8.
We want to call ``pke_enc_for`` here instead of the ``serialize``.

.. exercise:: Preparing the encryption

   What are the arguments to the call of ``pke_enc_for`` at this point?
   (Who wants to decrypt for who? Using what key?)

   .. toggle-answer::

      * ``alice``
      * ``bob``
      * some state ID of alice, where she stores public encryption keys
      * the key tag defined in the ``Data`` module
      * the abstract Ping message ``ping``

      So the call looks like this:
      
      .. code::

       pke_enc_for alice bob alice_public_keys_sid key_tag ping

We observe that the only "undefined" argument is
the session ID of the state where Alice stores her public encryption keys.
Recall from the `introduction of the key storage model <pke-key-storage-model>`,
that this session ID needs to be added as an extra argument to the protocol step.

.. exercise:: Adding the public key session ID as argument

   Add the key session ID where Alice stores her public keys
   as extra argument to the ``send_ping`` step.

   .. toggle-answer::
   
      .. code-block ::
         :linenos:
         :emphasize-lines: 2, 4

         val send_ping:
           (alice: principal) -> (alice_public_keys_sid: state_id) ->
           (bob: principal) -> traceful (state_id & timestamp)
         let send_ping alice alice_public_keys_sid bob =
           ...

Now, we want to call ``pke_enc_for`` in Line 8
and send the resulting cipher text in Line 9.
Since encryption is a monadic action,
we first need to think about the relevant monads
and which :fstar:`let` to use.

.. exercise:: Calling ``pke_enc_for`` in ``send_ping`` -- the Monads

   1. What monad is the ``pke_enc_for`` action in?
   2. What monad is the ``send_ping`` function in?
   3. What :fstar:`let` do we have to use in Line 8?

   .. toggle-answer::

      1. ``pke_enc_for`` is a ``traceful`` + ``option`` action
         (since it may fail, if there is not the right key in the provided session.)
      2. ``send_ping`` is a ``traceful`` function.
      3. None. We can not call ``pke_enc_for`` inside ``send_ping``,
         since it has more side effects.

Since we want to call ``pke_enc_for`` in the ``send_ping`` function,
we need to change the monad of ``send_ping`` to ``traceful`` + ``option``.

.. exercise:: Calling ``pke_enc_for`` in ``send_ping``

   1. Change the type of ``send_ping`` so that ``send_ping`` is a function in the ``traceful`` + ``option`` monad.
      
     .. toggle-answer::

      .. code::

           val send_ping:
             (alice: principal) -> (alice_public_keys_sid: state_id) -> (bob: principal) ->
             traceful (option (state_id & timestamp))
      
   2. Change Line 8 to use ``pke_enc_for``. What :fstar:`let` do we have to use?

      .. toggle-answer::

         Since we want the overall step to fail,
         if encryption fails, we use :fstar:`let*?` in Line 8:

         .. code::

            let*? ping_encrypted = pke_enc_for alice bob alice_public_keys_sid key_tag ping in

   3. Is there anything else we need to change in the ``send_ping`` function?

      .. toggle-answer::
      
         As we changed the monad of ``send_ping`` to ``traceful`` + ``option``,
         we now need to return an ``option``:

         .. code::

            return (Some (sid, msg_ts))
             

Putting everything together, the ``send_ping`` step for the Online? protocol looks like this
(highlighting the changes to the ``send_ping`` step from the Two-Message protocol):

.. code-block::
   :linenos:
   :emphasize-lines: 2-4,8,9, 14

   val send_ping:
     (alice: principal) -> (alice_public_keys_sid: state_id) -> (bob: principal) ->
     traceful (option (state_id & timestamp))
   let send_ping alice alice_public_keys_sid bob =
     let* n_a = gen_rand in

     let ping = Ping {alice = alice; n_a = n_a} in 
     let*? ping_encrypted = pke_enc_for alice bob alice_public_keys_sid key_tag ping in
     let* msg_ts = send_msg ping_encrypted in

     let ping_state = SentPing {bob = bob; n_a = n_a} in
     let* sid = start_new_session alice ping_state in

     return (Some (sid, msg_ts))

.. info:: Common Mistakes

  If you changed Line 8 to

  .. code::

     let*? ping_encrypted = pke_enc_for alice bob alice_public_keys_sid key_tag ping in

  and get the error

  .. code:: none

     - Expected type traceful (option (*?u8*) _)
       but
           ...
       has type traceful (state_id & timestamp)

  you probably forgot to

  * add ``option`` to the monad of ``send_ping``:
    
    .. code::

       val send_ping:
         (alice: principal) -> (alice_public_keys_sid: state_id) -> (bob: principal) ->
         traceful (option (state_id & timestamp))

  * or to return an ``option``:

    .. code:: 

       return (Some (sid, msg_ts))
       
Replying with an Ack
~~~~~~~~~~~~~~~~~~~~

As for ``send_ping``,
we will build the second protocol step for the Online? protocol
from the second step of the Two-Message protocol
and focus on the differences.

Start by copying the ``receive_ping_and_send_ack`` step from
``DY.TwoMessage.Protocol``:

.. code-block::
   :linenos:
   :emphasize-lines: 6, 14

   val receive_ping_and_send_ack:
      principal -> timestamp ->
      traceful (option (state_id & timestamp))
   let receive_ping_and_send_ack bob msg_ts =
     let*? msg = recv_msg msg_ts in 
     let*? png_ = return (parse message_t msg) in
     guard_tr (Ping? png_);*?

     let Ping png = png_ in
     let alice = png.alice in
     let n_a = png.n_a in

     let ack = Ack {n_a} in
     let* ack_ts = send_msg (serialize message_t ack) in

     let ack_state = SentAck {alice; n_a} in
     let* sess_id = start_new_session bob ack_state in

     return (Some (sess_id, ack_ts))

The main differences between the Online? and the Two-Message protocol are:

* the received Ping is encrypted and hence Bob needs to decrypt the message in Line 6
* the Ack needs to be encrypted for Alice in Line 14

Decrypting the Ping
^^^^^^^^^^^^^^^^^^^

We begin with decrypting the received message.
For this we want to use the `decryption function <ex-pke-decryption>` ``pke_dec_with_key_lookup``.

.. exercise:: Preparing the Decryption

   What are the arguments to the call of ``pke_dec_with_key_lookup``
   in Line 6?
   (Who wants to decrypt? Using what key?)

   .. toggle-answer::

      * ``bob``
      * some state ID of Bob, where he stores his private decryption keys
      * the key tag defined in the ``Data`` module
      * the wire-format ciphertext ``msg``

      So the call looks like this:

      .. code::

         pke_dec_with_key_lookup #message_t bob bob_private_keys_sid key_tag msg

Again, we currently don't have Bob's private key session ID available
and need to add it as extra argument to the protocol step.
So the type of the step changes to:

.. code::

   val receive_ping_and_send_ack:
     principal -> state_id -> timestamp ->
     traceful (option (state_id & timestamp))
   let receive_ping_and_send_ack bob bob_private_keys_sid msg_ts =
     ...

We are now ready to call the decryption function.

.. exercise:: Calling ``pke_dec_with_key_lookup`` in ``receive_ping_and_send_ack``

   1. Can we call ``pke_dec_with_key_lookup`` inside ``receive_ping_and_send_ack``?
      (Think about the relevant monads.)

      .. toggle-answer::
      
         Yes. Both the decryption action and the overall function are in the ``traceful`` + ``option`` monad.
      
   2. What :fstar:`let` do we need to use in Line 6?

      .. toggle-answer::
         
         Since we want the protocol step to fail,
         if decryption fails,
         we need to use :fstar:`let*?`.
      
   3. Change Line 6 accordingly.

      .. toggle-answer::

         .. code::

            let*? png_ = pke_dec_with_key_lookup #message_t bob private_keys_sid key_tag msg in

         Recall, that decryption includes parsing,
         so the returned ``png_`` is already in the abstract message format
         and we don't need to explicitly call ``parse``.

This concludes decryption of the received message to an abstract Ping message.

Encrypting the Ack
^^^^^^^^^^^^^^^^^^

Encrypting the Ack message works just like
encrypting the Ping in the first protocol step.

.. exercise:: Encrypting the Ack

   Change the step so that the Ack is encrypted for Alice.

   You may want to think about the following and adapt the model accordingly:
   
   1. What are the arguments for the encryption function?

      .. toggle-answer::
      
         * ``bob``
         * ``alice``
         * a session ID where Bob stores his public encryption keys
         * the key tag defined in the ``Data`` module
         * the abstract Ack ``ack``
      
   2. Does the type of the protocol step need to change?

      .. toggle-answer::
      
         Yes, we need to add the session ID for the public keys of Bob as extra argument:

         .. code::

            val receive_ping_and_send_ack:
              principal -> state_id -> state_id ->
              timestamp -> traceful (option (state_id & timestamp))
            let receive_ping_and_send_ack bob bob_private_keys_sid bob_public_keys_sid msg_ts =
              ... 
   3. Can we call the encryption function here and what :fstar:`let` should we use?

      .. toggle-answer::
      
         Yes, since both the encryption action and the overall protocol step are in the ``traceful`` + ``option`` monad.
         Since we want the whole step to fail, if encryption fails,
         we use :fstar:`let*?`.

         Line 14 changes to:

         .. code::

            let*? ack_encrypted = pke_enc_for bob alice bob_public_keys_sid key_tag ack in

Summary
^^^^^^^

To summarize, we

* used ``pke_dec_with_key_lookup`` for decrypting the received message
  (adding Bob's private keys session ID as extra argument to the step)
* used ``pke_enc_for`` to encrypt the Ack for Alice
  (adding Bob's public keys session ID as extra argument)

so that the final second protocol step now looks like this
(highlighting the changes to the second step of the Two-Message protocol):

.. code-block::
   :linenos:
   :emphasize-lines: 2, 4, 6, 14,15

   val receive_ping_and_send_ack:
     principal -> state_id -> state_id -> timestamp ->
     traceful (option (state_id & timestamp))
   let receive_ping_and_send_ack bob bob_private_keys_sid bob_public_keys_sid msg_ts =
     let*? msg = recv_msg msg_ts in
     let*? png_ = pke_dec_with_key_lookup #message_t bob bob_private_keys_sid key_tag msg in
     guard_tr (Ping? png_);*?

     let Ping png = png_ in
     let alice = png.alice in
     let n_a = png.n_a in

     let ack = Ack {n_a} in
     let*? ack_encrypted = pke_enc_for bob alice bob_public_keys_sid key_tag ack in
     let* ack_ts = send_msg ack_encrypted in

     let ack_state = SentAck {alice; n_a} in
     let* sess_id = start_new_session bob ack_state in

     return (Some (sess_id, ack_ts))

  
Receiving an Ack
~~~~~~~~~~~~~~~~

The final step of the Online? protocol
is again almost the same as the final step of the Two-Message protocol.
The only difference is,
that the received Ack is encrypted and needs to be decrypted by Alice.
This works in the same way as in the second step,
where Bob decrypts the Ping.
Looking back at the previous step,
you should be able to adapt the final step of the Two-Message protocol.

.. exercise:: Adapting ``receive_ack`` from the model of the Two-Message protocol

   Implement the final protocol step by adapting the ``receive_ack`` step from the model of the Two-Message protocol.

   You can follow these steps:
   
   1. Copy the ``receive_ack`` step from the model of the Two-Message protocol.
      Where do we need to perform decryption?

      .. toggle-answer::
      
         .. code-block::
            :linenos:
            :emphasize-lines: 6

            val receive_ack:
              principal -> timestamp ->
              traceful (option state_id)
            let receive_ack alice ack_ts =
              let*? msg = recv_msg ack_ts in
              let*? ack = return (parse message_t msg) in
              guard_tr (Ack? ack);*?

              let Ack ack = ack in
              let n_a = ack.n_a in

              let*? (sid, st) = lookup_state #state_t alice
                (fun st -> 
                      SentPing? st
                  && (SentPing?.ping st).n_a = n_a
                ) in
              guard_tr(SentPing? st);*?
              let bob = (SentPing?.ping st).bob in

              set_state alice sid (ReceivedAck {bob; n_a});*

              return (Some sid)      
   2. What are the arguments of the decryption function?

      .. toggle-answer::
      
         * ``alice``
         * the session ID where Alice stores her private decryption keys
         * the key tag defined in the ``Data`` module
         * the wire-format ciphertext ``msg``
      
   3. Does the type of the protocol step need to change?

      .. toggle-answer::
      
         Yes. We need to add the private keys session ID as extra argument:

         .. code::

            val receive_ack:
              principal -> state_id -> timestamp ->
              traceful (option state_id)
            let receive_ack alice alice_private_keys_sid ack_ts =
              ...

   4. Can we call the decryption function here and what :fstar:`let` should we use?

      .. toggle-answer::
      
         Yes. Since both decryption and the step are in the ``traceful`` + ``option`` monad.
         We use :fstar:`let*?`, as we want the whole step to fail if decryption fails.

         Line 6 changes to:

         .. code::

            let*? ack = pke_dec_with_key_lookup #message_t alice alice_private_keys_sid key_tag msg in

         We do not need to call parsing explicitly,
         as this is already part of decryption.

The final step of the Online? protocol looks like this
(highlighting the changes to ``receive_ack`` from the Two-Message protocol):

.. code-block::
   :linenos:
   :emphasize-lines: 2, 4, 6

   val receive_ack:
     principal -> state_id -> timestamp ->
     traceful (option state_id)
   let receive_ack alice alice_private_keys_sid ack_ts =
     let*? msg = recv_msg ack_ts in
     let*? ack = pke_dec_with_key_lookup #message_t alice alice_private_keys_sid key_tag msg in
     guard_tr (Ack? ack);*?

     let Ack ack = ack in
     let n_a = ack.n_a in
     
     let*? (sid, st) = lookup_state #state_t alice
       (fun st -> 
             SentPing? st
         && (SentPing?.ping st).n_a = n_a
       ) in
     guard_tr(SentPing? st);*?
     let bob = (SentPing?.ping st).bob in

     set_state alice sid (ReceivedAck {bob; n_a});*

     return (Some sid)

This concludes our model of the Online? protocol.
Which is very similar to the model of the Two-Message protocol,
with the new features of de- and encryption of messages.
     
An example protocol run
.......................

To check that our model works as expected,
we implement an example run,
where Alice sends a Ping to Bob,
Bob replies with an Ack
and Alice receives the Ack and checks that she started a run with the received nonce for Bob.

The general structure is the same as for the `Two-Message protocol <sec-ex-run-two-message-implementation>`:
we add a ``Run`` module in which we define a ``run`` function
where we call the protocol steps in the right order passing on arguments as needed
and finally print the trace.

But since we now use de- and encryption in the protocol steps,
we also need to take care of the key storage setup,
which will be our main focus in this section.

But first, let's setup the example run module.

The ``Run`` module
~~~~~~~~~~~~~~~~~~

.. exercise:: Setting up the ``Run`` module

   Follow the steps from `How-To: Modelling a Protocol <howto-modelling-protocols>`
   to add a new ``Run`` module,
   add the ``test`` target to the ``Makefile``,
   implement an (empty) ``run`` function that is called when executing the module
   and in which the current trace is printed.

   Try your setup by running ``make`` followed by ``make test``.
   
   .. toggle-answer::

      The ``Run`` module:

      .. code::

         module DY.Online.Run

         open DY.Core
         open DY.Lib
         open DY.Simplified

         open DY.Online.Data
         open DY.Online.Protocol

         let run () : traceful (option unit ) =
           let _ = IO.debug_print_string "************* Trace *************\n" in

           let* tr = get_trace in
           let _ = IO.debug_print_string (
               trace_to_string default_trace_to_string_printers tr
             ) in

           return (Some ())

         let _ = run () empty_trace


      Add to the ``Makefile``:

      .. code:: Makefile

         test:
                 cd $(TUTORIAL_HOME)/obj; $(FSTAR_EXE) --ocamlenv ocamlbuild -use-ocamlfind -pkg batteries -pkg fstar.lib DY_Online_Run.native
                 $(TUTORIAL_HOME)/obj/DY_Online_Run.native


      Running ``make`` followed by ``make test`` produces several lines on the terminal
      where the final line is:
      
      .. code:: none

         ************* Trace *************

Now that we have a working ``Run`` module,
we will populate the ``run`` function.
In the end, we want to call the protocol steps,
so we have to define all necessary arguments for those calls.
These arguments are

* the participants
* the key session IDs

For the participants, we define constants

.. code::

   let alice = "Alice" in
   let bob = "Bob" in

just as in the example run of the Two-Message protocol.

Let's now take a closer look at
how to setup the key storage for de- and encryption.

   
Setup of Key Storage
~~~~~~~~~~~~~~~~~~~~

Recall the layout of key storage at the participants from `before<pke-key-storage-model>`.
For our example run of the Online? protocol,
we want to have the following states after key storage setup:

.. code:: none

   State Alice:
     Session alice_private_keys_sid: {
       "Online.Key" = alice_private_key
     }
     Session alice_public_keys_sid: {
       ("Online.Key", Bob) = bob_public_key
     }

Alice has one private key and one public key for Bob for the Online? protocol in her state.
And similarly for Bob:
     
.. code:: none

   State Bob:
     Session bob_private_keys_sid: {
       "Online.Key" = bob_private_key
     }
     Session bob_public_keys_sid: {
       ("Online.Key", Alice) = alice_public_key
     }


To achieve these state layouts,
the setup consists of three phases for every participant:

1. Allocate sessions for the private and public keys.
2. Generate and store own private keys.
3. Retrieve and store public keys from other participants.
     
   
1. Allocating sessions for private and public keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
In the first initialization step,
we allocate new sessions at the participants
for the private and public keys.
These new sessions are initialized as empty dictionaries.

In ``DY.Lib`` there are ``initialize_*`` functions
that take as argument a participant
and return the new session ID where the keys are to be stored.
They are ``traceful`` functions that can not fail,
since they just add new sessions to the state.

.. example:: Allocate key sessions for Alice

   For the private keys session of Alice we use ``initialize_private_keys``:

   .. code::

     let* alice_private_keys_sid = initialize_private_keys alice in

   and for the public keys session we use ``initialize_pki``:

   .. code::

     let* alice_public_keys_sid = initialize_pki alice in

   After these initialization steps the state of Alice looks like this:

   .. code:: none

      State Alice:
        Session alice_private_keys_sid: { }
        Session alice_public_keys_sid: { }

   Alice has two new sessions, each containing an empty dictionary.

.. exercise:: Allocate key sessions for Bob

   Allocate new sessions for the private and public keys for Bob.

   .. toggle-answer::
   
      .. code::

         let* bob_private_keys_sid = initialize_private_keys bob in
         let* bob_public_keys_sid = initialize_pki bob in  
      
     
2. Generating and Storing private keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we know, *where* to store the private keys,
we can actually generate and store them.

In ``DY.Simplified`` there is a corresponding function:

.. code::
   
   val generate_private_pke_key:
     (alice: principal) -> (alice_private_keys_sid: state_id) -> (key_tag: string) ->
     traceful (option unit)

The function takes as arguments

* the participant to generate the private key for
* the session ID where the key should be stored, and
* the tag under which the key should be stored.

It generates a new key and stores it under the given tag in the provided session ID of the participant.
The step may fail,
if the session at the provided ID is not a private key dictionary.

:todo:`Explain why we use ;* and not ;*? here: It can fail but we don't do anything different if it does.`

.. example:: Generate private key for Alice

   To generate the private key for the Online? protocol for Alice,
   we use the session ID that we just created in step 1.
   and the key tag specified in the ``Data`` module:

   .. code::

      generate_private_pke_key alice alice_private_keys_sid key_tag;*

   After this step, the state of Alice looks like this:

   .. code:: none

       State Alice:
         Session alice_private_keys_sid: {
           "Online.Key" = alice_private_key
         }
         Session alice_public_keys_sid: { }
   

.. exercise:: Generate private key for Bob

   Generate a private key for the Online? protocol for Bob.

   .. toggle-answer::

      .. code::

         generate_private_pke_key bob bob_private_keys_sid key_tag;*
   

3. Retrieving and Storing public keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that both participants have a private key,
we want to store the corresponding public keys
at the other participant.

Again, there is a corresponding function in ``DY.Simplified``:

.. code::

   val install_public_pke_key:
     (alice: principal) -> (alice_public_keys_sid: state_id) ->
     (key_tag: string) ->
     (bob: principal) -> (bob_private_keys_sid: state_id) ->
     traceful (option unit)

Let's slowly go through the arguments of this function:

* ``alice`` is the participant who wants to store the public key
* ``alice_public_keys_sid`` is the session ID (of the public keys session),
  where Alice wants to store the key
* ``key_tag`` is the tag of the key used

  * as part of the lookup key in Alice's public keys session for the new key
  * to lookup the private key at Bob

* ``bob`` is the participant whose public key should be stored
* ``bob_private_keys_sid`` is the session ID of the private keys session of Bob,
  where he stores his private keys

A call to the function
     
.. code::

   install_public_pke_key alice alice_public_keys_sid key_tag bob bob_private_keys_sid


should be read as:

  ``alice`` wants to store in her public keys session (with ID ``alice_public_keys_sid``)
  under the lookup key pair ``(key_tag, bob)``
  the public key related to the private key
  that ``bob`` stores in his private keys session ``bob_private_keys_sid``
  under the same tag ``key_tag``.

.. example:: Storing Bob's public key at Alice

   Assume that after generation of the private keys,
   the states of Alice and Bob look like the following:
   
   .. code:: none

       State Alice:
         Session alice_private_keys_sid: {
           "Online.Key" = alice_private_key
         }
         Session alice_public_keys_sid: { }

       State Bob:
         Session bob_private_keys_sid: {
             "Online.Key" = bob_private_key
           , "Other.Key" = bob_other_private_key
         }
         Session bob_public_keys_sid: { }

   Alice has one private key for the Online? protocol,
   and Bob has two private keys: one for the Online? protocol
   and another one for some other protocol.

   If Alice wants to store the public key of Bob for the Online? protocol,
   she calls the ``install_public_pke_key`` function with the following arguments:

   .. code::
      
      install_public_pke_key alice alice_public_keys_sid "Online.Key" bob bob_private_keys_sid

   After this call, Alice has one entry in her public keys session:

   .. code:: none

      State Alice:
        Session alice_public_keys_sid: {
          ("Online.Key", Bob) = public key corresponding to bob_private_key
        }

You may ask yourself at this point,
what the value of the public key actually is and where it comes from.
After all, so far we only generated *private* keys.
At this point,
it is enough to know that the public key can be computed from the corresponding private key.
We don't need to care about how exactly that works.
Just remember:
A public key is identified by its corresponding private key.

.. reveal::
   :header: I want to know how it works.

   Since we are in the *symbolic* world,
   the public keys are actually just defined by adding
   a "public key of" constructor to the private key.
   That is,
   the public key corresponding to the private key ``private_key`` is
   :fstar:`Pk private_key`.


.. exercise:: Storing Alice's public key at Bob

   Store the public key of Alice at Bob.

   .. toggle-answer::

      .. code::

         install_public_pke_key bob bob_public_keys_sid key_tag alice alice_private_keys_sid;*

      Note that here we use the constant ``key_tag`` defined in the ``Data`` module,
      in contrast to the explicit string :fstar:`"Online.Key"` in the above example for Alice.
      Both is correct, but it is usually better to use the constants.
         
          
Summary of Key Storage Setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This concludes setup of the key storage
for our example run of the Online? protocol.
Your ``run`` function should look like the following:

.. code::

   let run () : traceful (option unit ) =
     let _ = IO.debug_print_string "************* Trace *************\n" in

     let alice = "Alice" in
     let bob = "Bob" in

     (*** key storage setup ***)

     let* alice_private_keys_sid = initialize_private_keys alice in
     let* alice_public_keys_sid = initialize_pki alice in

     let* bob_private_keys_sid = initialize_private_keys bob in
     let* bob_public_keys_sid = initialize_pki bob in  

     generate_private_pke_key alice alice_private_keys_sid key_tag;*
     generate_private_pke_key bob bob_private_keys_sid key_tag;*

     install_public_pke_key alice alice_public_keys_sid key_tag bob bob_private_keys_sid;*
     install_public_pke_key bob bob_public_keys_sid key_tag alice alice_private_keys_sid;*

     let* tr = get_trace in
     let _ = IO.debug_print_string (
         trace_to_string default_trace_to_string_printers tr
       ) in

     return (Some ())

If you run ``make`` followed by ``make test`` now,
you should see the following trace at the end of the output:

.. code:: none

   ************* Trace *************
   {"TraceID": 0, "Type": "Session", "SessionID": 0, "Principal": "Alice", "Tag": "DY.Lib.State.PrivateKeys", "Content": "[]"}
   {"TraceID": 1, "Type": "Session", "SessionID": 1, "Principal": "Alice", "Tag": "DY.Lib.State.PKI", "Content": "[]"}
   {"TraceID": 2, "Type": "Session", "SessionID": 0, "Principal": "Bob", "Tag": "DY.Lib.State.PrivateKeys", "Content": "[]"}
   {"TraceID": 3, "Type": "Session", "SessionID": 1, "Principal": "Bob", "Tag": "DY.Lib.State.PKI", "Content": "[]"}
   {"TraceID": 4, "Type": "Nonce", "Usage": {"Type": "PkeKey", "Tag": "Online.Key", "Data": "[Alice,]"}}
   {"TraceID": 5, "Type": "Session", "SessionID": 0, "Principal": "Alice", "Tag": "DY.Lib.State.PrivateKeys", "Content": "[Online.Key = (Nonce #4),]"}
   {"TraceID": 6, "Type": "Nonce", "Usage": {"Type": "PkeKey", "Tag": "Online.Key", "Data": "[Bob,]"}}
   {"TraceID": 7, "Type": "Session", "SessionID": 0, "Principal": "Bob", "Tag": "DY.Lib.State.PrivateKeys", "Content": "[Online.Key = (Nonce #6),]"}
   {"TraceID": 8, "Type": "Session", "SessionID": 1, "Principal": "Alice", "Tag": "DY.Lib.State.PKI", "Content": "[(Online.Key, Bob) = (Pk(sk=(Nonce #6))),]"}
   {"TraceID": 9, "Type": "Session", "SessionID": 1, "Principal": "Bob", "Tag": "DY.Lib.State.PKI", "Content": "[(Online.Key, Alice) = (Pk(sk=(Nonce #4))),]"}

.. info:: Hints for reading the trace output

   * Nonces are referred to by their creation time.
     As such we see ``Nonce #ts``, where ``ts`` is the timestamp of creation.
   * Dictionaries are represented as lists with entries ``key = value``.
   * Notation for a public key corresponding to a secret key is ``Pk (sk = the_private_key)``.

Let's look at the entries one by one:

* *Trace entries 0 - 3* correspond to initialization of the key sessions for Alice and Bob.
  Both get two empty dictionaries in Sessions 0 and 1 for private and public keys respectively.
* *Entries 4 + 5* show the generation (4) and storing (5) of Alice's private key.

  * Entry 4 reads: Created a new nonce that is to be used as private key with the tag "Online.Key" for Alice.
  * Entry 5 shows Session 0 of Alice, where the new key (the nonce generated in Step 4) is stored under the tag "Online.Key"

* *Entries 6 + 7* show the generation (6) and storing (7) of Bob's private key.
* *Entry 8* shows storing of Bob's public key in Alice's public key session (Session 1).
  The dictionary now contains one entry with the lookup key "Online.Key" and "Bob" 
  and the value is the public key corresponding to the nonce generated in Step 6, i.e., the private key of Bob.
* *Entry 9* shows storing of Alice's public key in Bob's public key session.

How-To: Setup Key Storage
~~~~~~~~~~~~~~~~~~~~~~~~~
     
We summarize the key setup for later reference:

.. howto:: Setup Key Storage

   1. Allocate sessions for the private and public keys:

      .. code::

         let* alice_private_keys_sid = initialize_private_keys alice in
         let* alice_public_keys_sid = initialize_pki alice in


   2. Generate and store own *private* keys:

      .. code::
         
         generate_private_pke_key alice alice_private_keys_sid key_tag;*

   3. Retrieve and store *public* keys from other participants:

      .. code::

         install_public_pke_key alice alice_public_keys_sid key_tag bob bob_private_keys_sid;*

      (Public keys are identified by their corresponding private key.)

The actual protocol run
~~~~~~~~~~~~~~~~~~~~~~~

We now have all things set up to call the protocol steps in the ``run`` function.

.. exercise:: Call the protocol steps

   In the ``run`` function, call the protocol steps corresponding to a run
   where Alice sends a Ping to Bob, Bob replies with an Ack, and Alice receives the Ack.

   Carefully think about the needed arguments,
   in particular the keys session IDs.

   .. toggle-answer::

      .. code::

         let*? (alice_sid, ping_ts) = send_ping alice bob alice_public_keys_sid in
         let*? (bob_sid, ack_ts) = receive_ping_and_send_ack bob bob_private_keys_sid bob_public_keys_sid ping_ts in
         receive_ack alice alice_private_keys_sid ack_ts;*?


Before calling ``make test``,
we again use a pretty printing function for the protocol messages and states:

* Download the ``DY.Online.Run.Printing.fst`` file from the `Tutorial Repo on GitHub <https://github.com/REPROSEC/dolev-yao-star-tutorial-code/blob/main/examples/Online/DY.Online.Run.Printing.fst>`_,
* import the module in your ``Run`` module and
* change the default printers to ``get_trace_to_string_printers``

so that printing is now:

.. code::

   let _ = IO.debug_print_string (
       trace_to_string get_trace_to_string_printers tr
    ) in


If you run ``make`` followed by ``make test`` now,
the output should end with the following trace
which is quite long and we will go through it line by line:

.. code:: none

   ************* Trace *************
   {"TraceID": 0, "Type": "Session", "SessionID": 0, "Principal": "Alice", "Tag": "DY.Lib.State.PrivateKeys", "Content": "[]"}
   {"TraceID": 1, "Type": "Session", "SessionID": 1, "Principal": "Alice", "Tag": "DY.Lib.State.PKI", "Content": "[]"}
   {"TraceID": 2, "Type": "Session", "SessionID": 0, "Principal": "Bob", "Tag": "DY.Lib.State.PrivateKeys", "Content": "[]"}
   {"TraceID": 3, "Type": "Session", "SessionID": 1, "Principal": "Bob", "Tag": "DY.Lib.State.PKI", "Content": "[]"}
   {"TraceID": 4, "Type": "Nonce", "Usage": {"Type": "PkeKey", "Tag": "Online.Key", "Data": "[Alice,]"}}
   {"TraceID": 5, "Type": "Session", "SessionID": 0, "Principal": "Alice", "Tag": "DY.Lib.State.PrivateKeys", "Content": "[Online.Key = (Nonce #4),]"}
   {"TraceID": 6, "Type": "Nonce", "Usage": {"Type": "PkeKey", "Tag": "Online.Key", "Data": "[Bob,]"}}
   {"TraceID": 7, "Type": "Session", "SessionID": 0, "Principal": "Bob", "Tag": "DY.Lib.State.PrivateKeys", "Content": "[Online.Key = (Nonce #6),]"}
   {"TraceID": 8, "Type": "Session", "SessionID": 1, "Principal": "Alice", "Tag": "DY.Lib.State.PKI", "Content": "[(Online.Key, Bob) = (Pk(sk=(Nonce #6))),]"}
   {"TraceID": 9, "Type": "Session", "SessionID": 1, "Principal": "Bob", "Tag": "DY.Lib.State.PKI", "Content": "[(Online.Key, Alice) = (Pk(sk=(Nonce #4))),]"}
   {"TraceID": 10, "Type": "Nonce", "Usage": {"Type": "NoUsage"}}
   {"TraceID": 11, "Type": "Nonce", "Usage": {"Type": "PkeNonce"}}
   {"TraceID": 12, "Type": "Message", "Content": "PkeEnc(pk=(Pk(sk=(Nonce #6))), nonce=(Nonce #11), msg=([Alice, [Nonce #10,]]))"}
   {"TraceID": 13, "Type": "Session", "SessionID": 2, "Principal": "Alice", "Tag": "Online.State", "Content": "SentPing [n_a = (Nonce #10), to = (Bob)]"}
   {"TraceID": 14, "Type": "Nonce", "Usage": {"Type": "PkeNonce"}}
   {"TraceID": 15, "Type": "Message", "Content": "PkeEnc(pk=(Pk(sk=(Nonce #4))), nonce=(Nonce #14), msg=( [Nonce #10,]))"}
   {"TraceID": 16, "Type": "Session", "SessionID": 2, "Principal": "Bob", "Tag": "Online.State", "Content": "SentAck [n_a = (Nonce #10), to = (Alice)]"}
   {"TraceID": 17, "Type": "Session", "SessionID": 2, "Principal": "Alice", "Tag": "Online.State", "Content": "ReceivedAck [n_a = (Nonce #10), from = (Bob)]"}


.. info:: Common Mistakes
   
   If you don't see a trace in your output,
   one of the steps fails.
   Move around the trace printing part (including ``get_trace``) and check which of the steps it is
   (the first one, for which you don't see a trace after ``make`` + ``make test``).
   Once you found the step, ask yourself:

   * Did you use the right arguments for that step?
   * Did you maybe swap private and public keys session IDs?

.. reveal::
   :header: A surprising Non-Mistake

   The run in the current ``run`` function
   will be successful (i.e., you'll see the correct trace)
   if you swapped Alice's keys session IDs for Bob's.
   For example, in the call to ``receive_ack`` you can use
   ``bob_private_keys_sid`` instead of ``alice_private_keys_sid``.

   Why is that possible?
   In the ``receive_ack`` step, Alice needs to decrypt the Ack
   and hence is looking for a key with the "Online.Key" tag in the provided session,
   which is now seemingly Bob's private key session.
   So apparently, Alice can decrypt a message encrypted for her using Bob's private key.
   Is there a bug in DY*'s decryption?

   .. toggle-answer::

      Of course there is no bug in DY*'s decryption!
      
      The misleading part in the above argument is
      that we don't provide sessions but session **IDs**.
      So Alice does not look for the key in Bob's private keys session,
      instead she looks in her own state at the provided session **ID**.
      Since both ``alice_private_keys_sid`` and ``bob_private_keys_sid`` are 0 in our run,
      she looks for the private key in her own Session 0 in both cases.

      *Lesson learned:*
      Session IDs are just numbers and a participant can only look at sessions in his own state.
      The same session ID may appear in the states of different participants,
      but probably with very different content related to it.

Let's now look at the trace entries:

* *Entries 0-9* show the key storage setup that we previously saw.
* *Entry 10 - 13* come from the first step of the protocol, where Alice generates a nonce :math:`n_A`
  and sends this nonce together with her name to Bob.

  * *Entry 10* shows the generation of the nonce :math:`n_A`
    :todo:`what to say about the usage/type? Ideally, I want to avoid talking about this. But it is needed for private key generation (and maybe PkeNonces)`
  * Let's now first look at *Entry 12*:

    .. code:: none

       {"TraceID": 12, "Type": "Message", "Content": "PkeEnc(pk=(Pk(sk=(Nonce #6))), nonce=(Nonce #11), msg=([Alice, [Nonce #10,]]))"}

    This is the encrypted message from Alice to Bob.

    * At the very end we see the plaintext ``msg=([Alice, [Nonce #10,]])``
      which is the message containing Alice's name and the nonce :math:`n_A` she generated at time 10.
    * In the beginning of the message content we see ``PkeEnc`` which means that the plaintext is encrypted.
    * The public encryption key that is used for this message,
      is given as we have seen previously: ``pk=(Pk(sk=(Nonce #6)))``.
      It is the public key corresponding to the private key that was generated at time 6.
      If we look at the entry at time 6, we see that this is (as expected) the private key of Bob.
    * We are left with the middle part ``nonce=(Nonce #11)``.
      :todo:`ideally i don't want to talk about this nonce (and hence entry 11) at all`

  * *Entry 13* shows that Alice creates a new session with ID 2 for the protocol status,
    where she stores that she sent the Ping :math:`n_A` (``Nonce #10``) to Bob.
  
* *Entries 14 - 16* come from the second protocol step,
  where Bob receives the Ping, and replies with an Ack.

  * *Entry 15* shows the encrypted Ack

    .. code:: none

       {"TraceID": 15, "Type": "Message", "Content": "PkeEnc(pk=(Pk(sk=(Nonce #4))), nonce=(Nonce #14), msg=( [Nonce #10,]))"}

    with

    * the plaintext ``msg=( [Nonce #10,])`` being the nonce generated at time 10
      (the nonce :math:`n_A`, Alice generated and sent to Bob in the Ping)
    * the encryption key ``pk=(Pk(sk=(Nonce #4)))`` being the public key related to the private key generated at time 4
      (which is, as expected, the private key of Alice)
    * the encryption nonce ``nonce=(Nonce #14)`` generated in the previous step (time 14)
      
  * *Entry 16* shows the new session that Bob creates in the step,
    where he stores
    that he sent the Ack :math:`n_A` (``Nonce #10``) to Alice.

* *Entry 17* shows the updated Session 2 of Alice, where she now stores
  that she received the Ack with :math:`n_A` (``Nonce #10``) from Bob.

So we see that our model of the Online? protocol
seems to be correct.
We can successfully model an example run,
where everything works as expected.
This concludes our model of the Online? protocol.
