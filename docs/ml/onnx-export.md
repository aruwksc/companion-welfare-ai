# ONNX Export

- Model: `usyd-community/vitpose-plus-base`
- Expert: AP-10K (`dataset_index=3`)
- Export device: CUDA
- ONNX output shape: `(1, 17, 64, 48)`
- Maximum absolute difference from PyTorch: `0.000000`
- ONNX Runtime smoke test: passed

The smoke test used a random input tensor to check that ONNX Runtime loads the exported model and produces outputs matching PyTorch. It does not measure pose accuracy or behaviour-classification performance. The ONNX file and model weights are excluded from Git.