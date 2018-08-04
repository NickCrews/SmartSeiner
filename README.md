# SmartSeiner

https://github.com/NickCrews/SmartBoat

How do millennials try to increase the catch on an Alaskan commercial salmon fishing boat? By making the process **DATA DRIVEN!!!!**

On commercial [purse seine](https://en.wikipedia.org/wiki/Seine_fishing) salmon fishing boats in [Prince William Sound, Alaska](https://en.wikipedia.org/wiki/Prince_William_Sound), maximizing the number of fish caught is essential. With so many contributing factors, it can be very difficult to pin down exactly what caused a set to be 3,000 or 5,000 pounds, but this difference can be the difference between a profitable season and bankruptcy. Hopefully, by collecting data on many sets, it should be possible to find important patterns that would influence strategy, such as determining the optimum time that a set should be held, how wide the net needs to be spread, where the fish show up at what time, and how catch is affected by the tide.

Traditionally, fisherman **do** think about these things, but with several hundred sets a season spread over three months, finding patterns based on memory is difficult or even misleading. We need to make the data-recording process accurate, but more importantly effortless, or otherwise fishermen will never do the extra effort. We use GPS and compass data to track the positions of the main boat and the skiff to determine separation, speed, hold time, and exact location and timing of all the sets. This is accomplished using an Arduino in the skiff relaying location information to a Raspberry Pi on the main boat, which also reads location data, merges these two streams, and saves the result for future analysis. In addition, a pressure and temperature sensor in the fish hold can be used to determine the level of water in the hold, and therefore determine the amount of fish caught each set.

# Dependencies
- [Raspberry Pi python library for RFM69 radio chip](https://github.com/jkittley/RFM69)
- [Raspberry Pi python library for Adafruit Ultimate GPS](https://github.com/wadda/gps3)
- [Raspberry Pi python library for LSM303 compass/accelerometer](https://github.com/adafruit/Adafruit_Python_LSM303)
- [Arduino library for RFM69 radio chip](https://github.com/LowPowerLab/RFM69)
- [Arduino library for Adafruit Ultimate GPS](https://github.com/adafruit/Adafruit_GPS)
- [Arduino library for LSM303 compass/accelerometer](https://github.com/adafruit/Adafruit_LSM303DLHC)
