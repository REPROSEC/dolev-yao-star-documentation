The ``traceful`` and ``option`` Monads
---------------------------------------

The ``traceful`` Monad
.......................

As we have seen previously,
the core object for capturing the overall state and for
stating and reasoning about properties of a protocol,
is the *global trace*.

Every protocol step is a sequence of reading entries from the current trace,
or adding new entries to the trace.
Each action in this sequence works with the new trace resulting from the previous action.

.. example:: Explicit Trace Manipulation in the Two-Message Protocol

   The explicit trace manipulations of the first step of the Two-Message protocol (see `Example: Local View of Two-Message Protocol <example-twomessage-localview>`) is:

   0. The current trace before the step begins is :code:`tr_in`
   1. Generate a nonce :math:`n_A` and store it on the current trace :code:`tr_in`.
      This results in the new trace :code:`tr_nonce`.
   2. Send the first message, i.e., append the message to the current trace :code:`tr_nonce`.
      This results in the new trace :code:`tr_message`.
   3. Store the SentPing state, i.e., append the new state to the current trace :code:`tr_message`.
      This results in the new trace :code:`tr_state`.

   The whole first step transforms the input trace :code:`tr_in` to the final trace :code:`tr_state`.

This explicit trace passing from one action to the next,
is rather cumbersome and we want to avoid doing that manually.
DY* offers the :code:`traceful` monad for *implicit* trace handling.
With this, we can just write the sequence of actions *without* having to think of the underlying traces.

At this point, you do *not* need to know what a monad is.
We will see everything we need to *use* the monad in the following.
The important general intuition is that monadic actions
compute some return value (just like normal functions)
but may have *side effects*.
In our case that means,
a traceful action works with the trace and may change the trace.
For example,
sending a message has the side effect,
that the message is added to the trace.


.. remember:: Intuition for Monads

   Monadic actions are functions with *side effects*.

   Specifically, a *traceful* action may look at and change the current trace.

.. infobox:: Info on Monads

   If you want to understand the general concept of monads in F*, we refer to the corresponding `chapter in the F* Book <https://fstar-lang.org/tutorial/book/part2/part2_par.html#a-first-model-of-computational-effects>`_.

   .. reveal::
      :header: If you are familiar with monads

      The :code:`traceful` monad
      is a *state monad*, where the state is the trace
      with the additional condition, that the new trace can only append entries to the old trace.
      The value/result type can be anything.

In the previous example, we see that each step has an effect on the trace (i.e., changes the trace).
We can thus consider the steps as traceful actions.

.. example:: Implicit Trace Manipulation in the Two-Message Protocol

   Using the :code:`traceful` monad, we can write the first step of the Two Message protocol as:

   1. Generate a new nonce :math:`n_A` (this implicitly changes the trace)
   2. Send the first message (this implicitly takes the trace after action 1 and produces a new trace)
   3. Store the SentPing state (this implicitly takes the trace after action 2 and produces a new trace)

   Which is exactly our intuitive description from `Example: Local View of Two-Message Protocol <example-twomessage-localview>`.


Sequential composition of traceful functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Combining two ``traceful`` actions sequentially,
like steps 1., 2. and 3. in the previous example,
is done with :fstar:`;*`:
:fstar:`traceful_action_1 ;* traceful_action_2`.

.. reveal::
   :header: If you are familiar with monads

   :fstar:`a;* b` is syntactic sugar for :fstar:`bind a (fun _ -> b)`
          
          
.. example:: Sequential Composition of Traceful Functions

   The following code snippet

   .. code::

      send_msg message ;*
      store_state alice state

   executes two traceful actions sequentially:

   1. A message (``message``) is sent (i.e., added to the end of the current trace)
   2. A new state (``state``) is stored for ``alice`` (i.e., the state is added to the trace after the message)


      
Accessing return values of traceful functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To access the computed value of a traceful action, we use :fstar:`let*`:

.. code::
   
   let* return_value = traceful_action in
   // now we can use return_value in subsequent actions

.. reveal::
   :header: If you are familiar with monads

   :fstar:`let* x = a in b` is syntactic sugar for :fstar:`bind a (fun x -> b)`


   
.. example:: Accessing Return Values of Traceful Functions

   With :fstar:`let* n_a = gen_rand in` we can access the nonce, returned by the traceful ``gen_rand`` function
   and use it later on under the name ``n_a``.

   *Note:* ``gen_rand`` as a traceful function also changes the underlying trace,
   but with :fstar:`let*` we are only accessing the computed *value*. The new trace is passed on implicitly as before.


.. _sec-traceful-return:
                
