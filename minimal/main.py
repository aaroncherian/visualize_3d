from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import numpy as np
import logging

from skellymodels.create_model_skeleton import create_mediapipe_skeleton_model
from skellymodels.experimental.model_redo.managers.human import Human
from skellymodels.experimental.model_redo.tracker_info.model_info import MediapipeModelInfo, ModelInfo

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your paths here
# recording_folder_path = Path(r"D:\2024-08-01_treadmill_KK_JSM_ATC\1.0_recordings\sesh_2024-08-01_16_18_26_JSM_wrecking_ball")
# data_path = recording_folder_path / "output_data" / "mediapipe_skeleton_3d.npy"

# skeleton = Human.from_tracked_points_numpy_array(
#     name = "human",
#     model_info = MediapipeModelInfo(),
#     tracked_points_numpy_array=np.load(data_path)

# )
# skeleton.calculate()

def test_it_works(
    human,
    threshold: float = 1e-6,
    verbose: bool = True,
):
    """
    Prints standard deviation of segment lengths for the rigidified trajectory.
    Highlights segments that fail the rigidity check.

    Parameters
    ----------
    human : Human
        Human model with 'rigid_3d_xyz' in body.trajectories.
    threshold : float
        Max allowable std deviation to consider a segment rigid.
    verbose : bool
        Whether to print full results.

    Returns
    -------
    None
    """
    trajectory = human.body.trajectories["rigid_3d_xyz"]
    segment_data = trajectory.segment_data

    print("\n🔍 Rigid Segment Variance Check:\n")
    print(f"{'Segment':<25} {'Std Dev':>10}   Status")

    for seg_name, data in segment_data.items():
        prox_xyz = data["proximal"]
        dist_xyz = data["distal"]

        lengths = np.linalg.norm(dist_xyz - prox_xyz, axis=1)
        std = np.nanstd(lengths)

        if std < threshold:
            status = "✅ OK"
        else:
            status = f"⚠️  NOT RIGID (>{threshold})"

        if verbose:
            print(f"{seg_name:<25} {std:10.6f}   {status}")


recording_folder_path = Path(r"D:\ferret_recording")
data_path = recording_folder_path/"output_data"/"dlc_body_3d_xyz.npy"

data_path = Path(r"C:\Users\aaron\Downloads\raw_dlc_3d_array_iteration_12.npy")

path_to_ferret_yaml = Path(__file__).parents[0]/'dlc_ferret.yaml'
ferret_model_info = ModelInfo(config_path=path_to_ferret_yaml)

landmarks_array = np.load(data_path)
landmarks_array = np.nan_to_num(landmarks_array)

skeleton = Human.from_landmarks_numpy_array(name="ferret",
               model_info=ferret_model_info,
               landmarks_numpy_array=landmarks_array)
skeleton.calculate()
test_it_works(human=skeleton)

html_path = Path(__file__).parents[0]/'index.html'


def human_to_custom_dict(human: Human) -> dict:
    """
    Mirror the legacy `to_custom_dict` for the new Human/Trajectory API.
    Returns only what the thin-client viewer needs.
    """
    traj = human.body.trajectories["rigid_3d_xyz"]          # Trajectory object
    markers = traj.landmark_names                     # list[str]  :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
    num_frames = traj.num_frames                      # int        :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}


    def numpy_to_list(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: numpy_to_list(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [numpy_to_list(i) for i in obj]
        return obj

    return {
        "markers"     : markers,
        "trajectories": {k: v.tolist() for k, v in traj.data.items()},  # (F, J, 3) → list
        "segments"    : human.body.anatomical_structure.segment_connections,
        "num_frames"  : num_frames,
    }


@app.get("/")
async def serve_index():
    return FileResponse(html_path)


@app.get("/data")
async def get_data():
    try:
        return JSONResponse(human_to_custom_dict(skeleton))
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise HTTPException(status_code=500, detail="Failed to load 3D data")


    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")