A Model of the Two-Message Protocol
-----------------------------------

We build the DY* model of the Two-Message protocol following the `local-view description <example-twomessage-localview>` step by step.

.. _model-twomessage-setup:

Setup
.....

Create a new folder ``TwoMessageP`` and add the following ``Makefile``:

.. code:: Makefile

   TUTORIAL_HOME ?= ../..

   EXAMPLE_DIRS = path_to/TwoMessageP

   include $(TUTORIAL_HOME)/Makefile

If your run ``make`` in the ``TwoMessageP`` folder now,
it will verify all of core DY*.
This produces a lot of output on the terminal (including some warnings)
and takes quite some time (around 10 Minutes)!
You only have to do this once though, so you may as well start it now and let it run.

   
It is best practice to separate the definition of the abstract message and state types from the protocol steps.
We create two files ``DY.TwoMessage.Data.fst`` and ``DY.TwoMessage.Protocol.fst`` in the ``TwoMessageP`` folder.
Both of them are F* modules and as such must begin with

.. code::

   module name_of_file_without_fst

To import functions from core DY*, we need to open the corresponding modules in both:

.. code::

   open Comparse
   open DY.Core
   open DY.Lib

If the environment variables and the Makefile are setup correctly,
you should be able to (interactively) check both of the files successfully.
If the previous ``make`` has finished and you do ``make`` again,
it should be much faster and you should see a few lines related to the two files in the folder.

The abstract message and state types
....................................

We define the types for the abstract message and state format in the ``DY.TwoMessage.Data`` file.

Messages
~~~~~~~~

When we previously introduced the abstract message format
and looked at the example for the Two-Message protocol,
we already used valid F* syntax.
So we can just copy the two record type definitions for ``ping_t`` and ``ack_t``
from the `previous example<ex-abstract-messages-twomessagep>`.

Now that we have the types for the two messages separately,
we want to collect them in a single type for messages.
We do this, by defining a new type ``message_t``
and use constructors for the two messages:

.. code::

   type message_t =
     | Ping: (ping:ping_t) -> message_t
     | Ack:  (ack:ack_t) -> message_t

     
This fully defines our abstract message format.
Whenever we have a ``msg`` of type ``message_t``,
we know from the constructor whether it is a Ping or Ack message
and we can access the corresponding fields from the ``ping_t`` or ``ack_t`` record.

.. example:: Recap -- Instantiating and Accessing Values of Record Types

   A concret instance of a Ping message with content "Alice" and :math:`n`, can be specified as

   .. code::

      let msg : message_t = Ping {alice = "Alice"; n_a = n}
   
   Given this ``msg``, we can access say the ``alice`` field value with:

   .. code::

      let al = (Ping?.ping msg).alice


We now need to deal with parsing and serializing of our abstract message format from/to the wire format.
Luckily, we don't have to write parsing and serializing by hand,
since the tool `Comparse <https://github.com/TWal/comparse>`_ can construct those
automatically from the type definitions.

To invoke Comparse for a given type, we have to call

.. code::

   %splice [ps_(name_of_type)] (gen_parser (`name_of_type))

In our case, we need:

.. code::

   %splice [ps_ping_t] (gen_parser (`ping_t))

   %splice [ps_ack_t] (gen_parser (`ack_t))

   %splice [ps_message_t] (gen_parser (`message_t))

This generates parsing and serializing functions for each of our abstract message types.

However, this does not quite work yet.
We need to guide Comparse a bit.
Since Comparse is so general, we need to add some annotations to our types.
We need to add
:fstar:`[@@ with_bytes bytes]` right before the type definitions, i.e.,

.. code::
  
   [@@ with_bytes bytes]
   type ping_t = {
     alice: principal;
     n_a : bytes;
   }

We need to do that also for ``ack_t`` and ``message_t``.

Once you added all annotations, the splices should verify.
Verifying these lines takes a while (up to 15 Seconds)!
This is one of the reasons to separate them from other functions that you may want to
re-check frequently (for example protocol steps).

