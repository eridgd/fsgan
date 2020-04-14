import torch
from fsgan.utils.blur import GaussianSmoothing


class LandmarkHeatmap(GaussianSmoothing):
    """ Generate heatmaps from landmarks.

    The heatmaps are generated by marking the position of each landmarks point in its corresponding channel map,
    followed by gaussian filtering.

    Args:
        channels (int): Number of channels for both input and output tensors.
        kernel_size(int or list of int): Size of the gaussian kernel
        sigma (float or list of float): Standard deviation of the gaussian kernel
        size (tuple of int): The required heatmap size (height, width)
    """
    def __init__(self, channels=68, kernel_size=13, sigma=2, size=(256, 256)):
        super(LandmarkHeatmap, self).__init__(channels, kernel_size, sigma)
        self.hm_size = size

    def forward(self, landmarks):
        """ Convert landmarks to heatmaps.

        Args:
            landmarks (torch.Tensor): Input landmarks (Bx68x2)

        Returns:
            heatmap (torch.Tensor): Output heatmap.
        """
        hm_tensor = torch.zeros(landmarks.shape[0], landmarks.shape[1], self.hm_size[0], self.hm_size[1],
                                device=landmarks.device)
        landmarks_long = landmarks.long()
        landmarks_long[:, :, :2] = torch.clamp(landmarks_long[:, :, :2], 0, self.hm_size[0] - 1)    # Avoid outliers

        ind0 = torch.arange(hm_tensor.shape[0], device=landmarks.device).repeat(
            hm_tensor.shape[1], 1).permute(1, 0).contiguous().view(-1)
        ind1 = torch.arange(hm_tensor.shape[1], device=landmarks.device).repeat(hm_tensor.shape[0])
        ind2 = landmarks_long[:, :, 1].view(-1)
        ind3 = landmarks_long[:, :, 0].view(-1)
        hm_tensor[(ind0, ind1, ind2, ind3)] = 1.0

        hm_tensor = super().forward(hm_tensor)
        hm_tensor.div_(hm_tensor.max())

        return hm_tensor