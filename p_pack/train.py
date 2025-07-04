# photonic_classifier/train.py

import jax
import jax.numpy as jnp
from p_pack import optimiser 
from p_pack import globals
from typing import List, Tuple




def train(init: List) -> Tuple[List, jnp.array]:
    """
    Executes the training loop for a fixed number of steps using `jax.lax.scan`.

    This function avoids using a standard for-loop to prevent high memory usage
    that could lead to a kernel crash. It iterates over the Adam optimization step
    for a number of steps defined in `globals.num_steps`.

    Args:
        init (List): The initial state for the optimizer carry, containing parameters,
                     data, labels, weights, and optimizer momentum vectors.

    Returns:
        Tuple[List, jnp.array]: A tuple containing the final state of the optimizer carry
                            and an array recording the loss at each step.
    """
    # Using for-loops ate all my RAM and then the kernel crashed.
    # But this awkward scan-loop seems to work very well!
    steps = jnp.arange(globals.num_steps)+1

    carry, loss_mem = jax.lax.scan(optimiser.adam_step, init, steps)
    # Note that jax.lax.scan automatically stacks the [step, loss_val] tensors we output
    # at the end of every Adam step. Therefore, the second output of scan is already
    # the full memory of all losses.
    return carry, loss_mem


# #some function gpt spat out when rewriting will have a look later
# @jax.jit
# def train2(init: List, num_steps: int, step_size: float) -> Tuple[List, jnp.array]:
#     """
#     An alternative JIT-compiled training loop using a factory for the Adam optimizer.

#     This function defines a scanner over Adam updates and is designed for performance.
#     It encapsulates the loss function and optimizer logic within the training function.

#     Args:
#         init (List): The initial state for the optimizer carry:
#                      [phases, data, labels, weights, m_p, v_p, m_w, v_w].
#         num_steps (int): The total number of training steps.
#         step_size (float): The learning rate for the Adam optimizer.

#     Returns:
#         Tuple[List, jnp.array]: A tuple containing the final state of the optimizer carry
#                             and an array recording the step and loss value at each iteration.
#     """
#     # scanner over Adam updates
#     def make_adam(carry, i):
#          """Defines a single Adam optimization step for use with jax.lax.scan."""

#         params_phases, data, labels, params_w, m_p, v_p, m_w, v_w = carry
    
#         loss_val = jax.lax.stop_gradient(
#             (jax.grad(lambda ph, w: train._loss(ph, data, labels, w), (0,3))
#              (params_phases, params_w))[0].mean()
#         )
#         # delegate to optimiser
#         opt = make_adam(step_size)
#         grads = jax.grad(train._loss, argnums=(0,3))(params_phases, data, labels, params_w)
#         (params_phases, params_w), (m_p, v_p, m_w, v_w) = opt.update(grads, (m_p, v_p, m_w, v_w), (params_phases, params_w))
#         return [params_phases, data, labels, params_w, m_p, v_p, m_w, v_w], jnp.array([i, loss_val])

#     # stash a handle to loss
#     @jax.jit
#     def _loss(ph, data, labels, w):
#         """A handle to the main loss function for use within this scope."""
#         from .loss import loss as L
#         return L(ph, data, labels, w)

#     train._loss = _loss

#     steps = jnp.arange(num_steps) + 1
#     carry, history = jax.lax.scan(adam_step, init, steps)
#     return carry, history



