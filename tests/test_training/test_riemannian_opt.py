# Copyright 2022 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""optimization tests"""

import numpy as np
from hypothesis import given
from hypothesis import strategies as st
from scipy.stats import unitary_group
from thewalrus.random import random_symplectic
from thewalrus.symplectic import is_symplectic

from mrmustard.math import Math
from mrmustard.training.parameter_update import update_orthogonal, update_symplectic, update_unitary

math = Math()


def is_unitary(M, rtol=1e-05, atol=1e-08):
    """Testing if the matrix M is unitary"""
    M_dagger = np.transpose(M.conj())
    return np.allclose(M @ M_dagger, np.identity(M.shape[-1]), rtol=rtol, atol=atol)


def is_orthogonal(M, rtol=1e-05, atol=1e-08):
    """Testing if the matrix M is orthogonal"""
    M_T = np.transpose(M)
    return np.allclose(M @ M_T, np.identity(M.shape[-1]), rtol=rtol, atol=atol)


@given(n=st.integers(2, 4))
def test_update_symplectic(n):
    """Testing the update of symplectic matrix remains to be symplectic"""
    S = math.new_variable(random_symplectic(n), name=None, dtype="complex128", bounds=None)
    for _ in range(20):
        dS_euclidean = math.new_variable(
            np.random.random((2 * n, 2 * n)) + 1j * np.random.random((2 * n, 2 * n)),
            name=None,
            dtype="complex128",
            bounds=None,
        )
        update_symplectic([[dS_euclidean, S]], 0.01)
        assert is_symplectic(S.numpy()), "training step does not result in a symplectic matrix"


@given(n=st.integers(2, 4))
def test_update_unitary(n):
    """Testing the update of unitary matrix remains to be unitary"""
    U = math.new_variable(unitary_group.rvs(dim=n), name=None, dtype="complex128", bounds=None)
    for _ in range(20):
        dU_euclidean = np.random.random((n, n)) + 1j * np.random.random((n, n))
        update_unitary([[dU_euclidean, U]], 0.01)
        assert is_unitary(U.numpy()), "training step does not result in a unitary matrix"
        sym = np.block(
            [[np.real(U.numpy()), -np.imag(U.numpy())], [np.imag(U.numpy()), np.real(U.numpy())]]
        )
        assert is_symplectic(sym), "training step does not result in a symplectic matrix"
        assert is_orthogonal(sym), "training step does not result in an orthogonal matrix"


@given(n=st.integers(2, 4))
def test_update_orthogonal(n):
    """Testing the update of orthogonal matrix remains to be orthogonal"""
    O = math.new_variable(math.random_orthogonal(n), name=None, dtype="complex128", bounds=None)
    for _ in range(20):
        dO_euclidean = np.random.random((n, n)) + 1j * np.random.random((n, n))
        update_orthogonal([[dO_euclidean, O]], 0.01)
        assert is_unitary(O.numpy()), "training step does not result in a unitary matrix"
        ortho = np.block(
            [
                [np.real(O.numpy()), -math.zeros_like(O.numpy())],
                [math.zeros_like(O.numpy()), np.real(O.numpy())],
            ]
        )
        assert is_symplectic(ortho), "training step does not result in a symplectic matrix"
        assert is_orthogonal(ortho), "training step does not result in an orthogonal matrix"