Returning a value inside a traceful function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If we compute some value inside a traceful function,
which we want to return to the caller of the function,
we use ``return value``.

.. example:: Returning a Value inside a Traceful Function

   Consider the example from above,
   where we send a message and then store a state.
   Recall, that sending a message is just adding the message to the trace.
   If later, someone should receive this message,
   the receiver needs to know the timestamp of the message on the trace.
   Thus, the send function returns exactly this timestamp and our bigger function
   needs to also return the timestamp.

   .. code::

      let* msg_ts = send_msg message in // send the message and store the returned timestamp
      store_state alice state ;*        // do some other traceful actions
      return msg_ts                     // return the message timestamp as final result of the traceful function
    
      
The ``option`` Monad
.....................

Another thing, that we want to simplify is combining functions that may fail.

Consider as an example a function where we want to
decrypt a cipher text, and then parse the resulting plain text to some abstract message format.
Both of the steps (decryption and parsing) may fail
and we want our overall function to succeed, only if both steps succeed.

Luckily, there is already a builtin type in F* capturing possible failure: the ``option`` type.
So we can write our function as

.. code::

   match decrypt cipher_text with
   | None -> None        // fail if decryption fails
   | Some plaintext -> ( // decryption was successful
       match parse plaintext with
       | None -> None               // fail if parsing fails
       | Some abstract_plaintext -> // parsing was successful
           ... // do something with abstract_plaintext
   )

This works perfectly fine, but is a lot of lines for just two actions!

To simplify the nested matches, we define the ``option`` monad.
The corresponding side effect here would be failure,
i.e., an optional action computes some value but may fail,
with the intuition that the execution stops in the failure case.

Similarly to :fstar:`;*` and :fstar:`let*` for the ``traceful`` monad,
we have :fstar:`;?` and :fstar:`let?` for composing functions that may fail
and accessing return values of such functions.

.. example:: :fstar:`;?` and :fstar:`let?` for the ``option`` monad

   Consider our example from before:
   a function that decrypts a cipher text, parses the resulting plain text
   and does something with the abstract plaintext.
   Each of the actions may fail and we want the overall function to succeed only if all actions succeed.
   We can write this as:
   
   .. code::

      let? plaintext = decrypt cipher_text in // Try to decrypt the ciphertext.
           // The whole step fails, if decryption fails. If decryption is successful, the result value is called plaintext.
      let? abstract_plaintext = parse plaintext in // Try to parse the plaintext. If successful the result value is called abstract_plaintext
      some_function abstract_plaintext;?  // Do something with the abstract plaintext. This step may fail (causing the whole function to fail).
      Some abstract_plaintext  // if all steps succeeded, the final return value of the function is the abstract plaintext

   See how the previous two nested matches are now just two lines (the first two)!
      
The ``traceful`` + ``option`` Monad
...................................
      
Most of the actions in a protocol step will be actions that work with the trace
*and* may fail.
For example,
in the last step of the Two-Message protocol,
Alice checks whether she previously started a flow
with the received nonce.
This action needs to look at the trace, but may fail if she did not start a flow with this nonce.

So we have a combination of the previous two side effects.
And indeed the combination of ``traceful`` and ``option``, where we have ``option`` inside ``traceful``,
i.e., :fstar:`traceful (option a)` is again a monad.

The intuition for sequentially composing two traceful + option actions is:

* the second action only gets executed if the first one is successful
* if the first action fails, the changes on the underlying trace of the first action are still captured

With this,
we model that the individual steps may fail,
but that all side-effects on the trace are recorded
up until the point of failure.
  

Just like before we have :fstar:`;*?` for sequential composition and
:fstar:`let*?` for accessing the return value of traceful + optional actions.

.. _example-composition-in-traceful-option:
       
