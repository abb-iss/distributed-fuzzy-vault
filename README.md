# Privacy mechanisms for decentralized fingerprint-based authentication

*MSc thesis project by Swe Geng at ETH Zurich in collaboration with ABB Corporate Research 
(supervisors: Georgia Giannopoulou, Maëlle Kabir-Querrec)*

The research results of the project have been published in [WPES 2019](https://dl.acm.org/doi/10.1145/3338498.3358648) and in an extended form, in [arxiv](https://arxiv.org/abs/1911.00248).

## Thesis abstract

Biometric authentication is getting increasingly popular due to the convenience of using unique individual traits, such as fingerprints, palm veins, irises. Especially fingerprints are widely used nowadays due to the availability and low cost of fingerprint scanners. To avoid identity theft or impersonation, fingerprint data is typically stored locally, e.g., in a trusted hardware module, in a single device that is used for user enrollment and authentication. Local storage, however, limits the ability to implement distributed applications, in which users can enroll their fingerprint once and use it to access multiple physical locations and mobile applications afterwards. This thesis presents a distributed authentication system that stores fingerprint data in a server or cloud infrastructure in a privacy-preserving way. Multiple devices can be connected and perform user enrollment or verification. To secure the privacy and integrity of sensitive data, we employ a cryptographic construct called fuzzy vault. We highlight challenges in implementing fuzzy vault-based authentication, for which we propose and compare alternative solutions. We conduct a security analysis of our biometric cryptosystem, and as a proof of concept, we build an authentication system for access control using resource-constrained devices (Raspberry Pis) connected to fingerprint scanners and the Microsoft Azure cloud environment. Furthermore, we evaluate the fingerprint matching algorithm against the well-known FVC2006 database and show that it can achieve comparable accuracy to widely-used matching techniques that are not designed for privacy, while remaining efficient with an authentication time of few seconds.

## Fuzzy Vault Implementation

This package contains the main code of the Master's thesis including the fuzzy vault algorithm and the fuzzy vault
distributed application. Several testing functions can be found in Tests.py.
Plot_Minutiae.py can be used to visualize minutiae with .xyt files which is the output format of the minutiae detector MINDTCT from NBIS.
Please refer to the report of the Master's thesis for more information on the library and code used to enable the fuzzy vault algorithm and the fuzzy vault distributed application.

### Fuzzy Vault Algorithm

The main algorithm runs in Main.py. The constants and parameters for the fuzzy vault algorithm are stored in Constants.py and can be changed according to
the desired experiments. Please refer to the Master's thesis report for more information.
The input fingerprint database with .xyt files are stored in /input_images. All input images need to be converted to .xyt files first before running the algorithm.
The normal logs from the algorithm are stored in /out. The last part in Constants.py is used for logging of full database testing (run through whole database with two different protocols described below) where the folder is defined where the logs should be written.

The algorithm is currently constructed to either run over the FVC2006 DB 2A or 2B. This can be changed with the flag
DATABASE_2A_FLAG in Constants.py where the value True indicates that the run is over DB 2A and DB 2B when the value is
False. The code is specifically designed for the two databases with the number of fingers and captures aligned for comparison.
SPLIT_COMPUTATION can be set to True in Constants.py in order to run the algorithm over different parts of the database
FVC2006 DB 2A. FINGER_START and FINGER_END indicate which fingers are taken as the gallery. The probe templates to be
matched are always the whole database (1'680 pictures). There are two protocol to run through the database: 1vs1 and FVC protocol.
Please refer to the Master's thesis report for more information.

The fuzzy vault algorithm should be run with PyPy3 as it is a lot faster than Python3. To run the algorithm, execute
Main.py with a positive integer as a parameter. If the integer is 0, the algorithm runs over the whole database.
Otherwise, only matches of XYT_GALLERY and XYT_PROBE are conducted, which are defined in Constants.py. In this case the
positive integer represents how many matches are conducted with those two templates.

### Fuzzy Vault Distributed Application

The fuzzy vault distributed application consists of the following python files:

* [App.py](App.py)
* [Adafruit_Handler.py](Adafruit_Handler.py)
* [DBHandler.py](DBHandler.py)

The fuzzy vault distributed application is intended to run on a Raspberry Pi 3 connected with an Adafruit fingerprint
sensor and PyPy3. PyPy3 is a lot faster than Python3 to run. The generated fuzzy vaults are stored on Microsoft Azure
CosmosDB. The database has to be set up prior to running the application. The connection string to the database has to
be filled in in the file [DBHandler.py](DBHandler.py) on line 12 (MongoClient). To run the distributed application, run [App.py](App.py) without
parameters. The application can enroll and verify fingerprints. MINDTCT from NBIS needs to be installed before running the application.

### Installation NBIS

1. Install `cmake`:

    ```shell
    sudo apt-get install cmake
    ```

2. Download zip from NBIS open server
3. unzip `nbis_v5.0.0`
4. Download `libpng-1.2.23rc01` and copy whole folder to `Rel_5.0.0/png/src/lib`, replacing existing `png` folder in mentioned path (rename new folder to `png`). Get `Makefile` from old folder `png` and replace the new one from `libpng-1.2.23rc01`
5. Run:

    ```shell
    ./setup.sh ~/Documents/NBIS/SRC
    ```

    * No –32 flag!!! There will be a -m32 flag not recognised error on raspberry

6. Run:

    ```shell
    make config
    ```

7. Compile `libpng` separately (described in [INSTALL](INSTALL) file from new `png` folder) and get `libpng12.a` file from `/usr/local/lib`
8. Copy `libpng12.a` file to `Rel_5.0.0/exports/lib` and rename to `libpng.a`
9. Copy renamed `libpng.a` also to `Rel_5.0.0/png/src/lib/png`
10. Run:

    ```shell
    make install LIBNBIS=yes
    cd ~/Documents/NBIS/SRC/bin
    sudo cp mindtct /usr/bin
    ```

    * to be able to call `mindtct` from anywhere
    * Possible Errors:
      * Error with library in `Rel_5.0.0/png/src/lib/png`
        * Replace whole folder `png` with a `libpng-1.2.23rc01` of `libpng` (rename folder to `png` again)
      * Error with configure in `Rel_5.0.0/png/src/lib/png`
        * Configure in `Rel_5.0.0/png/src/lib/zlib` not executable:

          ```shell
          chmod +x configure
          ```

      * Error in `Rel_5.0.0/openjp2/src`: cmake: not found
        * Install cmake:

          ```shell
          sudo apt-get install cmake
          ```

### Adafruit Sensor setup on Raspberry Pi

Serial:

* https://technicalustad.com/connect-fingerprint-sensor-module-with-raspberry-pi/
* https://tutorials-raspberrypi.com/how-to-use-raspberry-pi-fingerprint-sensor-authentication/
* https://www.pm-codeworks.de/pamfingerprint.html
* Adafruit cables wrong way around (Tx and Rx)

Instructions:

* Enable serial and disable console mode on serial: http://hallard.me/enable-serial-port-on-raspberry-pi/
* Disable bluetooth (necessary!): https://scribles.net/disabling-bluetooth-on-raspberry-pi/
* PINs of pi3 model B: http://pi4j.com/pins/model-3b-rev1.html
  * Red -> Power 3.3V, not 5V!
  * Black -> Ground
  * White -> TxD
  * Green -> RxD

Code:

* Set serial interface to "serial0" instead of "ttyUSB0"
* If using `pamfingerprint`: change to `serial0` instead of `ttyUSB0` in `/etc/pamfingerprint.conf`
