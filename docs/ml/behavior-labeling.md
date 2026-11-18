# CWA-26: Behaviour Video Labelling and ML Evaluation Protocol

## 1. Purpose and scope

This protocol defines observable behaviour labels for companion-dog videos, annotation rules, candidate data sources, and an initial evaluation plan. The prototype identifies visible movement patterns. It does not diagnose illness, infer a dog's emotional state from one frame, or replace veterinary assessment.

The first evaluation is a feasibility study. Results must be reported as preliminary if the number of dogs or labelled clips is small.

## 2. Behaviour label set

Use one primary label at a time for a single visible dog. Labels describe what can be seen, not why the dog is doing it.

| Label | Operational definition | Include | Do not infer |
|---|---|---|---|
| `RESTING` | The dog is lying or sitting with no clear locomotion for at least 3 seconds. | Lying, sitting, or remaining still; posture can change slowly. | Sleep, pain, calmness, or low mood. |
| `LOCOMOTION` | The dog changes location through walking, trotting, or running. | Movement between places without clear play interaction. | Exercise quality, fatigue, or intent. |
| `PLAY` | Bouncy or exaggerated movement clearly directed toward a toy, person, or another animal, or a recognizable play bow followed by play movement. | Visible reciprocal play or toy-directed play. | Happiness or social wellbeing. |
| `FEEDING_DRINKING` | The dog visibly consumes food or water from a bowl or other identifiable source. | Repeated mouth-to-bowl contact with consumption visible. | Appetite or health status if consumption cannot be confirmed. |
| `REPETITIVE_MOVEMENT` | The dog repeats substantially similar movement along the same short path or around the same location at least 3 times within 30 seconds. | Repeated pacing or circling when the repetition is visible. | A behavioural disorder, stress, or cause. |
| `OTHER` | The dog is visible, but the observed behaviour does not fit another class. | Sniffing, grooming, standing, or brief actions outside the defined classes. | A welfare-risk category. |
| `UNCERTAIN` | The behaviour cannot be labelled reliably from the video. | Occlusion, poor image quality, multiple dogs that cannot be separated, or ambiguous action. Add a reason code. | A confident class prediction. |

`OTHER` and `UNCERTAIN` are required fallback labels. Do not force ambiguous clips into one of the behaviour classes. A separate optional reason code may be recorded: `OCCLUDED`, `LOW_RESOLUTION`, `OUT_OF_FRAME`, `MULTIPLE_DOGS`, or `AMBIGUOUS_ACTION`.

## 3. Video annotation rules

1. Annotate the visible dog only. If dogs cannot be distinguished consistently, mark the interval `UNCERTAIN` with reason `MULTIPLE_DOGS`.
2. Use intervals in seconds with the half-open convention `[start, end)`: the start is included and the end is excluded.
3. Start an interval at the first frame where the operational definition is met. End it at the first frame where it no longer applies.
4. For `RESTING`, apply the 3-second minimum before assigning the label; include the interval from the beginning of the continuous resting episode once the minimum is met.
5. For `REPETITIVE_MOVEMENT`, record the interval only after the third repeated movement is observed; include the episode from its first repetition and add a short note describing the repeated path.
6. If behaviour changes, end the current interval and start a new one. Do not create overlapping primary labels for the same dog. If a brief transition cannot be resolved, use `UNCERTAIN` for that transition.
7. Annotate using the original video timestamp. Do not infer behaviour from audio alone.
8. Store annotator ID, video ID, dog ID (pseudonymous), start/end time, label, optional reason code, and a short evidence note. Do not put names, addresses, or other direct identifiers in annotation files.
9. Keep source videos and consent forms in the approved private storage, outside Git. Commit only the protocol, anonymised labels, and aggregate evaluation outputs allowed by the consent terms.

### Annotation example

```csv
video_id,dog_id,start_s,end_s,label,reason_code,annotator_id,note
PILOT_001,DOG_01,0.0,8.5,RESTING,,A,"Dog remains lying in frame"
PILOT_001,DOG_01,8.5,13.2,LOCOMOTION,,A,"Dog walks across the room"
PILOT_001,DOG_01,13.2,17.0,UNCERTAIN,OCCLUDED,A,"Dog is hidden behind furniture"
```

## 4. Annotation quality and disagreement handling

- Two annotators independently label the same initial subset of clips before the full annotation pass.
- Compare interval labels after temporal matching. Report class-wise agreement and Cohen's kappa for sampled time points; report mean temporal intersection-over-union (tIoU) for matched intervals.
- Use a provisional agreement target of Cohen's kappa >= 0.70 on the pilot subset. If the target is not met, review disagreements, clarify definitions with examples, and re-annotate the affected subset. This is an operational project target, not a universal scientific threshold.
- Resolve remaining disagreements by discussion and record the adjudicated label plus the reason for the decision. Preserve original annotator labels for agreement calculations.
- Report the number of dogs, videos, intervals and examples per class. Do not claim generalisation from multiple clips of the same dog as if they were independent dogs.

