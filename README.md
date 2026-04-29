# eStreamer Client (Redis-based)

This project is a refactored version of the original Cisco eStreamer eNcore client.

The original implementation used file-based storage for event data. In this version, the storage layer has been redesigned to use Redis, enabling faster data processing, improved scalability, and better suitability for real-time or distributed environments.

## Key Changes

* Replaced file-based storage with Redis
* Refactored data handling and processing logic
* Improved structure for easier integration with backend systems
* Optimized for high-throughput event streaming

## Overview

The eStreamer client connects to a Firepower Management Center and streams:

* Intrusion events
* Connection events
* Discovery data
* File events

The data is parsed from binary format and stored in Redis for further processing or integration with external systems.

## Usage

```bash
./encore.sh
```

### Additional commands:

* Test connectivity:

  ```bash
  ./encore.sh test
  ```
* Run in foreground:

  ```bash
  ./encore.sh foreground
  ```
* Start background process:

  ```bash
  ./encore.sh start
  ```
* Stop:

  ```bash
  ./encore.sh stop
  ```

## Requirements

* Python 3
* Redis server
* Access to Firepower Management Center (eStreamer enabled)

## Notes

Note: This project is based on an existing implementation and has been modified to change the storage mechanism and internal structure.


## License

Refer to the original project for licensing details. [text](https://github.com/CiscoSecurity/fp-05-firepower-cli)
