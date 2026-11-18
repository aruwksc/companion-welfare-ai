# CWA-40: Pose, ML Integration, and Behaviour Classifier Technology Comparison

**Status:** Decision outcome recorded. The team selected the options below for the prototype. Detailed ADR records should use the same decisions and retain the open conditions listed in this document.

## 1. Purpose and decision scope

This comparison evaluates the options listed in CWA-40:

- **D2 / ADR-0002:** pose-estimation technology;
- **D3 / ADR-0003:** integration boundary between the desktop application and ML pipeline;
- **D6 / ADR-0006:** behaviour-classification approach.

The comparison uses the system requirements in `docs/requirements.md`, the existing pose experiments in `docs/ml/model-comparison.md` and `docs/ml/onnx-export.md`, and the label/evaluation protocol in `docs/ml/behavior-labeling.md`. The product is an observation aid. It must not present predictions as a veterinary diagnosis.

## 2. Decision criteria

Options are assessed against:

1. suitability for dog videos and the defined observable labels;
2. compatibility with local processing and the SYS-01 privacy boundary;
3. ability to return events, intervals, confidence, and model version as required by SYS-03 and SYS-06;
4. measurable performance and uncertainty, without treating confidence as accuracy;
5. implementation and maintenance effort for the current team;
6. source-code, model-weight, and dataset terms checked separately;
7. ability to replace a model or runtime without changing the application UI or persistence layer.

## 3. D2 / ADR-0002: Pose-estimation technology

| Option | Fit and evidence | Licence and deployment considerations | Team experience / limits |
|---|---|---|---|
| **ViTPose++-Base with AP-10K expert** | Produces animal keypoints. In the existing same-20-frame pilot, it produced poses for 20/20 frames in 2.42 s (8.26 end-to-end pipeline FPS) on a Colab Tesla T4. The project also exported this checkpoint to ONNX and passed a runtime smoke test. | ViTPose source repository lists Apache-2.0. The exact checkpoint, config, training data, and any redistribution rights still need their own review; a code licence does not establish the weights' licence. The ONNX file and weights remain outside Git. | **Most demonstrated option:** the team has run Base and exported it. No ground-truth keypoints were available, and the local desktop has not been benchmarked. |
| **ViTPose++-Large with AP-10K expert** | Same pilot: 20/20 frames with poses in 4.90 s (4.08 pipeline FPS). Mean keypoint confidence was 0.597 versus 0.500 for Base, but confidence is not an accuracy measure. | Same separate checkpoint/config/data licence review is required. Greater runtime and memory needs should be measured on the target machine. | Already compared in the Colab pilot; no accuracy or target-desktop result is available. |
| **DeepLabCut SuperAnimal Quadruped** | Animal-oriented pose-estimation alternative with its own data and inference workflow. It could be evaluated against ViTPose on the same consented and manually annotated dog frames. | DeepLabCut software is LGPL-3.0; its README says SuperAnimal models are for research use only (non-commercial). Do not package or use these weights for a commercial product without resolving their terms. | No DeepLabCut implementation or benchmark is recorded in this repository; setup and evaluation would add onboarding work. |

### Selected decision — ADR-0002: Pose estimation

The team selected **ViTPose++-Base with the AP-10K expert as the prototype pose adapter**. ViTPose++-Large and DeepLabCut remain comparison options and will not be added as runtime dependencies. The exact checkpoint's licence must be verified before redistribution or packaging. The selection is based on existing integration evidence and the faster result in the preliminary pilot; it does not establish higher accuracy. Before making a model-quality claim, annotate a dog-separated keypoint subset and report PCK or OKS, then measure FPS, memory, and failure cases on the target desktop.

## 4. D3 / ADR-0003: ML integration boundary

| Option | Advantages | Costs and risks | Fit with requirements |
|---|---|---|---|
| **Run ML in the desktop application's process** | Simplest call path and packaging; no IPC layer. | Heavy ML imports, native dependencies, or a failed inference can affect the UI process; environment conflicts are harder to isolate. | Can keep data local, but weaker fault/dependency isolation. |
| **Separate local ML worker process with a versioned JSON contract** | Keeps video local; isolates ML dependencies and failures; permits a replaceable backend; can return stable event records independent of model framework. | Requires worker lifecycle, error handling, and schema/version management. | Strong fit for SYS-01 and SYS-03; supports the replaceable PosePort/model boundary in the architecture. |
| **Local HTTP service on loopback** | Familiar request/response API and easy separation of UI and ML runtime. | Adds service startup, port/security configuration, and request handling; loopback does not by itself guarantee correct privacy or lifecycle behavior. | Possible, but more machinery than needed for a single desktop prototype. |

### Selected decision — ADR-0003: ML integration

The team selected a **separate local ML worker process with a versioned application-to-ML contract**. The application sends a local video/frame reference plus analysis settings; the worker returns structured events and diagnostics, including `schema_version`, `model_id`, `model_version`, label, `[start, end)` timestamps, confidence, and warnings. Video remains on the device and is not sent to a remote service. Runtime-specific code stays behind `PosePort`/adapter interfaces. **ONNX Runtime is the selected first inference adapter** for the exported model; the worker contract remains independent of ONNX. The existing ONNX result is a runtime smoke test only, not evidence of pose accuracy.

