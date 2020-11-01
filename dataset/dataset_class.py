import torch
from torch.utils.data import Dataset
import os
import numpy as np
import pandas as pd

from .video_extraction_conversion import *


class VidDataSet(Dataset):
    def __init__(self, K, path_to_mp4, fid, device):
        self.K = K
        self.path_to_mp4 = path_to_mp4
        self.device = device
        self.fid = fid
    
    def __len__(self):
        return len(self.fid)
    
    def __getitem__(self, idx):
        vid_idx = idx
        file = self.fid['File'][idx]
        path = os.path.join(self.path_to_mp4, file)
        frame_mark = select_frames(path , self.K)
        frame_mark = generate_landmarks(frame_mark)
        frame_mark = torch.from_numpy(np.array(frame_mark)).type(dtype = torch.float) #K,2,224,224,3
        #print(frame_mark.shape,idx)
        if not len(frame_mark): return self.__getitem__(idx//2)
        frame_mark = frame_mark.transpose(2,4).to(self.device) #K,2,3,224,224
        
        g_idx = torch.randint(low = 0, high = self.K, size = (1,1))
        x = frame_mark[g_idx,0].squeeze()
        g_y = frame_mark[g_idx,1].squeeze()
        return frame_mark, x, g_y, vid_idx


class FineTuningImagesDataset(Dataset):
    def __init__(self, path_to_images, device):
        self.path_to_images = path_to_images
        self.device = device
    
    def __len__(self):
        return len(os.listdir(self.path_to_images))
    
    def __getitem__(self, idx):
        frame_mark_images = select_images_frames(self.path_to_images)
        random_idx = torch.randint(low = 0, high = len(frame_mark_images), size = (1,1))
        frame_mark_images = [frame_mark_images[random_idx]]
        frame_mark_images = generate_cropped_landmarks(frame_mark_images, pad=50)
        frame_mark_images = torch.from_numpy(np.array(frame_mark_images)).type(dtype = torch.float) #1,2,256,256,3
        frame_mark_images = frame_mark_images.transpose(2,4).to(self.device) #1,2,3,256,256
        
        x = frame_mark_images[0,0].squeeze()
        g_y = frame_mark_images[0,1].squeeze()
        
        return x, g_y
        

class FineTuningVideoDataset(Dataset):
    def __init__(self, path_to_video, device):
        self.path_to_video = path_to_video
        self.device = device
    
    def __len__(self):
        return 1
    
    def __getitem__(self, idx):
        path = self.path_to_video
        frame_has_face = False
        while not frame_has_face:
            try:
	            frame_mark = select_frames(path , 1)
	            frame_mark = generate_cropped_landmarks(frame_mark, pad=50)
	            frame_has_face = True
            except:
                print('No face detected, retrying')
        frame_mark = torch.from_numpy(np.array(frame_mark)).type(dtype = torch.float) #1,2,256,256,3
        frame_mark = frame_mark.transpose(2,4).to(self.device) #1,2,3,256,256
        
        x = frame_mark[0,0].squeeze()
        g_y = frame_mark[0,1].squeeze()
        return x, g_y