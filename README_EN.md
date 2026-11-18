# Malatya Apricot Production Prediction — Thesis Code Archive

**Researcher:** Zafer Gökçe  
**Affiliation:** Bayburt University, Graduate School, Department of Industrial Engineering (2026)  
**Status:** Pre-release research archive, version 0.1.0. **No DOI has been assigned yet.**

This repository documents a thesis-based analysis of fresh apricot production using Extra Trees, Random Forest and linear-kernel support vector regression. The historical modelling set contains 57 observations spanning available records in 1934–2024; a 42-observation continuous subset covers 1983–2024. The study applies repeated cross-validation, nested cross-validation, feature sensitivity tests and expanding-window chronological validation.

**Limits of reproducibility:** Executable sources for the reference split, repeated CV and chronological evaluation are present. Archived results for nested CV and the spring-minimum-temperature sensitivity study are present, but their exact executable source scripts have not yet been verified. The archive has not been rerun against the original dataset during packaging. Do not describe it as fully reproducible at this stage.

**Data policy:** Original meteorological data and source Excel workbooks are **excluded** pending clarification of redistribution permissions. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md). Code distribution license to be selected by the researcher.

See the [Turkish README](README.md) and [run instructions](docs/CALISTIRMA.md) for more detail. When a Zenodo DOI is actually registered, add it to citation metadata and the thesis appendix.