## 5. Candidate datasets and licence/use status

The consented project pilot videos are the primary source for dog-behaviour evaluation. Public datasets below have different tasks and must not be treated as interchangeable behaviour-training data.

| Source | Potential role | Licence / use status | Decision for this prototype |
|---|---|---|---|
| Team-recorded pilot videos with signed consent | Dog behaviour labels and end-to-end prototype evaluation | Use only under the approved consent and ethics terms. Consent must explicitly cover recording, analysis, storage, and any research use. | Primary behaviour dataset; keep raw video and consent records private. |
| AP-10K | Animal body keypoints for pose-estimation context or pose checks; it is not a dog-behaviour-labelled video dataset. | The official AP-10K repository states CC BY 4.0, while MMPose documentation describes the data as non-commercial. This conflict must be resolved against the exact downloaded release and its terms before redistribution or use beyond the permitted research purpose. | Do not include AP-10K images in the behaviour classifier evaluation. Record the exact release and licence decision before use. |
| DogFLW | Dog facial-landmark images; potentially useful for a separate facial-landmark study, not temporal behaviour classification. | Dataset repository states CC BY-NC 4.0. Non-commercial use and attribution conditions apply. | Not used as behaviour video training/evaluation data. |
| K9Bench | Candidate reference for dog-action video QA research. Its records point to third-party online videos. | The dataset notice says video copyright remains with the original rights holders; access to links does not grant redistribution or model-training rights. | Do not download, redistribute, or train on its videos unless rights and terms are checked for each item. |

For every dataset actually used, record: exact name and release/version, source URL, access date, licence text or consent basis, allowed purpose, attribution, redistribution restrictions, and whether the data contains video, images, pose labels, or behaviour labels. If any of these are unknown, mark the dataset `NOT APPROVED FOR USE` until checked.

## 6. Baseline models

Evaluate all baselines on the same dog-separated data split and the same labelled intervals:

1. **Majority-class baseline:** always predicts the most frequent training class. This checks whether a model improves over the class distribution alone.
2. **Pose-rule baseline:** uses a small, documented set of interpretable rules over keypoint displacement and posture, with `UNCERTAIN` when keypoint confidence is insufficient. This is a transparent reference, not a welfare diagnosis.
3. **Pose-feature Random Forest:** uses windowed pose-derived features (for example, normalized keypoint displacement, body-centre speed, posture angle, and movement direction) to predict the defined labels. Fix the window length and feature list before test evaluation.

If there are too few consented dogs to train and evaluate a classifier, report the data limitation and only run a descriptive feasibility analysis. Do not create a random frame-level split: adjacent frames from one dog/video would leak into both train and test sets.

## 7. Data split and evaluation metrics

- Split by dog, not by frame. No dog may appear in both training and test partitions. If the pilot has too few dogs for a fixed split, use leave-one-dog-out evaluation and report the number of folds.
- Keep a validation partition for model/configuration selection. Use the test partition once after the labels, features and thresholds are fixed.
- Report the class distribution and confusion matrix.
- Classification metrics: macro-F1 as the primary summary, plus per-class precision, recall and F1; report balanced accuracy as a supplementary metric.
- Temporal event metrics: match predicted and reference intervals at tIoU >= 0.50; report event precision, recall and F1, plus mean absolute onset/offset error in seconds.
- Pose metrics, if manually annotated ground-truth keypoints are available: report PCK or OKS on those labelled frames. Keypoint confidence alone is not an accuracy metric.
- Report processing time and FPS separately from predictive quality, together with device, model version, input resolution and frame-sampling rate.
- Report uncertainty and failure cases, including occlusion, low light, camera angle, multiple dogs, coat/body shape variation and transitions between behaviours.

## 8. Acceptance criteria for CWA-26

CWA-26 is ready for review when:

- the behaviour classes have operational definitions and examples, including `OTHER` and `UNCERTAIN`;
- the interval convention, transition rules, metadata fields and disagreement procedure are documented;
- each proposed dataset has a recorded licence/consent status and an explicit use decision;
- the majority, pose-rule and pose-feature baselines are specified, or the reason a baseline cannot be run is documented;
- the dog-separated split and classification/temporal metrics are specified;
- the report explicitly states that the output is an observation aid, not a diagnosis or a direct measurement of internal emotional state.

## References and licence pages checked

- AP-10K official repository: https://github.com/AlexTheBad/AP-10K (repository states CC BY 4.0).
- MMPose AP-10K dataset documentation: https://github.com/open-mmlab/mmpose/blob/main/docs/en/dataset_zoo/2d_animal_keypoint.md (documents non-commercial use; check the exact release terms because this differs from the official repository statement).
- DogFLW repository: https://github.com/martvelge/DogFLW (repository states CC BY-NC 4.0 and describes dog facial landmarks, not behaviour video labels).
- K9Bench dataset card: https://huggingface.co/datasets/K9Bench/K9Bench (dataset notice states third-party videos remain copyrighted by original rights holders).