.. info:: Common Mistake: Forgetting :fstar:`[@@ with_bytes bytes]`

   If you try :fstar:`%splice [ps_ping_t] (gen_parser (`ping_t))`,
   but get an error of the form

   .. code:: none
             
     - ’tc’ failed
     - ’tcc’ failed
     - Cannot type (3) DY.Core.Bytes.Type.ps_bytes in context ([]). Error = ( - Name
       "DY.Core.Bytes.Type.ps_bytes" not found )
   
   you probably forgot to add the annotation :fstar:`[@@ with_bytes bytes]`
   right before the type you are splicing (here ``ping_t``).

.. info:: Common Mistake: Not using ``ps_name_of_type`` in the first argument of ``splice``

   If you get an error of the form

   .. code:: none

       Splice declared the name DY.TwoMessageP.Data.something_else_than_ps_ack_t but it was not defined.
       Those defined were: [DY.TwoMessageP.Data.ps_ack_t]

   you probably didn't use ``ps_ack_t`` in the brackets of the splice.

   The term in this brackets really needs to be ``ps_`` followed by the name of the type (here ``ack_t``)!
       
   That is, :fstar:`%splice [something_else_than_ps_ack_t] (gen_parser (`ack_t))` will produce the above error,
   while :fstar:`%splice [ps_ack_t] (gen_parser (`ack_t))` will not.
   

The final step for serializing and parsing is to declare our message type ``message_t``
an instance of Comparse's ``parseable_serializable`` class, like this:

.. code:: 

   instance parseable_serializeable_bytes_message_t: parseable_serializeable bytes message_t =
     mk_parseable_serializeable ps_message_t

We don't need to understand the details of this line.
The important part is, that now we can call ``parse`` and ``serialize`` for instances of our message type.

.. example:: ``serialize`` and ``parse`` for ``message_t``

   With :fstar:`let msg : message_t = Ping {alice = "Alice"; n_a = empty}` from above, we can write

   .. code::

      let _ =
        let msg_wire : bytes = serialize message_t msg in // serialize the abstract format to the wire format
        let msg_ = parse message_t msg_wire in  // parse from the wire format to an abstract message

   Note that we have to tell ``serialize`` and ``parse`` what the abstract type is that we consider (here ``message_t``).

We don't need to care about *how* the abstract messages are translated to the wire format,
i.e., how ``msg_wire`` looks like.
We just use the following properties that Comparse provides automatically:

.. code::

   let parse_serialize_inv_lemma x =
     parse message_t (serialize message_t x) == Some x

   let serialize_parse_inv_lemma buff =
     match parse message_t buf with
     | Some x -> serialize message_t x == buf
     | None -> True


..
   .. toggle-header::
      :header: **Discussion**

.. reveal::
   :header: Discussion
      
   These inverse properties of parsing and serializing are quite strong
   and may not be true for some real-world protocols!
   There might be different abstract messages that have the same serialization.
   Or the other way around: a wire format message could be parsed to two different abstract formats.
   There are examples of format confusion attacks for several protocols.

   Thus, enforcing the inverse properties "hides" some attacks
   that can not be found when using Comparse for generating the parser and serializer of a type.


Your ``DY.TwoMessageP.Data.fst`` file should now look like this:

.. code::

   module DY.TwoMessageP.Data

   open Comparse
   open DY.Core
   open DY.Lib

   [@@ with_bytes bytes]
   type ping_t = {
     alice: principal;
     n_a : bytes;
   }

   [@@ with_bytes bytes]
   type ack_t = {
     n_a : bytes;
   }

   [@@ with_bytes bytes]
   type message_t =
     | Ping: (ping:ping_t) -> message_t
     | Ack:  (ack:ack_t) -> message_t

   %splice [ps_ping_t] (gen_parser (`ping_t))
   %splice [ps_ack_t] (gen_parser (`ack_t))
   %splice [ps_message_t] (gen_parser (`message_t))

   instance parseable_serializeable_bytes_message_t: parseable_serializeable bytes message_t =
     mk_parseable_serializeable ps_message_t
     
We defined types for the abstract formats for Ping and Ack messages.
We then collected them in an overall ``message_t`` type.
Finally, we used Comparse to generate parsers and serializers for our types,
so that we can call ``parse`` and ``serialize`` for values of type ``message_t``.
     
States
~~~~~~

We do the exact same thing for our `abstract state formats <ex-abstract-state-twomessage>`.

.. exercise:: Define the abstract state format and parsing and serializing for them

   1. Copy the record types for the single abstract states.

      .. toggle-answer::

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


   2. Collect the types for the single states into an overall ``state_t`` type.

      .. toggle-answer::

         .. code::

            type state_t = 
              | SentPing: (ping:sent_ping_t) -> state_t
              | SentAck: (ack:sent_ack_t) -> state_t
              | ReceivedAck: (rack:received_ack_t) -> state_t
   3. Use Comparse to generate a parser and serializer for ``state_t``.

      .. toggle-answer::

         .. code::

            %splice [ps_sent_ping_t] (gen_parser (`sent_ping_t))
            %splice [ps_sent_ack_t] (gen_parser (`sent_ack_t))
            %splice [ps_received_ack_t] (gen_parser (`received_ack_t))
            %splice [ps_state_t] (gen_parser (`state_t))

         Don't forget to add :fstar:`[@@ with_bytes bytes]` for every type!
   4. Make ``state_t`` an instance of Comparse's ``parseable_serializable`` class.

      .. toggle-answer::

         .. code::

            instance parseable_serializeable_bytes_state_t: parseable_serializeable bytes state_t =
              mk_parseable_serializeable ps_state_t
      
            
