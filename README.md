# Intrinsic Pitch Value
This repository contains python notebooks that explore the process of creating an intrinsic pitch value model based on Trackman data.

The models in repository all follow the binary outcome tree structure ending in all BIP outcomes as a multiclass model (i.e. swing/take > contact/whiff > fair/foul > ball in play outcomes).

## Notebooks
1. **one-pitch-binary-models.ipynb** Walks through the steps to create the binary tree models based on just the current pitch.
2. **BIP_Run_Value_Exploration.ipynb** Explores different methods of modeling ball in play results (including HR's)
3. **Ball_Strike_model.ipynb** Explores creation of a called strike model for taken pitches.
4. **two-pitch-sequence.ipynb** (Work in Progress) Explores the same model as in the one pitch binary models, but with information about the previous pitch included.