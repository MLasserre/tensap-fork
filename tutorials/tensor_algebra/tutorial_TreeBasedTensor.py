# Copyright (c) 2020, Anthony Nouy, Erwan Grelier
# This file is part of tensap (tensor approximation package).

# tensap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# tensap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with tensap.  If not, see <https://www.gnu.org/licenses/>.

"""
Tutorial on TreeBasedTensor.

"""

import numpy as np
import tensap

# %% Linear dimension tree
ORDER = 5
TREE = tensap.DimensionTree.linear(ORDER)
TREE.plot(title="Nodes indices")
TREE.plot_dims(title="Nodes dimensions")

# %% Random dimension tree
ORDER = 10
ARITY_INTERVAL = [2, 3]
TREE = tensap.DimensionTree.random(ORDER, ARITY_INTERVAL)
TREE.plot(title="Nodes indices")
TREE.plot_dims(title="Nodes dimensions")

# %% TreeBasedTensor: random generation
TENSOR = tensap.TreeBasedTensor.rand(TREE)
TENSOR.plot(title="Active nodes")
TENSOR.plot([x.storage() for x in TENSOR.tensors], title="Tensors' storage complexity")
TENSOR.plot(TENSOR.representation_rank, title="Representation ranks")

# %% Truncation of a TreeBasedTensor with prescribed rank
TRUNCATOR = tensap.Truncator(tolerance=0, max_rank=np.random.randint(1, 5))
TENSOR = tensap.TreeBasedTensor.rand(TREE)
TENSOR_TRUNCATED = TRUNCATOR.hsvd(TENSOR)
print(
    "Prescribed rank, error = %2.5e\n"
    % ((TENSOR - TENSOR_TRUNCATED).norm() / TENSOR.norm())
)

# %% Truncation of a TreeBasedTensor with prescribed relative precision
ORDER = 10
TREE = tensap.DimensionTree.random(ORDER, 3)
TENSOR = tensap.TreeBasedTensor.rand(TREE)

TRUNCATOR = tensap.Truncator(tolerance=1e-8)
TRUNCATOR._hsvd_type = 1  # Root to leaves truncation
TENSOR_TRUNCATED_1 = TRUNCATOR.hsvd(TENSOR)
ERR_1 = (TENSOR - TENSOR_TRUNCATED_1).norm() / TENSOR.norm()
print(
    "Root to leaves: prescribed tolerance = %2.5e, error = %2.5e\n"
    % (TRUNCATOR.tolerance, ERR_1)
)

TRUNCATOR._hsvd_type = 2  # Leaves to root truncation
TENSOR_TRUNCATED_2 = TRUNCATOR.hsvd(TENSOR)
ERR_2 = (TENSOR - TENSOR_TRUNCATED_2).norm() / TENSOR.norm()
print(
    "Leaves to root: prescribed tolerance = %2.5e, error = %2.5e\n"
    % (TRUNCATOR.tolerance, ERR_2)
)

TENSOR_TRUNCATED_2.plot(
    TENSOR_TRUNCATED_2.representation_rank, title="Representation ranks"
)

# %% Truncation of a FullTensor
ORDER = 5
ARITY_INTERVAL = [2, 3]
TREE = tensap.DimensionTree.random(ORDER, ARITY_INTERVAL)

SIZE = np.random.randint(8, 11, ORDER)
ACTIVE_NODES = tensap.TreeBasedTensor._random_is_active_node(TREE)

A = tensap.FullTensor.randn(SIZE)
TRUNCATOR = tensap.Truncator(tolerance=5e-1)
A_TRUNCATED = TRUNCATOR.hsvd(A, TREE, ACTIVE_NODES)
ERR = (A - A_TRUNCATED.full()).norm() / A.norm()
print("Tolerance = %2.5e, error = %2.5e\n" % (TRUNCATOR.tolerance, ERR))
A_TRUNCATED.plot(A_TRUNCATED.representation_rank, title="Representation ranks")

TRUNCATOR.tolerance = 1e-2
A_TRUNCATED = TRUNCATOR.hsvd(A, TREE, ACTIVE_NODES)
ERR = (A - A_TRUNCATED.full()).norm() / A.norm()
print("Tolerance = %2.5e, error = %2.5e\n" % (TRUNCATOR.tolerance, ERR))
A_TRUNCATED.plot(A_TRUNCATED.representation_rank, title="Representation ranks")

