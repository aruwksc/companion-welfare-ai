import argparse
from pathlib import Path

import onnxruntime as ort
import torch
from transformers import VitPoseForPoseEstimation


MODEL_ID = "usyd-community/vitpose-plus-base"
DATASET_INDEX = 3  # AP-10K expert
INPUT_SHAPE = (1, 3, 256, 192)


class PoseHeatmaps(torch.nn.Module):
    def __init__(self, model: VitPoseForPoseEstimation):
        super().__init__()
        self.model = model

    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        dataset_index = torch.full(
            (pixel_values.shape[0],),
            DATASET_INDEX,
            dtype=torch.long,
            device=pixel_values.device,
        )
        outputs = self.model(
            pixel_values=pixel_values,
            dataset_index=dataset_index,
        )
        return outputs.heatmaps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="ml/models/vitpose_ap10k/vitpose_plus_base.onnx",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = VitPoseForPoseEstimation.from_pretrained(MODEL_ID)
    model.eval()
    model.to(device)

    export_model = PoseHeatmaps(model).eval()
    example_input = torch.randn(INPUT_SHAPE, dtype=torch.float32, device=device)

    with torch.inference_mode():
        torch_output = export_model(example_input)

    torch.onnx.export(
        export_model,
        (example_input,),
        str(output_path),
        input_names=["pixel_values"],
        output_names=["heatmaps"],
        opset_version=17,
        dynamo=False,
    )

    session = ort.InferenceSession(
        str(output_path),
        providers=["CPUExecutionProvider"],
    )
    onnx_output = session.run(
        ["heatmaps"],
        {"pixel_values": example_input.detach().cpu().numpy()},
    )[0]

    torch_array = torch_output.detach().cpu().numpy()
    max_abs_difference = abs(torch_array - onnx_output).max()

    print(f"Model: {MODEL_ID}")
    print(f"Dataset index: {DATASET_INDEX} (AP-10K)")
    print(f"Device used for export: {device}")
    print(f"ONNX file: {output_path}")
    print(f"ONNX output shape: {onnx_output.shape}")
    print(f"Maximum absolute difference: {max_abs_difference:.6f}")
    print("ONNX Runtime smoke test: passed")


if __name__ == "__main__":
    main()