There is one final technicality that we need to do for the state type.
We need to make it an instance of DY*'s ``local_state`` like this:

.. code::

   instance local_state_state_t: local_state state_t = {
     tag = "TwoMessage.State";
     format = parseable_serializeable_bytes_state_t;
   }

This ensures that our protocol-level states do not interfere with any state internal to DY*.

Summary
~~~~~~~

We now have our abstract message and state types
and can translate those to and from the wire format.
This is all that goes into the ``Data`` module.

.. howto:: Define abstract message and state formats

   * The abstract formats for messages and states go into the ``Data`` module.
   * For each message and state in the protocol,
     define its own type as a record.
   * Collect the individual record types for messages and states in an overall type ``message_t`` and ``state_t``
     using constructors for each of the cases.
   * Use Comparse to generate a parser and serializer for the types, with
     :fstar:`%splice [ps_name_of_type] (gen_parser (`name_of_type))` and :fstar:`[@@ with_bytes bytes]` annotations.
   * Define ``parseable_serializable`` instances for ``message_t`` and ``state_t``.
   * Define ``local_state`` instance for ``state_t``.
   

The protocol steps
..................

We will now implement the protocol steps in the ``DY.TwoMessage.Protocol`` module.

First, we need to import some libraries that we need later.
From above, we already have

.. code::

   open Comparse
   open DY.Core
   open DY.Lib

we add two more DY* libraries from the tutorial repo,
that offer a simplified interface to some of the core DY* functions:

.. code::

   open DY.Simplified
   open DY.Extend

These are imports for DY* functionality,
but we also want to use the abstract message and state types,
we just defined.
So we finally need to import

.. code::

   open DY.TwoMessage.Data

Our model of the Two-Message Protocol,
will consist of 3 functions,
one for each step of the `local-view description <example-twomessage-localview>`.

The first step: Sending a Ping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recall what happens in the first step of the protocol,
where Alice sends a Ping message:

1. Alice generates a new nonce :math:`n_A`
2. Alice sends the Ping message containing the nonce :math:`n_A`
   together with her name.
3. She stores the nonce :math:`n_A` and Bob's name in a new session.

The type
^^^^^^^^

Let's first think about the type of this protocol step.
Since we will send a message and store a new state,
the step is a ``traceful`` function.
Sending a message and storing a new state are both actions
that will always succeed, so we have a plain non-optional ``traceful`` function.

The input arguments are the names of Alice and Bob,
where Alice is the acting party and Bob is the intended receiver
of the message.

The return values are
the session ID of the new session of Alice,
where she stored the nonce,
so that we know which of Alice's sessions is the one
related to this run of the protocol
and
the timestamp of the Ping message,
so that we know where Bob can read the Ping on the trace.

In total, we have:

.. code::

   val send_ping:
     (alice: principal) -> (bob: principal) ->
     traceful (state_id & timestamp)


Generating the nonce
^^^^^^^^^^^^^^^^^^^^

To generate the nonce :math:`n_A`,
we use the function ``gen_rand`` from the ``DY.Simplified`` library.
This is a ``traceful`` action, so we need to use :fstar:`let*`
to give a name to the nonce:

.. code::

     let* n_a = gen_rand in


Sending the message
^^^^^^^^^^^^^^^^^^^

We build the abstract Ping message with

.. code::

   let ping = Ping {alice = alice; n_a = n_a} in 

Note that this is a non-monadic action,
i.e., an action without any side effects.
We are just defining a concrete instance of an abstract message.
Hence, we use the plain :fstar:`let` here.
Recall,
that plain :fstar:`let` s can be used inside any monad.

Before sending the Ping,
we need to translate it to the wire format.
That is, we need to serialize it:

.. code::

   let ping_wire = serialize message_t ping in

Again, serializing is a non-monadic action,
so we have the plain :fstar:`let`.
   
Observe that we need to tell the ``serialize`` function
the type of the second argument (here ``message_t``),
so that it knows which format to use.

Now, we can send the serialized Ping message
with the ``send_msg`` function from ``DY.Core``.
This function is a ``traceful`` function
that adds the message to the trace
and returns
the timestamp of the message on the trace.
This time, we have to use :fstar:`let*` to give the returned timestamp a name
(``traceful`` action inside a ``traceful`` function):

.. code::

   let* msg_ts = send_msg ping_wire in

The message is now sent and we can turn to storing the new state.
   
Storing the state
^^^^^^^^^^^^^^^^^

As for the message,
we first define the abstract state with

.. code::

   let ping_state = SentPing {bob = bob; n_a = n_a} in

We can then use the ``start_new_session`` function from
the simplified ``DY.Simplified`` library,
which returns the sessoin ID of the new session that was created.
This is a ``traceful`` action,
hence we use :fstar:`let*` again.
   

.. code::

   let* sid = start_new_session alice ping_state in

Note, that in contrast to messages,
we do not need to serialize the abstract state first!
This is handled internally by the ``start_new_session`` function
which is very convenient.

That's it for storing the state.

Returning
^^^^^^^^^

We performed all actions
(generating the nonce, sending the Ping message and storing a new state)
and can now finish the protocol step
by returning the new session id and the message timestamp:

.. code::

   return (sid, msg_ts)

Summary
^^^^^^^
   
In total, the function looks like this:

.. code::

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


The second step: Replying with an Ack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the second protocol step,
Bob receives a Ping message,
sends back the received nonce
and stores a new state for the session
with Alice and the none received in the message.

The Type
^^^^^^^^

We begin again with the type of this second step.
We are now reading from the trace, sending a message
and storing a new state.
So this step is also a ``traceful`` function.
But now, reading the Ping message may fail
(either when receiving, if there is no message entry at the
given timestamp or when parsing the wire format message to a Ping)
and so the whole step mail fail and we end up with a
``traceful`` + ``option`` function.

The input arguments are
the name of Bob (the receiving and replying participant)
and the timestamp of the Ping message.

The return values are the same as for the first protocol step:
the session ID of the new session of Bob,
where he stores the received nonce and name for this protocol run
and the timestamp of his reply (the Ack).

Thus, we have the type:

.. code::

   val receive_ping_and_send_ack:
     (bob:principal) -> (ping_ts:timestamp) ->
     traceful (option (state_id & timestamp))

     
Receiving the Ping
^^^^^^^^^^^^^^^^^^

To read the message from the trace,
i.e., receiving a message,
we call the ``recv_msg`` function from ``DY.Core``.
It takes as an argument the timestamp of the message
and returns the content of the message in wire format.
This can fail, if the entry at the provided timestamp
is not a message entry (for example, if it is a state entry,
or a generate nonce entry).
``recv_msg`` is thus a ``traceful`` + ``option`` function.
Since we want the overall protocol step to fail,
if receiving the message fails,
we use :fstar:`let*?` to store the read message content:

.. code::

   let*? msg = recv_msg msg_ts in 

If receiving is successful,
``msg`` contains the content of the message
and the step continues.
We now have to translate the wire format ``msg``
to our abstract Ping type.
Translating from wire to abstract format is parsing
and we would like to call

.. code::

   parse message_t msg

Parsing is an action that might fail,
but does not need to look at or change the trace.
Hence, parsing is an ``option`` action.
Now recall from the `monad introduction<monads-combine>`
that if we want to use an ``option`` action
inside a ``traceful`` + ``option`` action,
we need to use a ``return`` around the call.
And again, we want our overall step to fail,
if parsing fails,
so we use :fstar:`let*?`:

.. code::

    let*? png = return (parse message_t msg) in


If parsing is successful,
we now have the abstract format of
the message content stored at the input argument timestamp.
Now, we need to check that the received message
is indeed a Ping message (and not an Ack for example).
If it is not a Ping message,
the whole step should fail.

For this check,
we use the ``guard_tr`` function from ``DY.Core``.
This function takes a ``bool`` as argument
and has the behavior: if the bool is :fstar:`true`,
the execution continues with an unchanged trace,
if it is :fstar:`false` the execution stops.

With this, we can write:

.. code::
   
   guard_tr (Ping? png);*?
   
This checks, if the received abstract message is a Ping or not
and stops the execution if not.
   
Now, we know that the received message is indeed a Ping
and we can finally access the values that we need:

.. code::

   let Ping png = png in
   let alice = png.alice in
   let n_a = png.n_a in

Note: The first line above just removes the :fstar:`Ping` constructor.
The received and parsed ``png`` is of the general ``message_t`` type,
but to access the field values of the ``ping_t`` record,
we need to remove the :fstar:`Ping` constructor first.

This concludes receiving of the message
and reading its content.

Sending the Ack
^^^^^^^^^^^^^^^

We can now build the reply by
defining the concrete instance of the :fstar:`ack_t`:

.. code::

   let ack = Ack {n_a} in

To send the reply,
we first need to serialize it to the wire format
and can then use the ``send_msg`` function,
we already saw in the first protocol step.
This time, we do both serializing and sending together:
   
.. code::
   
   let* ack_ts = send_msg (serialize message_t ack) in

Remember that sending a message is a ``traceful`` action
that does not fail,
hence we have to use :fstar:`let*` here.
   

Storing the State
^^^^^^^^^^^^^^^^^

The remaining part of the second protocol step
is storing a new state for Bob.
This works the same as in the first protocol step.
We first define the content of the new state
in the abstract format:

.. code::

   let ack_state = SentAck {alice; n_a} in

and then start a new session for Bob with this new content:
   
.. code::
   
   let* sess_id = start_new_session bob ack_state in

Recall, we don't have to serialize the state content,
as this is done implicitly inside the ``start_new_session`` function.
Again, this is a ``traceful`` function that does not fail,
hence the :fstar:`let*`.
   

Returning
^^^^^^^^^

Finally, we have to return the
session ID of the new session
and the timestamp of the Ack.
Remember, that we are now in a ``traceful`` + ``option`` function,
hence we need to return an ``option``
(in contrast to the first protocol step):

.. code::

   return (Some (sess_id, ack_ts))

Summary
^^^^^^^

Collecting everything from above,
the second protocol step looks like this:

.. code::

   val receive_ping_and_send_ack:
     (bob: principal) -> (ping_ts: timestamp) ->
     traceful (option (state_id & timestamp))
   let receive_ping_and_send_ack bob msg_ts =
     let*? msg = recv_msg msg_ts in 
     let*? png = return (parse message_t msg) in
     guard_tr (Ping? png);*?

     let Ping png = png in
     let alice = png.alice in
     let n_a = png.n_a in

     let ack = Ack {n_a} in
     let* ack_ts = send_msg (serialize message_t ack) in

     let ack_state = SentAck {alice; n_a} in
     let* sess_id = start_new_session bob ack_state in

     return (Some (sess_id, ack_ts))


The third step: Receiving an Ack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the final protocol step,
Alice receives an Acknowledgment from Bob
and checks whether she previously started a run with Bob
and the nonce received in the Ack.
If this is the case,
she stores that this run is now completed.

The Type
^^^^^^^^

This step reads the Ack message from the trace
and looks for a previous state of Alice on the trace
and updates that state.
The step is thus a ``traceful`` function.
As in the previous step,
reading (and parsing) the Ack message may fail
as well as finding a previous state of Alice.
We thus have a ``traceful`` + ``option`` function.

The input arguments are the name of the acting participant,
i.e., Alice and the timestamp of the acknowledgment.

The return value is the session ID of the session
that Alice now considers as completed.

The type is:

.. code::

   val receive_ack:
     (alice: principal) -> (ack_ts: timestamp) ->
     traceful (option state_id)

Receiving the Ack
^^^^^^^^^^^^^^^^^

Receiving and parsing of the Ack
is the same as for the Ping message in the previous step.

We first call the ``recv_msg`` function with the provided timestamp of the Ack.
Recall, this is a ``traceful`` + ``option`` action
that might fail, if the trace entry at this timestamp
is not a message entry.
We thus have to use :fstar:`let*?`

.. code::

   let*? msg = recv_msg ack_ts in

If this action is successful,
we now have the Ack in the wire format.
To translate it to our abstract format,
we call ``parse``. Since this is an ``option`` action
inside a ``traceful`` + ``option`` function,
we need to wrap the call in a ``return`` and use :fstar:`let*?`:

.. code::

   let*? ack = return (parse message_t msg) in


If this action is successful,
we have the abstract message that was on the trace
at the provided timestamp.
We now need to check that this message
is indeed an Ack.
For this we use again the ``guard_tr`` function:

.. code::

   guard_tr (Ack? ack);*?


Reading the Ack from the trace was successful
and we can now access the data with

.. code::

   let Ack ack = ack in
   let n_a = ack.n_a in

Note again, that the first line just removes the :fstar:`Ack` constructor
to then access the ``n_a`` record field of the ``ack_t`` type.
   
Searching a previous state
^^^^^^^^^^^^^^^^^^^^^^^^^^

At this point,
Alice received a nonce :math:`n_A` as an acknowledgment.
She now wants to check, whether she actually
started a run with this nonce.


That is,
we are looking for a previous state of Alice
that is a :fstar:`SentPing` state and contains the same nonce
:math:`n_A`.

For this, we use the ``lookup_state`` function
from ``DY.Extend``:

.. code::

   let*? (sid, st) = lookup_state #state_t alice
     (fun st -> 
            SentPing? st
        && (SentPing?.ping st).n_a = n_a
     ) in

This function takes three arguments:

* the implicit abstract state type (here ``state_t``)
* the participant for which we want to find a state (here ``alice``)
* a property of an abstract state :fstar:`propt: state_t -> bool`
  
  Here the property checks that
  the state is a :fstar:`SentPing` state
  and the stored nonce in the state is the same as the received nonce :math:`n_A`
  from the Ack message.

The lookup function returns the
session ID of the found state and
the content, i.e. the abstract state.
The action may fail,
if there is no state of the principal satisfying the property.


.. reveal::
   :header: Discussion: How lookup works

   The ``lookup_state`` function
   looks for the first state entry on the trace
   (starting from the back/most recent time)
   that satisfies the property.
   It does *not* check that this state entry
   is the most recent one in the session.
   I.e., it could be the case,
   that the returned state is not the current state
   of the principal.
   In our case here that means,
   that we do not check whether Alice already completed the run before.

   For the examples in this tutorial,
   this implementation of the lookup function
   is sufficient.
   A future feature in DY*
   will change the behavior of the lookup
   to include the check to look only at the
   most recent states of sessions.

   
.. reveal::
   :header: Discussion: Why use lookup?

   From the analysis of cryptographic protocols
   you may be used to the attacker
   specifying the concrete session in
   follow-up steps.
   In our example, we could have added an
   additional argument to the ``receive_ack`` step
   for the session that Alice should be in.
   I.e., she would check whether the received nonce
   corresponds to the nonce stored in that
   specific session and then finish this session.

   Instead, we use the state lookup function here
   which is closer to how web servers work.
   They look at the content of received messages
   and try to find the corresponding session from that.
   For example by looking at some session ID provided in the message.

   Both models cover a range of session mixup attacks.
   If the attacker can provide the session,
   he can inject data in possibly unrelated sessions.
   With the lookup, we also get session mixup
   since the key we use for lookup might not be unique across sessions.

   Both models can be implemented in DY*.

Now that we have the previous state of Alice,
we can access the fields and see who was the other participant of that run

.. code::

   let bob = (SentPing?.ping st).bob in

Unfortunately,
this does not work immediately as we would expect.
We need to use another ``guard_tr`` first.

.. code::

   guard_tr (SentPing? st);*?

This guard should always be satisfied,
since the lookup function returns a state
satisfying the property,
which already includes that the state is
a :fstar:`SentPing` state.
So it doesn't change the function,
but it is needed for a technical reason
for DY* to argue that the found state is a :fstar:`SentPing` state.

..
   .. toggle-header::
      :header: **The technical reason**

.. reveal:: 
   :header: The technical reason
            
   In the bind of the ``traceful`` + ``option`` monad,
   the second action can't make use of the fact,
   that it is executed only if the first action was successful.
   It turns out to be technically very difficult
   to express this behavior for the second action
   in the type definition of the bind.


We have now found that Alice previously
started a run with the nonce received in the Ack.


Setting the new state
^^^^^^^^^^^^^^^^^^^^^

The next action is finishing the run.
We do this by updating the previous session of Alice
to a :fstar:`ReceivedAck` state.

Recall from the introduction of `sec-intro-states`
and `sec-intro-trace`
that a (full) state of a principal consists of several sessions
and that state entries on the trace contain only a single
state and not a complete session or full state of a principal.
The content of a state are stored together
with the name of the principal
and the session ID on the trace.
We may have several state entries for the same principal and session ID.
In this case the intended meaning is,
that the most recent of those entries is the current state
of this session.

Updating the state of a session,
is thus just adding a new state entry to the trace
with the new content
for the same principal and session ID.
This can be done with the ``set_state`` function:

.. code::

   set_state alice sid (ReceivedAck {bob; n_a});*

It is a ``traceful`` action that does not fail,
it takes as arguments the principal (``alice``),
the session ID (``sid``)
and the content of the state in its abstract format (the :fstar:`ReceivedAck` state)
   
   
Returning
^^^^^^^^^

The protocol step returns the session ID
of the session of Alice that has now finished.

.. code::

   return (Some sid)


Summary
^^^^^^^

The final protocol step looks like this:

.. code::

   val receive_ack:
     (alice: principal) -> (ack_ts: timestamp) ->
     traceful (option state_id)
   let receive_ack alice ack_ts =
     let*? ack = recv_msg ack_ts in
     let*? ack = return (parse message_t ack) in
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

This concludes the model of the  Two-message protocol.
We defined the abstract message and state types in
``DY.TwoMessage.Data`` and the three protocol steps
as functions in ``DY.TwoMessage.Protocol``.

You should be able to run ``make`` now in the example folder.

.. _sec-ex-run-two-message-implementation:

An Example Protocol Run
.......................

Now that we have our model of the Two-Message protocol,
we need to check that we modeled the right behavior.
We do this by implementing an example run of the protocol
using the protocol functions from the model.
We can then print the trace after this run and see
whether the run finishes successfully
and whether the trace looks as we expect.

Recall from `before <ex-run-two-messagep>`
that the trace after one successful run of the Two-Message protocol
should look like this:

.. code:: none
          
   1. Generate nonce n_A
   2. Message: Ping (Alice, n_A)
   3. Session 0 of Alice: SentPing n_A to Bob
   4. Message: Ack n_A
   5. Session 0 of Bob: SentAck n_A to Alice
   6. Session 0 of Alice: ReceivedAck n_A from Bob

Setup
~~~~~
      
We implement the example run in a new module ``DY.TwoMessage.Run``
in the same ``TwoMessageP`` folder.
We begin the module with the usual imports of the DY* libraries
and of course our protocol model:

.. code::

   open DY.Core
   open DY.Lib
   open DY.Simplified

   open DY.TwoMessage.Protocol

   
As a second setup,
we add a new target to our ``Makefile``
so that we can execute the extracted code and print the trace.
Add the following at the end of the ``Makefile`` in the ``TwoMessageP`` folder:

.. code:: Makefile

   test:
	cd $(TUTORIAL_HOME)/obj; $(FSTAR_EXE) --ocamlenv ocamlbuild -use-ocamlfind -pkg batteries -pkg fstar.lib DY_TwoMessage_Run.native
	$(TUTORIAL_HOME)/obj/DY_TwoMessage_Run.native


If you now run ``make`` followed by ``make test``,
the second command should produce some warnings on the terminal
and end with the following:

.. code:: none

   Finished, 4 targets (0 cached) in 00:00:00.
   ../../obj/DY_TwoMessage_Run.native


You are now set up to start implementing the example protocol run
in the new ``DY.TwoMessage.Run`` module.
This will consist of three parts:

1. Calling the protocol steps.
2. Printing the trace after the run.
3. Executing the example run.

The example run
~~~~~~~~~~~~~~~

The example run, will be a function where we call the
protocol steps in the expected order.
Since the individual steps are functions in the ``traceful`` + ``option`` monad,
our overall run function will also be in the ``traceful`` + ``option`` monad.
The run does not take any input arguments and does not return any value.
The type of the run function is thus

.. code::

   val run: unit -> traceful (option unit)

The first step of the protocol is the ``send_ping`` step.
This step takes as arguments the names of the two participants,
i.e., Alice and Bob.
Since we need these names later on again,
it is useful to define them in two variables:

.. code::

   let alice = "Alice" in
   let bob = "Bob" in

We can now call the ``send_ping`` step with ``alice`` and ``bob``.
This is a ``traceful`` action that returns
the new session ID of Alice for this new run
and the timestamp of the Ping message on the trace.
For the second step, we need the timestamp of the Ping,
so we save the computed values of the ``send_ping`` step
with :fstar:`let*`:

.. code::

   let* (alice_sid, ping_ts) = send_ping alice bob in

The second protocol step (``receive_ping_and_send_ack``)
takes as arguments the name of Bob (i.e., the variable ``bob``)
and the timestamp of the Ping
that the first step just computed (``ping_ts``).
The second step is a ``traceful`` + ``option`` action
and we want the overall run to fail,
if this step fails,
so we use :fstar:`let*?` to store the computed values:

.. code::

   let*? (bob_sid, ack_ts) = receive_ping_and_send_ack bob ping_ts in


The final step takes as argument the name of Alice
(stored in ``alice``)
and the timestamp of the Ack.
This last step is also a ``traceful`` + ``option`` action
and we want the run to fail, if this step fails.
Since we don't want to continue our run after this step,
we don't need to save the computed values and can just use:

.. code::

   receive_ack alice ack_ts;*?

This concludes the implementation of the example protocol run.
We called the protocol steps in the expected order,
passing on the arguments (in particular the message timestamps) from the previous steps.

Printing the Trace
~~~~~~~~~~~~~~~~~~

Inside the ``run`` function,
we want to print the trace,
after the run.

Printing in F* works with :fstar:`IO.debug_print_string` which takes
a string as argument that is then printed.
As you noticed before,
the ``make test`` produced some lines of output, even though
we didn't have any run yet.
It is thus useful,
to print some recognizable string before the actual output starts.
For example like this:

.. code::

   let _ = IO.debug_print_string "************* Trace *************\n" in


To print the actual trace,
we use the ``trace_to_string`` function from ``DY.Lib``.
This function takes two arguments:
some printer functions and the trace to be printed.
It returns a string.
For now, we can just use the default printers ``default_trace_to_string_printers``.

But how do we get the trace after the example run?
There is the ``traceful`` function ``get_trace`` in ``DY.Core``
that returns the current trace.
We can thus access the trace after the example run,
by calling ``get_trace`` after the calls to the protocol steps:

.. code::

   let* tr = get_trace in

Now that we have the trace,
we can call ``trace_to_string``
and print the resulting string:

.. code::

   let _ = IO.debug_print_string (
      trace_to_string default_trace_to_string_printers tr
    ) in

This concludes printing of the trace.

However, the ``run`` function has return type
``traceful (option unit)``,
so we need to return something in the end.
In our case,
we can just go with

.. code:: 

   return (Some ())

The overall ``run`` function looks like this:

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


     let* tr = get_trace in
     let _ = IO.debug_print_string "************* Trace *************\n" in
     let _ = IO.debug_print_string (
       trace_to_string default_trace_to_string_printers tr
       ) in

     return (Some ())

You can run ``make`` followed by ``make test`` now.
But you will not see any output from the ``run`` function,
only some warnings and output from the extraction process.
     
   
Executing the Run
~~~~~~~~~~~~~~~~~

As a final step,
we need to call our ``run`` function,
when the module is executed.
We achieve this by adding

.. code::

   let _ = run () empty_trace

at the end of the module.

If you run ``make`` followed by ``make test`` now,
you will see the ``*** Trace ***`` string
followed by the trace after the run.
The trace should look like this:

.. code:: none

   {"TraceID": 0, "Type": "Nonce", "Usage": {"Type": "NoUsage"}}
   {"TraceID": 1, "Type": "Message", "Content": "[Alice, [Nonce #0,]]"}
   {"TraceID": 2, "Type": "Session", "SessionID": 0, "Principal": "Alice", "Tag": "TwoMessage.State", "Content": "[Bob, [Nonce #0,]]"}
   {"TraceID": 3, "Type": "Message", "Content": " [Nonce #0,]"}
   {"TraceID": 4, "Type": "Session", "SessionID": 0, "Principal": "Bob", "Tag": "TwoMessage.State", "Content": "[Alice, [Nonce #0,]]"}
   {"TraceID": 5, "Type": "Session", "SessionID": 0, "Principal": "Alice", "Tag": "TwoMessage.State", "Content": "[Bob, [Nonce #0,]]"}

   
Pretty Printing
~~~~~~~~~~~~~~~

We can print the content of the trace entries nicer,
by defining our own printer functions for our
message and state types.
Download the ``DY.TwoMessage.Run.Printing.fst`` file from the `Tutorial Repo on GitHub <https://github.com/REPROSEC/dolev-yao-star-tutorial-code/blob/main/examples/TwoMessageP/DY.TwoMessage.Run.Printing.fst>`_.
Import the module in the ``DY.TwoMessage.Run`` module
and change the default printers to ``get_trace_to_string_printers``.

