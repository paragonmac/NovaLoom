from astropy.io import fits
import matplotlib.pyplot as plt

hdul = fits.open(r'F:\Astroimages\M31\M31 6-18-23\Light_M31_300.0s_Bin1_2600MC_20230618-035346_0001.fit')
hdul.info()

for i, hdu in enumerate(hdul):
    if hdu.data is not None:
        plt.imshow(hdu.data, cmap='gray', origin='lower')
        plt.title(f"HDU {i}")
        plt.colorbar()
        plt.show()

hdul.close()