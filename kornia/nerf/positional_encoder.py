import torch
from torch import nn

from kornia.core import Tensor


class PositionalEncoder(nn.Module):
    r"""Sine-cosine positional encoder for input points.

    Args:
        num_dims: Number of input dimensions (channels): int
        num_freqs: Number of frequency bands for encoding span: int
        log_space: Whether frequency sampling should be log spaced: bool
    """

    def __init__(self, num_dims: int, num_freqs: int, log_space: bool = False) -> None:
        super().__init__()
        self._num_dims = num_dims
        self._embed_fns = [lambda x: x]

        # Define frequencies in either linear or log scale
        if log_space:
            freq_bands = 2.0 ** torch.linspace(0.0, num_freqs - 1, num_freqs)
        else:
            freq_bands = torch.linspace(2.0**0.0, 2.0 ** (num_freqs - 1), num_freqs)

        # Alternate sin and cos
        for freq in freq_bands:
            self._embed_fns.append(lambda x, freq=freq: torch.sin(x * freq))  # FIXME: PI?
            self._embed_fns.append(lambda x, freq=freq: torch.cos(x * freq))

        self._num_encoded_dims = self._num_dims * len(self._embed_fns)

    @property
    def num_encoded_dims(self) -> int:
        return self._num_encoded_dims

    def forward(self, x: Tensor) -> Tensor:
        r"""Apply positional encoding to input.

        Args:
            x: Positionsl (or directional) tensor to encode: Tensor

        Returns:
            Tensor with encoded position/direction: Tensor
        """
        if x.ndim < 1:
            raise ValueError('Input tensor represents a scalar')
        if x.shape[-1] != self._num_dims:
            raise ValueError(
                f'Input tensor number of dimensions {x.shape[-1]} does not match instantiated dimensionality '
                f'{self._num_dims}'
            )
        return torch.cat([fn(x) for fn in self._embed_fns], dim=-1)
