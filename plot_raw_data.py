import sys
import  numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.timeseries import TimeSeries
from astropy.timeseries import aggregate_downsample
import astropy.units as u

if __name__ == '__main__':

    # file_name = 'sigdigger_20240417_080531Z_1000000_890000000_float32_iq.raw'
    # file_name = '/tmp/gqrx_20240409_081819_890000000_240000_fc_maximum_rausgelaufen.raw'
    # file_name = 'gqrx_20240409_085313_890000000_240000_fc_himmel_boden.raw'
    file_path = sys.argv[1]
    file_name = file_path.split('/')[-1]
    file_name_components = file_name.split('_')

    plot_raw = True
    # plot_raw = False
    plot_waterfall = True
    # plot_waterfall = False
    plot_magnitude = True
    # plot_magnitude = False
    plot_psd = True
    # plot_psd = False

    #   Decode date and time
    year = file_name_components[1][0:4]
    month = file_name_components[1][4:6]
    day = file_name_components[1][6:8]
    hour = file_name_components[2][0:2]
    minute = file_name_components[2][2:4]
    second = file_name_components[2][4:6]
    print('Detected date and time:')
    print(f'Year: {year}, Month: {month}, Day: {day}, Hour: {hour}, Minute: {minute}, Second: {second}')

    #   Decode sampling
    # sampling = float(file_name_components[3])
    sampling = float(file_name_components[4])
    print(f'Detected sampling: {sampling}')

    #   Read file
    f = np.fromfile(open(file_path), dtype=np.float32)

    #   Number of data points
    n_data_points = int(f.shape[0] * 0.5)
    print(f'Data stream length: {n_data_points/sampling/60:6.2f} min')

    start_time = Time(f'{year}-{month}-{day}T{hour}:{minute}:{second}', format='isot')

    if plot_raw:
        #   Calculate amplitude
        amplitude = np.sqrt(f[0::2]**2 + f[1::2]**2)

        #   Setup lightcurve
        time_array = np.arange(0, n_data_points)

        time_series = TimeSeries(
            time=start_time + time_array / sampling * u.s,
            data={
                'amplitude': amplitude,
            }
        )

        #   Bin lightcurve
        ts_binned = aggregate_downsample(
            time_series,
            time_bin_size=1 * u.s,
        )

        # print(ts_binned.time_bin_start)

        fig = plt.figure(figsize=(10, 10))
        plt.scatter(
            ts_binned.time_bin_start.jd,
            np.array(ts_binned['amplitude']),
            s=40,
            facecolors=(0.5, 0., 0.5, 0.2),
            edgecolors=(0.5, 0., 0.5, 0.7),
            lw=0.9,
        )
        plt.xlabel("Time [jd]")
        plt.ylabel("Amplitude")
        plt.show()
        plt.close()

    if plot_waterfall or plot_magnitude or plot_psd:
        data = f[0::2] + 1j * f[1::2]

    if plot_waterfall:
        fig = plt.figure(figsize=(10, 10))
        plt.specgram(data, NFFT=2**10, Fs=sampling)
        plt.xlabel("Time")
        plt.ylabel("Frequency")
        plt.show()
        plt.close()

    if plot_magnitude:
        fig = plt.figure(figsize=(10, 10))
        plt.magnitude_spectrum(data, Fs=sampling)
        plt.xlabel("Frequency")
        plt.ylabel("Magnitude")
        plt.show()
        plt.close()

    if plot_psd:
        fig = plt.figure(figsize=(10, 10))
        plt.psd(data, Fs=sampling)
        plt.xlabel("Frequency")
        plt.ylabel("Power")
        plt.show()
        plt.close()