.. example:: Composition in the ``traceful`` + ``option`` Monad

   Consider the following function in the traceful + option monad:

   .. code::

      let f (x:int): traceful (option string) =
        if x < 2 
        then ( 
          add_entry_ en;*?
          return (Some "added entry")
        )
        else return None

   This function takes an :fstar:`int` ``x``,
   if ``x`` is less than 2,
   an entry ``en`` is added to the current trace
   and the string "added entry" is returned.
   If ``x`` is not less than 2,
   the function fails (and returns :fstar:`None`).

   We sequentially execute this function 3 times with different values for ``x``:
   
   .. code::
      
      let f3 = f 1;*? f 2;*? f 0

   and see how the trace evolves (beginning with an empty trace) and what the final return value is.

   1. We begin with an empty trace ``tr0``
      and execute :fstar:`f 1`.
      This returns an optional string ``opt_str1`` and a new trace ``tr1``.
      Since 1 is less than 2,
      the entry ``en`` will be added to the trace ``tr0``
      and ``opt_str1`` is :fstar:`Some "added entry"`.
   2. We then execute :fstar:`f 2` with the new trace ``tr1``.
      This again, returns an optional string ``opt_str2`` and a new trace ``tr2``.
      Since 2 is not less than 2,
      ``opt_str2`` is :fstar:`None` and the trace doesn't change.
   3. Since the previous step returned :fstar:`None`,
      the final :fstar:`f 0` is not executed.

   In total,
   after step 3 we have a return value :fstar:`None`
   and a trace :fstar:`[en]`.
  
   To better understand the behaviour of the ``traceful`` + ``option`` monad,
   lets look at what happens if we switch the order of the three actions in the function ``f3``:
   (the first row is the case we just looked at)

   +-----------------------------+----------------------------+---------------+
   |``f3``                       |return value                |new trace      |
   +=============================+============================+===============+
   |:fstar:`f 1;*?  f 2;*?  f 0` |:fstar:`None`               |:fstar:`[en]`  |
   +-----------------------------+----------------------------+---------------+
   |:fstar:`f 0;*?  f 1;*?  f 2` |:fstar:`None`               |:fstar:`[en;   |
   |                             |                            |en]`           |
   +-----------------------------+----------------------------+---------------+
   |:fstar:`f 2;*?  f 1;*?  f 0` |:fstar:`None`               |:fstar:`[ ]`   |
   +-----------------------------+----------------------------+---------------+
   |:fstar:`f 1;*?  f 0`         |:fstar:`Some "added entry"` |:fstar:`[en;   |
   |                             |                            |en]`           |
   +-----------------------------+----------------------------+---------------+

   Looking at the first three rows,
   this highlights that monadic actions have *side effects*.
   Although the return value is the same for all three rows,
   the final trace is different.

:todo:`where should the following box go?`
   
.. _remember-last-action-in-traceful-option:
   
.. remember::

   The *last* action in a ``traceful`` + ``option`` function,
   must be

   * a call to a ``traceful`` + ``option`` action or
   * a ``return`` of :fstar:`None` or :fstar:`Some value`

   
   
.. _sec-comparing-traceful+option-traceful:
   
Comparing ``traceful`` + ``option`` with ``traceful``
.....................................................

The ``traceful`` + ``option`` monad can be considered
a special case of the ``traceful`` monad:
Every action in the ``traceful`` + ``option`` monad
can be considered as an action in the plain ``traceful`` monad,
if we ignore the knowledge that the return type is an option.

We already saw this in the function ``f`` in the previous example:
The function uses the :fstar:`return` of the ``traceful`` monad (in Lines 5 and 7)
to return the computed value.
Since, the return type of ``f``, considered as a plain ``traceful`` action,
is an option,
we need to return :fstar:`Some value` or :fstar:`None`.

It is important to know
which of the two monads we want,
when composing ``traceful`` + ``option`` actions.

.. example:: Comparing Composition of ``traceful`` + ``option`` actions with ``traceful`` actions

   To highlight the difference between sequential composition
   in the ``traceful`` + ``option`` monad
   with composition in the plain ``traceful`` monad,
   lets use :fstar:`;*` instead of :fstar:`;*?` in the function ``f3`` in the previous example:

   .. code::
      
      let f3 = f 1;* f 2;* f 0

   In the ``traceful`` monad,
   the composition just passes on the trace
   without looking at the return values of the function.
   Thus, the execution of ``f3`` does **not** stop
   when :fstar:`f 2` fails (as in the previous example)!
   :fstar:`f 2` doesn't change the trace and
   :fstar:`f 0` is successfully executed.

   The overall result of the new ``f3`` is
   :fstar:`Some "added entry"`
   and the new trace is :fstar:`[en; en]`.

   Look back at the first line in the table in the previous example
   and compare the results when using :fstar:`;*?`.
   

.. remember:: 

   If we compose two ``traceful`` + ``option`` actions with :fstar:`;*`,
   the second action gets executed in any case, even if the first action fails.

   If we compose them instead with :fstar:`;*?`,
   the second action is not executed when the first action fails.


:todo:`add a link/pointer to the example file in the repo (examples/Basics/DY.Basics.Monads.fst)`

Combining actions from different Monads
.......................................

We have now seen three monads,
and we looked at how to sequentially execute
actions *within the same* monad.
However,
it is often the case that we need to
combine actions from *different* monads.

