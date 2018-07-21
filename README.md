# SmartSeiner
How do millennials try to increase the catch on an Alaskan commercial salmon fishing boat? By making the process **DATA DRIVEN!!!!**

On commercial [purse seine](https://en.wikipedia.org/wiki/Seine_fishing) salmon fishing boats in [Prince William Sound, Alaska](https://en.wikipedia.org/wiki/Prince_William_Sound), maximizing the number of fish caught is essential. With so many contributing factors, it can be very difficult to pin down exactly what caused a set to be 3,000 or 5,000 pounds, but this difference can be the difference between a profitable season and bankruptcy. Hopefully, by collecting data on many sets, it should be possible to find important patterns that would influence strategy, such as determining the optimum time that a set should be held, or how wide the net needs to be spread.

We use GPS and compass data to track the positions of the main boat and the skiff to determine separation, speed, hold time, and exact location and timing of all the sets. This is accomplished using an Arduino in the skiff relaying location information to a Raspberry Pi on the main boat, which also reads location data, merges these two streams, filters it, and saves the result for future analysis.

# Dependencies
- [Raspberry Pi python library for RFM69 radio chip](https://github.com/jkittley/RFM69)
- FIND THIS [Raspberry Pi python library for Adafruit Ultimate GPS]
- [Raspberry Pi python library for LSM303 compass/accelerometer](https://github.com/adafruit/Adafruit_Python_LSM303)
- [Arduino library for RFM69 radio chip](https://github.com/LowPowerLab/RFM69)
- [Arduino library for Adafruit Ultimate GPS](https://github.com/adafruit/Adafruit_GPS)
- [Arduino library for LSM303 compass/accelerometer](https://github.com/adafruit/Adafruit_LSM303DLHC)
