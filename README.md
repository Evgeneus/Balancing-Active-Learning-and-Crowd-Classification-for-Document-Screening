# Active Learning for Multi-Predicate Document Screening

Given a set of documents, we consider a problem of screening them based on a set of binary predicates that verify by machines, crowd workers or experts. Our objective is to optimize the screening process regarding the quality of results and budget spent on obtaining training data for machine classifiers and crowd-based classification.

To run experiments install:
- Python 3.6 
- conda 4.3.30
- [modAL](https://modal-python.readthedocs.io/en/latest/)

<b>machine_and_experts_annotate</b> - active learning ML where experts annotate training data  <br/>
To start experiments, need to run machine_and_experts_annotate/src/main.py <br/>
To plot chaerts of results, use notebook machine_and_experts_annotate/notebooks/machines_and_experts.ipynb
