use std::ptr::NonNull;

use objc2_core_foundation::CFRetained;
use objc2_core_video::{
    CVPixelBuffer, CVPixelBufferCreate, CVPixelBufferGetBaseAddress, CVPixelBufferGetBytesPerRow,
    CVPixelBufferGetHeight, CVPixelBufferGetPixelFormatType, CVPixelBufferGetWidth,
    CVPixelBufferLockBaseAddress, CVPixelBufferLockFlags, CVPixelBufferUnlockBaseAddress,
    kCVPixelFormatType_32BGRA,
};

use crate::{Result, StudioError};

pub(crate) struct Pixels {
    pub width: u32,
    pub height: u32,
    pub bytes: Vec<u8>,
}
pub(crate) const MAX_OWNED_FRAME_BYTES: u64 = 128 * 1024 * 1024;
pub(crate) fn extent(width: u32, height: u32) -> Result<usize> {
    let bytes = u64::from(width)
        .checked_mul(u64::from(height))
        .and_then(|value| value.checked_mul(4));
    match bytes {
        Some(bytes) if bytes > 0 && bytes <= MAX_OWNED_FRAME_BYTES => {
            usize::try_from(bytes).map_err(|_| error("Pixel address extent overflow"))
        }
        _ => Err(StudioError::new(
            "unsupported_pixel_extent",
            "Each owned BGRA source and canvas frame must fit within 128 MiB",
        )),
    }
}
struct PixelLock<'a> {
    image: &'a CVPixelBuffer,
    flags: CVPixelBufferLockFlags,
}
impl Drop for PixelLock<'_> {
    fn drop(&mut self) {
        unsafe { CVPixelBufferUnlockBaseAddress(self.image, self.flags) };
    }
}
fn error(detail: &str) -> StudioError {
    StudioError::new("native_pixel_error", detail)
}
fn lock(image: &CVPixelBuffer, flags: CVPixelBufferLockFlags) -> Result<PixelLock<'_>> {
    if unsafe { CVPixelBufferLockBaseAddress(image, flags) } != 0 {
        return Err(error("Native pixel memory could not be locked"));
    }
    Ok(PixelLock { image, flags })
}

pub(crate) fn require_opaque_native(
    image: &CVPixelBuffer,
    mut check: impl FnMut() -> Result<()>,
) -> Result<()> {
    let width = CVPixelBufferGetWidth(image);
    let height = CVPixelBufferGetHeight(image);
    let row = width
        .checked_mul(4)
        .ok_or_else(|| error("Decoded alpha scan row overflow"))?;
    let size = row
        .checked_mul(height)
        .ok_or_else(|| error("Decoded alpha scan extent overflow"))?;
    let stride = CVPixelBufferGetBytesPerRow(image);
    if CVPixelBufferGetPixelFormatType(image) != kCVPixelFormatType_32BGRA
        || stride < row
        || size == 0
        || size as u64 > MAX_OWNED_FRAME_BYTES
    {
        return Err(error("Unsupported decoded BGRA alpha scan layout"));
    }
    let _lock = lock(image, CVPixelBufferLockFlags::ReadOnly)?;
    let address = CVPixelBufferGetBaseAddress(image).cast::<u8>();
    if address.is_null() {
        return Err(error("Decoded alpha scan base address is absent"));
    }
    for y in 0..height {
        check()?;
        let bytes = unsafe { std::slice::from_raw_parts(address.add(y * stride), row) };
        if bytes.chunks_exact(4).any(|pixel| pixel[3] != 255) {
            return Err(error("Decoded output contains a non-opaque alpha sample"));
        }
    }
    Ok(())
}

impl Pixels {
    pub(crate) fn copy(image: &CVPixelBuffer) -> Result<Self> {
        let width = CVPixelBufferGetWidth(image);
        let height = CVPixelBufferGetHeight(image);
        let row = width
            .checked_mul(4)
            .ok_or_else(|| error("Pixel row overflow"))?;
        let size = row
            .checked_mul(height)
            .ok_or_else(|| error("Pixel extent overflow"))?;
        let stride = CVPixelBufferGetBytesPerRow(image);
        if CVPixelBufferGetPixelFormatType(image) != kCVPixelFormatType_32BGRA
            || stride < row
            || size as u64 > MAX_OWNED_FRAME_BYTES
            || size == 0
        {
            return Err(error("Unsupported native BGRA layout or memory extent"));
        }
        let _lock = lock(image, CVPixelBufferLockFlags::ReadOnly)?;
        let address = CVPixelBufferGetBaseAddress(image).cast::<u8>();
        if address.is_null() {
            return Err(error("Native pixel base address is absent"));
        }
        let mut bytes = vec![0; size];
        for y in 0..height {
            let source = unsafe { std::slice::from_raw_parts(address.add(y * stride), row) };
            bytes[y * row..(y + 1) * row].copy_from_slice(source);
        }
        Ok(Self {
            width: u32::try_from(width).map_err(|_| error("Pixel width overflow"))?,
            height: u32::try_from(height).map_err(|_| error("Pixel height overflow"))?,
            bytes,
        })
    }
    pub(crate) fn into_native(self) -> Result<CFRetained<CVPixelBuffer>> {
        let mut pointer = std::ptr::null_mut();
        let status = unsafe {
            CVPixelBufferCreate(
                None,
                self.width as usize,
                self.height as usize,
                kCVPixelFormatType_32BGRA,
                None,
                NonNull::from(&mut pointer),
            )
        };
        if status != 0 {
            return Err(error("Native output pixel allocation failed"));
        }
        let image = unsafe {
            CFRetained::from_raw(
                NonNull::new(pointer)
                    .ok_or_else(|| error("Native output allocation returned null"))?,
            )
        };
        let row = self.width as usize * 4;
        let stride = CVPixelBufferGetBytesPerRow(&image);
        if stride < row || self.bytes.len() != row * self.height as usize {
            return Err(error("Owned pixel extent differs from native output"));
        }
        {
            let _lock = lock(&image, CVPixelBufferLockFlags::empty())?;
            let address = CVPixelBufferGetBaseAddress(&image).cast::<u8>();
            if address.is_null() {
                return Err(error("Native output pixel base address is absent"));
            }
            for y in 0..self.height as usize {
                unsafe {
                    std::ptr::copy_nonoverlapping(
                        self.bytes[y * row..(y + 1) * row].as_ptr(),
                        address.add(y * stride),
                        row,
                    )
                };
            }
        }
        Ok(image)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn decoded_output_alpha_scan_checks_rows_without_an_owned_frame_copy() {
        let opaque = Pixels {
            width: 2,
            height: 2,
            bytes: vec![1, 2, 3, 255, 4, 5, 6, 255, 7, 8, 9, 255, 10, 11, 12, 255],
        }
        .into_native()
        .unwrap();
        let mut rows = 0;
        require_opaque_native(&opaque, || {
            rows += 1;
            Ok(())
        })
        .unwrap();
        assert_eq!(rows, 2);

        let nonopaque = Pixels {
            width: 1,
            height: 1,
            bytes: vec![1, 2, 3, 254],
        }
        .into_native()
        .unwrap();
        assert_eq!(
            require_opaque_native(&nonopaque, || Ok(()))
                .unwrap_err()
                .code,
            "native_pixel_error"
        );

        assert_eq!(
            require_opaque_native(&opaque, || {
                Err(StudioError::new("cancelled_test", "stop"))
            })
            .unwrap_err()
            .code,
            "cancelled_test"
        );
    }
}
