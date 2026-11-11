# Behavior Labeling Protocol

## Purpose and scope

This protocol defines how visible dog movement and posture are labeled in video clips for the first version of the project. The labels describe what can be observed in the video. They do not describe the dog's emotions, personality, health, or reason for acting in a particular way.

The initial annotation unit is one dog in one video clip. The target is a small set of broad, visually distinguishable states. The label set should be reviewed against the available videos before the main dataset is annotated.

## Label set

| Label | Operational definition | Boundary with other labels |
|---|---|---|
| `locomotion` | The dog's body changes location across consecutive frames through walking, running, or another clear form of travel. | Use this label when there is clear translation across the scene. Small head, tail, or limb movements without a change of location do not count as locomotion. |
| `standing` | The dog is upright with its body supported by its legs and is not clearly changing location. | Use when the dog is not sitting or lying and there is no clear locomotion. Small movements in place remain `standing`. |
| `sitting` | The dog's hindquarters are visibly supported by the ground while the front part of the body remains upright. | If the posture cannot be distinguished reliably from standing or lying, use `uncertain`. |
| `lying` | The dog's chest, side, or abdomen is visibly supported by the ground. | A lowered head alone is not sufficient evidence for this label. |
| `other` | The dog is visible, but the interval shows an action or posture that is outside the target states, such as eating or grooming. | Use only when the video is clear enough to describe the interval but none of the target labels applies. Do not use `other` as a substitute for poor visibility. |
| `uncertain` | The dog's state cannot be assigned reliably from the available frames. | Use for substantial occlusion, poor lighting, blur, an unclear transition, or an unusable camera view. Do not guess. |

The labels are mutually exclusive. When a dog moves from one state to another, annotate the visible state at each point in time. Clear travel takes precedence as `locomotion`; once the dog stops, label its stationary posture as `standing`, `sitting`, or `lying` when it is visible.

## Annotation rules

1. Annotate intervals using timestamps in seconds from the start of the source video.
2. Represent each interval as `[start_seconds, end_seconds)`: the start is included and the end is the first time the next label applies.
3. Start an interval at the first frame where the label is visually supported. End it at the first frame where the label changes or the dog is no longer observable.
4. If the exact transition cannot be located confidently, mark the ambiguous transition interval as `uncertain` rather than assigning an arbitrary boundary.
5. Keep separate intervals when the dog returns to a previous label after a different state. Do not merge intervals across a visible state change.
6. Label only what is visible. Audio, assumptions about context, and presumed motivation must not determine the label.
7. If the dog is fully out of frame or hidden for an interval, label that interval `uncertain`; do not infer its state from frames before or after it.
8. If more than one dog is visible and the target dog cannot be identified consistently, mark the affected interval `uncertain` and record the issue in the note field.

## Annotation record

Store one row per labeled interval with these fields:

| Field | Description |
|---|---|
| `video_id` | Anonymous identifier for the source video. |
| `dog_id` | Anonymous identifier for the dog. |
| `start_seconds` | Start time of the interval in the source video. |
| `end_seconds` | End time of the interval in the source video. |
| `label` | One value from the label set above. |
| `annotator_id` | Anonymous identifier for the annotator. |
| `note` | Optional explanation for an uncertain interval or an unusual labeling decision. |

Example header:

```text
video_id,dog_id,start_seconds,end_seconds,label,annotator_id,note
```

Use anonymous IDs in annotation files. Do not include owner names, contact details, or other personal information.

## Annotation and review procedure

1. Review the label definitions together and annotate a small pilot set of permitted clips.
2. Compare labels and interval boundaries. Discuss disagreements and revise the definitions where the rules do not produce consistent decisions.
3. Record the approved version of this protocol before annotating the evaluation set.
4. Have a second team member independently review an agreed subset of intervals. Resolve disagreements using the written definitions and record any protocol change.
5. Keep the protocol version and the annotator IDs with each annotation export so that results can be traced to the rules used.

## Video handling

Use only video for which the team has permission to perform the planned analysis. Store source videos in the agreed access-controlled location. Do not commit source videos, extracted frames, signed consent forms, or identifiable information to the Git repository.

## Limitations

These labels cover broad visible movement and posture states. They are not a complete ethogram and do not establish why a dog behaved in a particular way. In particular, a label must not be presented as evidence of pain, stress, an emotional state, a personality trait, or a veterinary diagnosis.

## Protocol status

This is the initial labeling protocol for the project. The team should review it on the pilot clips and record any agreed changes before producing the main evaluation annotations.
