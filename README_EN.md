# Malatya Apricot Production Forecasting — Thesis Analysis Archive

**Author:** Zafer Gökçe  
**Institution:** Bayburt University, Graduate School, Department of Industrial Engineering, Türkiye (2026)  
**Status:** **0.4.0 development/pre-release**; **no Zenodo DOI has been assigned**.  
**Repository:** https://github.com/zafergokce44/malatya-kayisi-production-forecast

This repository documents Extra Trees, Random Forest and linear-kernel Support Vector Regression analyses of fresh apricot production using agricultural-capacity and meteorological inputs. Two modelling datasets are distinguished: **TAM (57 observations)** from available historical records in 1934–2024 and **MALATYA (42 observations)** from the contiguous 1983–2024 subset. The Seed 42 holdout is a randomized split, not a forward-in-time forecast. Expanding-window validation covers 22 one-step-ahead assessments for 2003–2024. The results do not establish a causal effect of climate change.

## Source-to-result status

| Analysis | Script | Evidence and limits |
|---|---|---|
| Reference Seed 42 and five-seed exploratory split | `scripts/tezfinal.py` | Original source supplied; complete independent numerical rerun not documented |
| Repeated 10×5 CV, feature groups, lag sensitivity | `scripts/analiz_v2.py` | Supplied code and archived results; full independent rerun not documented |
| Chronological validation | `scripts/analiz_v2.py` | Supplied code and archived results; full independent rerun not documented |
| Nested 5×3 CV | `scripts/nested_cv_reconstruction.py` | **Reconstructed**, not original; selected outer folds matched saved predictions; full 30-fold validation pending |
| Spring minimum temperatures, 8 versus 11 inputs | `scripts/ilkbahar_min_reconstruction.py` | **Reconstructed**; all eight recorded result CSV files matched within 1×10⁻⁵ tolerance |

See [run instructions](docs/CALISTIRMA.md), [experiment mapping](docs/DENEY_ESLESTIRME.md) and the [archive audit](docs/ARSIV_DENETIMI_v0.4.0.md). Run `python tools/verify_repository.py` for hash/syntax checks (not a model reproduction test).

**Data access:** Source Excel files and original MGM meteorological data are not bundled. Some results include year-level actual production or row-level predictions; their publication rights require separate checking. Refer to [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md). Code owned by the author is licensed under [MIT](LICENSE); this does not license third-party datasets.

Citation metadata is in [CITATION.cff](CITATION.cff); add an actual verified DOI only after a Zenodo record has been published.