# %% Tensor train format
ORDER = 10
TREE = tensap.DimensionTree.linear(ORDER)
RANKS = np.hstack((1, np.random.randint(1, 3, TREE.nb_nodes - 1)))

SIZE = np.full(ORDER, 3)
ACTIVE_NODES = np.logical_not(TREE.is_leaf)
ACTIVE_NODES[TREE.dim2ind[0] - 1] = True
TENSOR = tensap.TreeBasedTensor.rand(TREE, RANKS, SIZE, ACTIVE_NODES)

TENSOR.plot(title="Nodes indices")
TENSOR.tree.plot_dims(title="Nodes dimensions")

# With a permutation of dimensions
RPERM = np.random.permutation(range(ORDER))
TREE = tensap.DimensionTree.linear(RPERM)
TENSOR = tensap.TreeBasedTensor.rand(TREE, RANKS, SIZE, ACTIVE_NODES)

TENSOR.plot(title="Nodes indices")
TENSOR.tree.plot_dims(title="Nodes dimensions")

# %% Algebraic operations
ORDER = 8
TREE = tensap.DimensionTree.linear(ORDER)
SZ = np.random.randint(3, 10, ORDER)
T1 = tensap.TreeBasedTensor.rand(TREE, shape=SZ)
T2 = tensap.TreeBasedTensor.rand(TREE, shape=SZ)
print("ranks of T1   :", T1.ranks)
print("ranks of T2   :", T2.ranks)
print("\nAddition of tensors:\n--------------------")
Tplus = T1 + T2
print("ranks of T1+T2:", Tplus.ranks)
print("\nSubstraction of tensors:\n----------------------")
Tminus = T1 - T2
print("ranks of T1-T2:", Tminus.ranks)
print("\nHadamard product of tensors:\n-------------------------")
Ttimes = T1 * T2
print("ranks of T1*T2:", Ttimes.ranks)
print("\nNorm of tensors:\n--------------------")
print("norm of T1", T1.norm())
print("norm of T1*T2", Ttimes.norm())

print("\nSum of T1 along dimensions:\n-------------------------")
print("dimensions of T1        : ", T1.shape)
print("dimensions of T1.reduce_sum(0) : ", T1.reduce_sum(0).shape)
print("dimensions of T1.reduce_sum([2,5,7]) : ", T1.reduce_sum([2, 5, 7]).shape)
print("sum of all entries = ", T1.reduce_sum())


# %% Changing root node of a tree based tensor

ORDER = 5
TREE = tensap.DimensionTree.balanced(ORDER)
RANKS = np.hstack((1, np.random.randint(2, 3, TREE.nb_nodes - 1)))
SZ = np.random.randint(2, 4, ORDER)
T1 = tensap.TreeBasedTensor.rand(TREE, ranks=RANKS, shape=SZ)
T1.plot(title="Nodes indices with root 1")
num2 = 2
T2 = T1.change_root(num2)
T2.plot(title="Nodes indices with root " + str(num2))
num3 = 9
T3 = T1.change_root(num3)
T3.plot(title="Nodes indices with root" + str(num3))
T3bis = T2.change_root(num3)
T3bis.plot(
    title="Nodes indices with root " + str(num3) + " from format with root " + str(num2)
)
print((T3 - T3bis).norm() / (T3.norm() + T3bis.norm()) * 2)


# %% Activate and incativate nodes
ORDER = 5
TREE = tensap.DimensionTree.balanced(ORDER)
T1 = tensap.TreeBasedTensor.rand(TREE)
T1.plot(title="Initial tensor format")
T2 = T1.inactivate_nodes([9, 5])
print("Check T1-T2 = 0 : ", (T2 - T1).norm() / (T1.norm() + T2.norm()) * 2)
T2.plot(title="Inactivate nodes [9,5]")
T3 = T2.activate_nodes([9, 5])
T3.plot(title="Reactivate nodes [9,5]")
print("Check T1-T3 = 0 : ", (T3 - T1).norm() / (T1.norm() + T3.norm()) * 2)


# %% Extraction of a subtree and corresponding tensor
# (basis of minimal subspace)
ORDER = 5
TREE = tensap.DimensionTree.balanced(ORDER)
T = tensap.TreeBasedTensor.rand(TREE)
subTREE, nodes = TREE.sub_dimension_tree(2)
subT = tensap.TreeBasedTensor(T.tensors[nodes - 1], subTREE)
