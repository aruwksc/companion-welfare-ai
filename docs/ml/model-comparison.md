### Preliminary inference test

- Model: ViTPose++-Base, AP-10K expert (`dataset_index=3`)
- Test: one frame extracted at approximately 1 second from a sample video
- Result: the model detected the dog and produced animal keypoints
- Limitation: this was a smoke test; accuracy was not measured, the full video was not analysed, and behaviour was not classified
- Implementation used: Hugging Face Transformers checkpoint in Google Colab; the local `.pth` checkpoint has not been tested yet

| Model | Frames with poses | Processing time | Pipeline FPS | Mean keypoint confidence | Hardware |
|---|---:|---:|---:|---:|---|
| ViTPose++-Base | 20/20 | 2.42 s | 8.26 | 0.500 | Google Colab Tesla T4 |
| ViTPose++-Large | 20/20 | 4.90 s | 4.08 | 0.597 | Google Colab Tesla T4 |

Both models were evaluated on the same 20 sampled frames. FPS measures the complete detection-and-pose pipeline. Mean keypoint confidence is not an accuracy metric; no ground-truth keypoint annotations were available.

### Prototype model decision

ViTPose++-Base is selected as the primary pose-estimation model for the prototype. It meets the minimum model-size requirement and was faster than ViTPose++-Large in the preliminary 20-frame test. ViTPose++-Large remains a comparison model. The test used Google Colab Tesla T4; performance on the target desktop has not been measured. Keypoint confidence is not an accuracy metric.