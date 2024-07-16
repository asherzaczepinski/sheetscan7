# Super fast OMR (optical music recognition) without AI!

## Overview 
This project provides a Python-based Optical Music Recognition system without the use of AI algorithms. It processes images of musical scores to detect and analyze printed music. The system extracts notes and other musical symbols directly from images and can process both individual images and PDFs containing musical scores.

## Features
- Extract notes, rests, and other musical symbols from images.
- Support for processing images in bulk via directory input.
- Convert PDF files into images for note extraction.
- Draw rectangles around detected notes for visual verification (development stage).

## Prerequisites
Before you can run this project, you need to install the required Python libraries. Ensure you have Python 3.x installed on your system. This project relies on the following Python libraries:
- Pillow
- NumPy
- PyMuPDF (fitz)
- argparse

## How to install:
pip install Pillow numpy PyMuPDF argparse

## Cloning Project
git clone https://github.com/asherzaczepinski/sheetscan7.git

## Usage
Run main.py! --- (Need to name your sheet music as input.pdf. Replace the current input.pdf)
