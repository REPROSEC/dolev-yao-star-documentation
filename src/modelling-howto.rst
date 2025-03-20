How To: Modelling a Protocol in DY*
-----------------------------------

Before we continue to model the next protocol,
let's summarize how we build a model of a protocol in DY*
using our model of the Two-Message protocol as an example.

.. _howto-modelling-protocols:

.. howto:: Modelling a Protocol in DY*

   *Technical Setup:*

   * create a new folder
   * .. toggle-header::
        :header: add a ``Makefile``

        .. code:: Makefile

           TUTORIAL_HOME ?= ../..

           EXAMPLE_DIRS = path_to/TwoMessageP

           include $(TUTORIAL_HOME)/Makefile

                 
   * .. toggle-header::
        :header: create two modules: ``Data.fst`` and ``Protocol.fst``

        .. code::

           module DY.TwoMessage.Data

           open Comparse
           open DY.Core
           open DY.Lib


        .. code::

           module DY.TwoMessage.Protocol

           open Comparse
           open DY.Core
           open DY.Lib

           open DY.Simplified
           open DY.Extend

           open DY.TwoMessage.Data


           
   *Define abstract message and state formats:*

   * The abstract formats for messages and states go into the ``Data`` module.
   * .. toggle-header::
        :header: For each message and state in the protocol,
                 define its own type as a record.

        .. code::

           type ping_t = {
             alice: principal;
             n_a : bytes;
           }

           type ack_t = {
             n_a : bytes;
           }

        .. code::

            type sent_ping_t = {
              bob : principal;
              n_a : bytes;
            }

            type sent_ack_t = {
              alice: principal;
              n_a : bytes;
            }

            type received_ack_t = {
              bob : principal;
              n_a : bytes;
            }

           
   * .. toggle-header::
        :header: Collect the individual record types for messages and states in an overall type ``message_t`` and ``state_t``
                using constructors for each of the cases.

        .. code::

           type message_t =
             | Ping: (ping:ping_t) -> message_t
             | Ack:  (ack:ack_t) -> message_t


        .. code::

            type state_t = 
              | SentPing: (ping:sent_ping_t) -> state_t
              | SentAck: (ack:sent_ack_t) -> state_t
              | ReceivedAck: (rack:received_ack_t) -> state_t

     
   * .. toggle-header::
        :header: Use Comparse to generate a parser and serializer for the types, with
                 :fstar:`%splice [ps_name_of_type] (gen_parser (`name_of_type))` and :fstar:`[@@ with_bytes bytes]` annotations.

        .. code::

           %splice [ps_ping_t] (gen_parser (`ping_t))
           %splice [ps_ack_t] (gen_parser (`ack_t))
           %splice [ps_message_t] (gen_parser (`message_t))

        .. code::

           [@@ with_bytes bytes]
           type ping_t = {
             alice: principal;
             n_a : bytes;
           }

   * .. toggle-header::
        :header: Define ``parseable_serializable`` instances for ``message_t`` and ``state_t``.

        .. code:: 

           instance parseable_serializeable_bytes_message_t: parseable_serializeable bytes message_t =
             mk_parseable_serializeable ps_message_t

        .. code::

            instance parseable_serializeable_bytes_state_t: parseable_serializeable bytes state_t =
              mk_parseable_serializeable ps_state_t
      
             
   * .. toggle-header::
        :header: Define ``local_state`` instance for ``state_t``.

        .. code::

           instance local_state_state: local_state state_t = {
             tag = "P.State";
             format = parseable_serializeable_bytes_state_t;
           }



   *Implement the protocol steps:*

   * The protocol steps go into the ``Protocol`` module.
   * For each step think about the *type* first:
     
     * The *monad*:
       
       * Every step will be in the ``traceful`` monad, since it works with the trace.
       * The step is in the ``traceful`` + ``option`` monad,
         if it may fail.
         (For example when reading a message from the trace,
         parsing a message to an expected format, looking up a particular state, etc.)
       * Most steps will probably be in the ``traceful`` + ``option`` monad.
         (A typical exception is the very first step of the protocol.)
     * Typical *input arguments* are:
       
       * the active participant in this step (of type :fstar:`principal`)
       * the timestamp of the message that is received in this step (of type :fstar:`timestamp`)
       * the session IDs of the state of the active participant,
         where private and public keys are stored (of type :fstar:`state_id`)
     * Typical *return values* are:

       * the timestamp of the message sent in this step (of type :fstar:`timestamp`)
       * the session ID of the active participant that has been used or updated in this step (of type :fstar:`state_id`)
       * The verly last step of the protocol usually doesn't have any return values and hence has return type :fstar:`unit`.
   * The general structure of one protocol step is:

     1. Receiving the message:

        1. .. toggle-header::
              :header: *receive* the message at the provided timestamp
           
              .. code::
                 
                 let*? msg = recv_msg msg_ts in
        2. .. toggle-header::
             :header: *decrypt* the message

             .. code::

                let*? plaintext = pke_dec_with_key_lookup #message_t alice keys_sid key_tag cipher in
        3. .. toggle-header::
              :header: *parse* the message to the abstract format

              .. code::

                 let*? abstract_msg = return (parse message_t msg) in
        4. .. toggle-header::
              :header: *check* that the message is of the *expected format* for the step

              .. code::
                 
                 guard_tr (Ping? asbtract_msg);*?
     2. .. toggle-header::
           :header: *Find* the *session* of the active participant corresponding to the received message.
            This includes checks of the received data and the stored data.

            .. code ::
            
               let*? (st, sid) = lookup_state #state_t alice some_property in
     3. Generate the next message (the reply):

        1. compute the *abstract* reply
        2. .. toggle-header::
              :header: *serialize* the reply

              .. code::
                 
                 let wire_msg = serialize #bytes message_t abstract_msg in
        3. .. toggle-header::
             :header: *encrypt* the reply

             .. code::
                
                let*? cipher = pke_enc_for alice bob key_sid key_tag plaintext in
        4. .. toggle-header::
              :header: *send* the reply

              .. code::

                 let* reply_ts = send_msg ciper in
     4. .. toggle-header::
           :header: *Update* the corresponding *session*

           .. code::

              set_state alice sid abstract_state;*
     5. *Return* the message timestamp from Step 3.4. and the session ID updated in Step 4.
           

   *Check the model with an example run:*
   
   After implementing the protocol steps,
   you should check that they model the protocol in the correct way.
   I.e., call the steps in the right order of an example run of the protocol
   and closely look at the produced trace:

   * .. toggle-header::
        :header: In a ``Run`` module,

        .. code::

           module DY.TwoMessage.Run

           open DY.Core
           open DY.Lib
           open DY.Simplified

           open DY.TwoMessage.Protocol

     * define a ``run`` function where you
     
       * .. toggle-header::
            :header: call the protocol steps in the order of an example run of the protocol,
                     passing on arguments (message timestamps, session IDs) as needed.

            .. code::

               val run:
                 unit -> traceful (option unit)
               let run () =
                 let alice = "Alice" in
                 let bob = "Bob" in

                 let* (alice_sid, ping_ts) = send_ping alice bob in
                 let*? (bob_sid, ack_ts) =
                   receive_ping_and_send_ack bob ping_ts in
                 receive_ack alice ack_ts;*?

         
       * .. toggle-header::
            :header: access the trace after the run with ``get_trace``
                     
            .. code::

               let* tr = get_trace in
      
       * .. toggle-header::
            :header: print the trace with :fstar:`IO.debug_print_string` using ``trace_to_string`` with
                     either ``default_trace_to_string_printers`` or a custom ``get_trace_to_string_printers`` for pretty printing.

            .. code::

               let _ = IO.debug_print_string "************* Trace *************\n" in
               let _ = IO.debug_print_string (
                  trace_to_string default_trace_to_string_printers tr
                ) in

         
     * .. toggle-header::
          :header: call the ``run`` function on the empty trace when executing the module

          .. code::

             let _ = run () empty_trace
   * .. toggle-header::
        :header: Add the ``test`` target to the ``Makefile``.

        .. code:: Makefile

           test:
             cd $(TUTORIAL_HOME)/obj; $(FSTAR_EXE) --ocamlenv ocamlbuild -use-ocamlfind -pkg batteries -pkg fstar.lib DY_TwoMessage_Run.native
             $(TUTORIAL_HOME)/obj/DY_TwoMessage_Run.native

   * Run ``make`` followed by ``make test``.
   * Look at the output and check:

     * Did the example run succeed? I.e., do you see any output after the ``***Trace***`` string?
       (If not, move ``get_trace`` and :fstar:`IO.debug_print_string` around until you find the step that is failing.)
     * Does the trace look like expected? Do all entries appear with the right values?
