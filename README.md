# Project: BundleTree
A Bundle Tree-type implement of Adaptive Mesh Refinement (AMR) for General Relativity Magneto-hydrodynamics (GRMHD) simulations.

## How we name this project?
By analysis of traditional AMR frameworks, we find that what we're actually doing is not just adaptively refining meshes. Since we usually define our data on a customized mesh, we can regard this structure as a fibre bundle. As for adaptive refinement process, we can realize it by submitting refined grids into next or higher level (corresponding to AMR level). In this way, we obtain a tree-like bundles and name it naturally as BundleTree.

## Framework
### DataStructure.py
In this file, we pre-defined three useful classes for establishing a BundleTree for a specific problem.

To define grids or meshes, one can initialize a `Chart` object. To define corresponding data, one can use given data and newly created `Chart` object to initialize a `Bundle` object. In order to build a tree, a class named `TreeNode` is provided. You can refer to our test file `test.py` for more details.
