from PIL import Image


def add_watermark(img: Image, watermark: Image, position=(10, 10), opacity=0.5) -> Image:
  """
  Adds a watermark image to the input image with adjustable opacity.

  Args:
      img (Image): The main PIL Image object.
      watermark (Image): The watermark PIL Image object (must have alpha channel for transparency).
      position (tuple, optional): The position (x, y) of the watermark on the main image. Defaults to (0, 0).
      opacity (float, optional): The transparency level of the watermark (0.0 to 1.0). Defaults to 0.5.

  Returns:
      Image: The watermarked image as a PIL Image object.

  Raises:
      ValueError: If the opacity value is outside the range (0.0, 1.0).
  """

  if not 0.0 <= opacity <= 1.0:
      raise ValueError("Opacity must be between 0.0 (fully transparent) and 1.0 (fully opaque)")

  # Ensure both images have alpha channel for transparency
  img = img.convert('RGBA')
  watermark = watermark.convert('RGBA')

  # Create a mask for the watermark based on its alpha channel
  watermark_mask = watermark.copy().convert('L')

  # Apply transparency using alpha compositing
  img.paste(watermark, position, mask=watermark_mask)

  # Adjust overall image opacity (optional)
  img = img.convert('RGB')  # Convert back to RGB for JPEG output (if needed)
  return img