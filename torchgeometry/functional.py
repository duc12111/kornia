import torch


def convert_points_from_homogeneous(points, eps=1e-6):
    """Converts points from homogeneous to Euclidean space.

    Args:
        points (Tensor): tensor of N-dimensional points of size (B, D, N).

    Returns:
        Tensor: tensor of N-1-dimensional points of size (B, D, N-1).
    """
    if not torch.is_tensor(points):
        raise TypeError("Input type is not a torch.Tensor. Got {}"
                        .format(type(points)))

    if not len(points.shape) == 3:
        raise ValueError("Input size must be a three dimensional tensor. Got {}"
                         .format(points.shape))

    return points[..., :-1] / (points[..., -1:] + eps)


def convert_points_to_homogeneous(points):
    """Converts points from Euclidean to homogeneous space.

    Args:
        points (Tensor): tensor of N-dimensional points of size (B, D, N).

    Returns:
        Tensor: tensor of N+1-dimensional points of size (B, D, N+1).
    """
    if not torch.is_tensor(points):
        raise TypeError("Input type is not a torch.Tensor. Got {}"
                        .format(type(points)))

    if not len(points.shape) == 3:
        raise ValueError("Input size must be a three dimensional tensor. Got {}"
                         .format(points.shape))

    return torch.cat([points, torch.ones_like(points)[..., :1]], dim=-1)


def transform_points(dst_homo_src, points_src):
    # TODO: add documentation
    """Applies Transformation to points.
    """
    if not torch.is_tensor(dst_homo_src) or not torch.is_tensor(points_src):
        raise TypeError("Input type is not a torch.Tensor")
    if not dst_homo_src.device == points_src.device:
        raise TypeError("Tensor must be in the same device")
    if not len(dst_homo_src.shape) == 3 or not len(points_src.shape) == 3:
        raise ValueError("Input size must be a three dimensional tensor")
    if not dst_homo_src.shape[0] == points_src.shape[0]:
        raise ValueError("Input batch size must be the same for both tensors")
    if not dst_homo_src.shape[1] == (points_src.shape[1] + 1):
        raise ValueError("Input dimensions must differe by one unit")
    # to homogeneous
    points_src_h = convert_points_to_homogeneous(points_src)  # BxNx3
    # transform coordinates
    points_dst_h = torch.matmul(dst_homo_src, points_src_h.transpose(1, 2))  # Bx3xN
    points_dst_h = points_dst_h.permute(0, 2, 1)  # BxNx3
    # to euclidean
    points_dst = convert_points_from_homogeneous(points_dst_h)  # BxNx2
    return points_dst


def inverse(homography):
    # TODO: add documentation
    # NOTE: we expect in the future to have a native Pytorch function
    """Batched version of torch.inverse(...)
    """
    if not len(homography.shape) == 3:
        raise ValueError("Input size must be a three dimensional tensor. Got {}"
                         .format(points.shape))
    # iterate, compute inverse and stack tensors
    return torch.stack([torch.inverse(homo) for homo in homography])