import os
import cv2
from typing import Iterator, Tuple, Any
from scipy.spatial.transform import Rotation
import pickle

import glob
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow_hub as hub


class Bridge(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for example dataset."""

    VERSION = tfds.core.Version('1.0.0')
    RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")

    def _info(self) -> tfds.core.DatasetInfo:
        """Dataset metadata (homepage, citation,...)."""
        return self.dataset_info_from_configs(
            features=tfds.features.FeaturesDict({
                'steps': tfds.features.Dataset({
                    'observation': tfds.features.FeaturesDict({
                        'image': tfds.features.Image(
                            shape=(250, 250, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Main camera RGB observation.',
                        ),
                        'wrist_image': tfds.features.Image(
                            shape=(250, 250, 3),
                            dtype=np.uint8,
                            encoding_format='jpeg',
                            doc='Wrist camera RGB observation.',
                        ),
                        'joint_state': tfds.features.Tensor(
                            shape=(7,),
                            dtype=np.float64,
                            doc='Robot joint state. Consists of [7x joint states]',
                        ),
                        'joint_state_velocity': tfds.features.Tensor(
                            shape=(7,),
                            dtype=np.float64,
                            doc='Robot joint velocities. Consists of [7x joint velocities]',
                        ),
                        'end_effector_pos': tfds.features.Tensor(
                            shape=(3,),
                            dtype=np.float64,
                            doc='Current End Effector position in Cartesian space',
                        ),
                        'end_effector_ori': tfds.features.Tensor(
                            shape=(3,),
                            dtype=np.float64,
                            doc='Current End Effector orientation in Cartesian space as Euler (xyz)',
                        ),
                        'end_effector_ori_quat': tfds.features.Tensor(
                            shape=(4,),
                            dtype=np.float64,
                            doc='Current End Effector orientation in Cartesian space as Quaternion',
                        )
                    }),
                    'action': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Delta robot action, consists of [3x delta_end_effector_pos, '
                            '3x delta_end_effector_ori (euler: roll, pitch, yaw), 1x des_gripper_width].',
                    ),
                    'action_joint_state': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Robot action in joint space, consists of [7x joint states]',
                    ),
                    'action_joint_vel': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Robot action in joint space, consists of [7x joint velocities]',
                    ),
                    'delta_des_joint_state': tfds.features.Tensor(
                        shape=(7,),
                        dtype=np.float64,
                        doc='Delta robot action in joint space, consists of [7x joint states]',
                    ),
                    'action_gripper_width': tfds.features.Scalar(
                        dtype=np.float64,
                        doc='Desired gripper width, consists of [1x gripper width] in range [0, 1]',
                    ),
                    'discount': tfds.features.Scalar(
                        dtype=np.float64,
                        doc='Discount if provided, default to 1.'
                    ),
                    'reward': tfds.features.Scalar(
                        dtype=np.float64,
                        doc='Reward if provided, 1 on final step for demos.'
                    ),
                    'is_first': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on first step of the episode.'
                    ),
                    'is_last': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on last step of the episode.'
                    ),
                    'is_terminal': tfds.features.Scalar(
                        dtype=np.bool_,
                        doc='True on last step of the episode if it is a terminal step, True for demos.'
                    ),
                    'language_instruction': tfds.features.Text(
                        doc='Language Instruction.'
                    ),
                    'language_instruction_2': tfds.features.Text(
                        doc='Language Instruction.'
                    ),
                    'language_instruction_3': tfds.features.Text(
                        doc='Language Instruction.'
                    ),
                    'language_embedding': tfds.features.Tensor(
                        shape=(3, 512),
                        dtype=np.float32,
                        doc='Kona language embedding. '
                            'See https://tfhub.dev/google/universal-sentence-encoder-large/5'
                    ),
                }),
                'episode_metadata': tfds.features.FeaturesDict({
                    'file_path': tfds.features.Text(
                        doc='Path to the original data file.',
                    ),
                    'traj_length': tfds.features.Scalar(
                        dtype=np.float64,
                        doc='Number of samples in trajectorie'
                    )
                }),
            }))

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Define data splits."""
        data_path = "/home/marcelr/uha_test_policy/finetune_data/des_joint_state/*"
        return {
            'train': self._generate_examples(path=data_path),
            # 'val': self._generate_examples(path='data/val/episode_*.npy'),
        }

    def _generate_examples(self, path) -> Iterator[Tuple[str, Any]]:
        """Generator of examples for each split."""

        # create list of all examples
        episode_paths = glob.glob(path)

        # for smallish datasets, use single-thread parsing
        for sample in episode_paths:
            yield _parse_example(sample, self._embed)

        # for large datasets use beam to parallelize data parsing (this will have initialization overhead)
        # beam = tfds.core.lazy_imports.apache_beam
        # return (
        #         beam.Create(episode_paths)
        #         | beam.Map(_parse_example)
        # )

def _parse_example(episode_path, embed=None):
    data = {}

    for data_field in os.listdir(episode_path):
        data_field_full_path = os.path.join(episode_path, data_field)
        if os.path.isdir(data_field_full_path):
            print("image")
        elif data_field == "lang.txt":
            with open(data_field_full_path, 'rb') as f:
                lang_txt = {"lang.txt": f.read()}
            data.update(lang_txt)
        else:
            data.update({data_field: np.load(data_field_full_path, allow_pickle=True)})

    # agent_data.pkl: dict_keys(['traj_ok', 'camera_info', 'term_t', 'stats'])
    # policy_out.pkl: dict_keys(['actions', 'new_robot_transform', 'delta_robot_transform', 'policy_type'])
    # obs_dict.pkl  : dict_keys(['joint_effort', 'qpos', 'qvel', 'full_state', 'state', 'desired_state', 'time_stamp', 'eef_transform', 'high_bound', 'low_bound', 'env_done', 't_get_obs', 'task_stage'])
    # lang.txt      : b'take the silver pot and place it on the top left burner\nconfidence: 1\n'
    # for key, value in data.items():
    #     print(key)
    #     if isinstance(value, list):
    #         print(value[0].keys())
    #     elif isinstance(value, dict):
    #         print(value.keys())
    #     else:
    #         print(value)
    

    trajectory_length = data["traj_length"]
    cam1_path = os.path.join(episode_path, "cam_1")
    cam2_path = os.path.join(episode_path, "cam_2")
    cam1_image_vector = create_img_vector(cam1_path, trajectory_length)
    cam2_image_vector = create_img_vector(cam2_path, trajectory_length)
    data.update({'image': cam1_image_vector, 'wrist_image': cam2_image_vector})

    episode = []
    for i in range(trajectory_length):
        # (w,x,y,z) -> (x,y,z,w)
        delta_quat = Rotation.from_quat(np.roll(data['delta_end_effector_ori'][i], -1))
        eef_quat = Rotation.from_quat(np.roll(data['end_effector_ori'][i], -1))
        # compute Kona language embedding
        language_embedding = embed(data['language_description']).numpy() if embed is not None else [np.zeros(512)]
        action = np.append(data['delta_end_effector_pos'][i], delta_quat.as_euler("xyz"), axis=0)
        action = np.append(action, data['des_gripper_width'][i])
        # action = data['des_joint_state'][i]

        episode.append({
            'observation': {
                'image': data['image'][i],
                'wrist_image': data['wrist_image'][i],
                'joint_state': data['joint_state'][i],
                'joint_state_velocity': data['joint_state_velocity'][i],
                'end_effector_pos': data['end_effector_pos'][i],
                'end_effector_ori': eef_quat.as_euler("xyz"),
                'end_effector_ori_quat': data['end_effector_ori'][i],
            },
            'action': action,
            'action_joint_state': data['des_joint_state'][i],
            'action_joint_vel': data['des_joint_vel'][i],
            'action_gripper_width': data['des_gripper_width'][i],
            'delta_des_joint_state': data['delta_des_joint_state'][i],
            'discount': 1.0,
            'reward': float(i == (data['traj_length'] - 1)),
            'is_first': i == 0,
            'is_last': i == (data['traj_length'] - 1),
            'is_terminal': i == (data['traj_length'] - 1),
            'language_instruction': data['language_description'][0],
            'language_instruction_2': data['language_description'][1],
            'language_instruction_3': data['language_description'][2],
            'language_embedding': language_embedding,
        })

    # create output data sample
    sample = {
        'steps': episode,
        'episode_metadata': {
            'file_path': episode_path,
            'traj_length': data['traj_length'],
        }
    }

    # if you want to skip an example for whatever reason, simply return None
    return episode_path, sample

def create_img_vector(img_folder_path, trajectory_length):        
    cam_list = []
    cam_path_list = []
    for index in range(trajectory_length):
        frame_file_name = '{}.jpeg'.format(index)
        cam_path_list.append(frame_file_name)
        img_path = os.path.join(img_folder_path, frame_file_name)
        img_array = cv2.imread(img_path)
        cam_list.append(img_array)
    return cam_list

def get_trajectorie_paths_recursive(directory, sub_dir_list):
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            sub_dir_list.append(full_path) if entry == "raw" else get_trajectorie_paths_recursive(full_path, sub_dir_list)
    # return subdirectories

if __name__ == "__main__":
    data_path = "/home/marcelr/BridgeData/raw"
    embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
    raw_dirs = []
    get_trajectorie_paths_recursive(data_path, raw_dirs)
    for raw_dir in raw_dirs:
        for traj_group in os.listdir(raw_dir):
            traj_group_full_path = os.path.join(raw_dir, traj_group)
            if os.path.isdir(traj_group_full_path):
                for traj_dir in os.listdir(traj_group_full_path):
                    traj_dir_full_path = os.path.join(traj_group_full_path, traj_dir)
                    if os.path.isdir(traj_dir_full_path):
                        _parse_example(traj_dir_full_path, embed)
                    else:
                        print("non dir instead of traj found!")
            else:
                print("non dir instead of traj_group found!")
    # create list of all examples
    # episode_paths = glob.glob(data_path)
    # for episode in episode_paths:
    #     _, sample = _parse_example(episode, embed)