.. example:: The Three Monads in one Protocol Step

   Consider the following prototypical excerpt of a protocol step: 
   
   1. receive a message
   2. parse the received message
   3. send a new message

   These actions are all in different monads:

   1. receiving a message is a traceful action that may fail (if there is no message entry at the provided timestamp) (``traceful`` + ``option``)
   2. parsing a message is an action that may fail, but does not need the trace (``option``)
   3. sending a message is a traceful action that never fails (``traceful``)


It is possible to compose actions of different monads,
but one has to be extra careful
which composition to use
and what the overall type of the function will be.

The Overall Type
~~~~~~~~~~~~~~~~

Let's first think about the overall type of a function
executing several actions from different monads.

Recall the main intuition:
monadic actions are functions with side effects.
If we compose several actions with different side effects,
the overall function may have *all* of the individual side effects.

In our case, we have the three side effects of
working with the trace, potential failure and "work with the trace and may fail".
Observe, that the last one captures both side effects of the first two.
From this, we intuitively see that
whenever we compose actions from different monads,
the overall function will be in the ``traceful`` + ``option`` monad,
since we may have an effect on the trace and may fail.

Putting things a bit differently, this means,
that if you want to write a function in the ``option`` monad,
you *can not* use any ``traceful`` or ``traceful`` + ``option`` actions
inside,
since this would mean having more side effects
than just the failure case from ``option``
specified in the type of your function.
And similarly,
if you are writing a non-optional ``traceful`` function,
you can not use an ``option`` or ``traceful`` + ``option`` action inside,
since the failure side effect is not covered by the specified type.

.. remember:: 

   If you compse actions from different monads,
   you will end up in the ``traceful`` + ``option`` monad.

   * Inside an ``option`` function,
     you *can not* call ``traceful`` or ``traceful`` + ``option`` actions.
   * Inside a plain non-optional ``traceful`` function,
     you *can not* call ``option`` or ``traceful`` + ``option`` actions.

How to Compose
~~~~~~~~~~~~~~

Now that we know,
we are in a ``traceful`` + ``option`` function,
we have to think about
how to call ``option`` and plain ``traceful`` actions
inside our function.

``traceful`` inside ``traceful`` + ``option``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Plain non-optional ``traceful`` actions
already have the "may modify trace" side effect,
but are missing the "might fail" effect.
Intuitively, a non-optional action,
just does not fail and always produces a result and a new trace.
We can thus use the plain ``traceful`` :fstar:`;*`.

.. example:: ``traceful`` action inside ``traceful`` + ``option``

   In most of the protocol steps,
   we will send some message.
   This is a ``traceful`` action,
   since it appends the message to the trace,
   that returns the timestamp of the message in the new trace.
   The action never fails, since entries can always be added to the trace.

   In the protocol step we can write

   .. code::

      send_msg message;*
      ... // some other traceful + option actions

   Or, if we want to use the returned timestamp

   .. code::

      let* ts = send_msg message in
      ... // some other traceful + option actions that can use ts

Recall from `before <remember-last-action-in-traceful-option>`
that the last action in a ``traceful`` + ``option`` function,
needs to be a call to another ``traceful`` + ``option`` action (as in the example above),
or a ``return`` of an ``option``.
So if we want to have a plain ``traceful`` action as the last step in our function,
we need to have a ``return`` after that.

.. example:: ``traceful`` action as *last* action inside ``traceful`` + ``option``

   If sending a message is the last action in our protocol step,
   and we want to return the message timestamp,
   we need to write

   .. code::

      let* ts = send_msg message in
      return (Some ts)

``traceful`` + ``option`` actions inside ``traceful`` + ``option``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A special case of the above, are ``traceful`` + ``option`` actions
inside the overall ``traceful`` + ``option`` function.
You may wonder why we need to talk about this case here.
Isn't this just combining actions within the *same* monad?

Well, we have seen `before <sec-comparing-traceful+option-traceful>`
that we can use both :fstar:`;*` and :fstar:`;*?`
to combine ``traceful`` + ``option`` actions.
And it depends on whether we want the second action to be executed
if the first one fails or not.