The printing should now look like:

.. code::

   let _ = IO.debug_print_string (
      trace_to_string get_trace_to_string_printers tr
    ) in


Run ``make`` followed by ``make test`` again.
The trace should now look like this:

.. code:: none

   {"TraceID": 0, "Type": "Nonce", "Usage": {"Type": "NoUsage"}}
   {"TraceID": 1, "Type": "Message", "Content": "Ping [name = (Nonce #0), n_a = (Alice)]"}
   {"TraceID": 2, "Type": "Session", "SessionID": 0, "Principal": "Alice", "Tag": "TwoMessage.State", "Content": "SentPing [n_a = (Nonce #0), to = (Bob)]"}
   {"TraceID": 3, "Type": "Message", "Content": "Ack [n_a = (Nonce #0)]"}
   {"TraceID": 4, "Type": "Session", "SessionID": 0, "Principal": "Bob", "Tag": "TwoMessage.State", "Content": "SentAck [n_a = (Nonce #0), to = (Alice)]"}
   {"TraceID": 5, "Type": "Session", "SessionID": 0, "Principal": "Alice", "Tag": "TwoMessage.State", "Content": "ReceivedAck [n_a = (Nonce #0), from = (Bob)]"}

Which is much closer to our `previous<ex-run-two-messagep>` intuitive description of the trace.

..  LocalWords:  Comparse
