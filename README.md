# Standalone Mozilla HTTP Observatory - CLI Scanner
## Score your site's HTTPS practices from a lightweight CLI


The [Mozilla HTTP Observatory](https://github.com/mozilla/http-observatory)  is a set of tools to analyze your website and inform you if you are utilizing the many available methods to secure it. It consists of a full suite to run a site such as [https://observability.mozilla.com](https://observatory.mozilla.org/) with scanners, APIs, databases and more.

This is a subset of Mozilla's which focuses on CLI scanning of a website without the other tooling. The indened usage is to include it in CI/CD pipelines to ensure certain levels of security in a build pipeline.

Mozilla's CLI package (https://github.com/mozilla/observatory-cli) does not perform its own scanning. It asks Mozilla's server to scan your site, and returns the (cached) results.

## Scanning a site 
To scan a site, use the observatory-scanner
```bash
$ observatory-scanner
```   
See the --help option for all options.

## Installation
The by far easiest way to install the Mozilla HTTP Observatory - CLI Scanner is to use Canonical's snaps:

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/tingdahl-observatory-http-cli-scanner)

If you are handy with python, you should be able to make a local install by

```bash
# Install the HTTP Observatory - CLI Scanner
$ git clone https://github.com/tingdahl/observatory-scanner.git
$ cd http-observatory-local-scan
$ pip3 install --upgrade .
```
Build is maintained on recent Ubuntu (24.04)

## Updates
This softare is a clone and simplified version of the upstream project. All copyright of the upstream project belongs there. It is the intention to be up to date with the scoring methodology of the upstream process.