## 5. D6 / ADR-0006: Behaviour-classifier technology

The class definitions and annotation rules remain those in `docs/ml/behavior-labeling.md`. Classification is performed on pose-derived temporal features and must be able to return `UNCERTAIN` or `OTHER` rather than forcing a label.

| Option | Advantages | Limitations | Licence / team evidence |
|---|---|---|---|
| **Transparent pose rules** | Easy to explain and inspect; useful as a first behaviour baseline; can explicitly abstain when keypoints are unreliable. | Rules may be brittle across dogs, viewpoints, and transitions; thresholds require validation. | No separate ML package required. Not implemented yet. |
| **Random Forest on windowed pose features** | Practical tabular baseline for normalized keypoint displacement, body-centre speed, posture angle, and direction; comparatively small and fast. | Needs consented labelled examples from enough dogs; feature windows and thresholds need to be fixed before test evaluation. | scikit-learn uses BSD-3-Clause. No classifier code or trained model is currently recorded in the repository. |
| **Temporal neural classifier (for example, TCN/LSTM)** | Can learn patterns across sequences rather than relying only on hand-written thresholds. | Requires more representative labelled dogs and careful dog-separated evaluation; harder to interpret and maintain for the current small pilot. | PyTorch main project is BSD-3-Clause with separately listed third-party components. No temporal classifier has been implemented or evaluated. |

### Selected decision — ADR-0006: Behaviour classification

The team selected a **transparent pose-rule baseline** and a **scikit-learn Random Forest** as the two prototype approaches to compare on the same windowed pose features and dog-separated split. A temporal neural classifier is deferred until the project has enough consented, independently labelled dogs to justify it. Evaluation will report macro-F1, per-class precision/recall/F1, balanced accuracy, and event-level temporal metrics as specified in `docs/ml/behavior-labeling.md`. The system will preserve `UNCERTAIN` for low-quality or ambiguous input. Neither approach will be described as validated until measured against reference labels.

## 6. Requirements traceability

| Requirement | How the selected decisions address it |
|---|---|
| SYS-01: keep media local | Local worker; no cloud inference or upload in the proposed data flow. |
| SYS-02: UI uses application API | UI calls the application layer; it does not call the worker or database directly. |
| SYS-03: worker boundary returns observable events | Versioned worker contract returns event labels, intervals, confidence, model identity, and warnings. |
| SYS-04: repository controls persistence | The application repository remains responsible for persistence; the classifier does not access storage directly. |
| SYS-05: observations are not diagnoses | Labels describe visible behavior; uncertainty and limitations remain visible. |
| SYS-06: reviewable report | Event schema includes timestamps, label, confidence, and model version for review/export. |

## 7. Evidence and unresolved items

- The Base/Large timings are from the **same 20 sampled frames on Colab Tesla T4**. They are preliminary pipeline-throughput measurements, not a statistically meaningful benchmark.
- The mean keypoint confidence values do not measure correctness. There were no ground-truth pose annotations in that pilot.
- The ONNX comparison used a random input tensor for numerical/runtime smoke testing. It does not establish correct dog keypoints or behavior accuracy.
- Target-desktop performance, annotated test-set accuracy, model-weight redistribution terms, and final D1/D4 platform/storage decisions remain open.
- Team experience in this document is inferred only from artifacts present in the project: the ViTPose Base/Large experiment and Base ONNX export. No DeepLabCut or behaviour-classifier implementation is evidenced here.
- Add the selected outcomes, rationale, approver/date, exact model/checkpoint version, and licence conditions to ADR-0002, ADR-0003, and ADR-0006. This comparison records the selected technical direction; it does not supply a meeting date, attendee list, or checkpoint licence clearance.

## References

1. Xu et al. “ViTPose++: Vision Transformer for Generic Body Pose Estimation.” *IEEE TPAMI*, 2023. https://arxiv.org/abs/2212.04246
2. ViTAE-Transformer, official ViTPose repository and source licence: https://github.com/ViTAE-Transformer/ViTPose
3. AP-10K project and data terms; the project protocol notes differing statements between the dataset repository and MMPose docs, so verify the exact release before use: https://github.com/AlexTheBad/AP-10K and https://github.com/open-mmlab/mmpose/blob/main/docs/en/dataset_zoo/2d_animal_keypoint.md
4. Mathis et al. “DeepLabCut: markerless pose estimation of user-defined body parts with deep learning.” *Nature Neuroscience*, 2018. https://doi.org/10.1038/s41593-018-0209-y
5. DeepLabCut source licence and SuperAnimal model use notice: https://github.com/DeepLabCut/DeepLabCut/blob/main/LICENSE and https://github.com/DeepLabCut/DeepLabCut#license
6. Breiman, L. “Random Forests.” *Machine Learning* 45, 5–32 (2001). https://doi.org/10.1023/A:1010933404324
7. scikit-learn source licence: https://github.com/scikit-learn/scikit-learn/blob/main/COPYING
8. ONNX Runtime source licence: https://github.com/microsoft/onnxruntime/blob/main/LICENSE
9. PyTorch source licence: https://github.com/pytorch/pytorch/blob/main/LICENSE
