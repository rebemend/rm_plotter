# falconry

![Python package](https://github.com/fnechans/plotteert/workflows/Python%20package/badge.svg)

## Table of contents

- [Introduction](#introduction)
- [Installation](#installation)

## Introduction

Work in progress! Not fully functional yet.

Wrapper around the CERN's pyROOT, written in python3. The goal is to have a simple way to handle inputs and produce nice plots quickly.

The goal is to steer style through config files, where there would be default style for e.g. ATLAS. 


## Installation

Requires ROOT 6 with python3 pyroot.

To install plotter, simply call following in the repository directory:

    $ pip3 install --user -e .

Then you can include the package in your project simply by adding:

    import plotter