.. example:: Using both :fstar:`;*` and :fstar:`;*?` for ``traceful`` + ``option`` actions

   We look again at the function ``f`` from `the previous example <example-composition-in-traceful-option>`
   and use a mix of :fstar:`;*` and :fstar:`;*?` to combine
   the calls for different arguments:

   +----------------------------+---------------------------+-----------------+
   |``f3``                      |return value               |new trace        |
   +============================+===========================+=================+
   |:fstar:`f 1;*?  f 2;* f 0`  |:fstar:`Some "added entry"`|:fstar:`[en; en]`|
   |                            |                           |                 |
   +----------------------------+---------------------------+-----------------+
   |:fstar:`f 1;* f 3 ;* f 1 ;* |:fstar:`None`              |:fstar:`[en; en]`|
   |f 2 ;*? f 0`                |                           |                 |
   +----------------------------+---------------------------+-----------------+
   |:fstar:`f 1;* f 3 ;*? f 1 ;*|:fstar:`None`              |:fstar:`[en]`    |
   |f 2 ;*? f 0`                |                           |                 |
   +----------------------------+---------------------------+-----------------+


      
``option`` inside ``traceful`` + ``option``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An ``option`` action,
already has the "may fail" effect,
but is missing the "modifies trace" effect,
since it doesn't even operate on a trace.
Intuitively,
an action not working with the trace
can be seen as a ``traceful`` action
that doesn't change the trace.
That is, an ``option`` action
can be seen as a ``traceful`` action
that computes some value and passes the underlying trace on unchanged.
This behavior can be realized with the ``return`` we :ref:`previously <sec-traceful-return>` introduced.
``return`` takes some value and attaches the current trace to it unchanged.

.. example:: ``option`` action inside ``traceful`` + ``option``

   When we receive a message in some protocol step,
   the message is in the wire format.
   Since we want to work with the abstract format,
   we need to parse the received message.
   Parsing may fail but does not need to look at the trace.
   Thus, parsing is an ``option`` action.
   The overall protocol step will be a ``traceful`` + ``option`` function.

   Thus, we need to use ``return`` around the call to ``parse`` inside the protocol step:

   .. code::
      
      let*? abstract_message = return (parse wire_message) in
   

:todo:`add an exercise`

.. remember::

   To call an ``option`` action
   inside a ``traceful`` + ``option`` function,
   you need to use ``return`` around the call to the action.


Summary
~~~~~~~
   
To summarize,
it is possible to combine actions from different monads.
If we do so, we will end up in the ``traceful`` + ``option`` monad.
To combine these actions, we need to take special care of which
:fstar:`;` and :fstar:`let` to use.
The following gives an overview:

.. _monads-combine:

.. remember:: Which :fstar:`;` and :fstar:`let` to use?

   If you want to call an action :fstar:`act : m ret`
   inside a function :fstar:`f : m' ret'`,
   where ``m`` and ``m'`` are two of the three monads we have seen,
   and ``ret`` and ``ret'`` some return types,
   you can use the following table to choose the right composition and accessing return values:
   
   +----------------------------+----------------------------+--------------+--------------+-----------------+
   |``m'`` (the monad of ``f``) |``m`` (the monad of ``act``)|:fstar:`;`    |:fstar:`let`  |comment          |
   +============================+============================+==============+==============+=================+
   |``option``                  |``option``                  |:fstar:`;?`   |:fstar:`let?` |                 |
   +----------------------------+----------------------------+--------------+--------------+-----------------+
   |``traceful``                |``traceful``                |:fstar:`;*`   |:fstar:`let*` |                 |
   +----------------------------+----------------------------+--------------+--------------+-----------------+
   |``traceful`` + ``option``   |``traceful`` + ``option``   |:fstar:`;*` or|:fstar:`let*` |depending on     |
   |                            |                            |:fstar:`;*?`  |or            |wanted behavior  |
   |                            |                            |              |:fstar:`let*?`|in error case:   |
   |                            |                            |              |              |                 |
   |                            |                            |              |              |should the rest  |
   |                            |                            |              |              |be executed if   |
   |                            |                            |              |              |the first action |
   |                            |                            |              |              |fails or not?    |
   |                            |                            |              |              |                 |
   +----------------------------+----------------------------+--------------+--------------+-----------------+
   |                            |``option``                  |:fstar:`;*?`  |:fstar:`let*?`|*must* use       |
   |                            |                            |              |              |``return`` around|
   |                            |                            |              |              |call to action   |
   +----------------------------+----------------------------+--------------+--------------+-----------------+
   |                            |``traceful`` and ``ret'`` is|:fstar:`;*`   |:fstar:`let*` |if *last* action |
   |                            |not ``option``              |              |              |in ``f``, a      |
   |                            |                            |              |              |``return`` must  |
   |                            |                            |              |              |follow           |
   +----------------------------+----------------------------+--------------+--------------+-----------------+

   Plain :fstar:`let` (i.e., non-monadic actions) can be used inside any monadic function.


We now have all pre-requisites to start our first protocol model in DY*.
   
      
..  LocalWords:  traceful fstar monads
