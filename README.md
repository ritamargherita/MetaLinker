# MetaLinker

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0--1.0-lightgrey.svg)](#license)

## ✨ What is MetaLinker?

**MetaLinker** is a metadata-driven linking framework for tabular datasets. Instead of relying on the actual cell values (which may be inaccessible or privacy-sensitive), MetaLinker uses table **metadata** and embeddings to propose **links** between table elements and concepts from vocabularies. 

---

## 🗂️ Repository structure

MetaLinker/
├─ data/              # Example metadata, toy datasets, gold link labels
├─ src/               # Core library modules
├─ scripts/           # Entry-point scripts for linking, evaluation, etc.
├─ tests/             # Unit / integration tests
├─ results/           # Outputs: link proposals, evaluation reports
├─ LICENSE
└─ README.md

## 📣 Citation

If you use MetaLinker in your work, please cite this repository and its associated paper.

@article{martoranaLinker2024,
  title = {Column Vocabulary Association (CVA): Semantic Interpretation of Dataless Tables},
  author = {Martorana, Margherita and Pan, Xueli and Kruit, Benno and van Ossenbruggen, Jacco},
  url = {https://ceur-ws.org/Vol-3889/paper2.pdf},
  year = {2024}
  }
