Deep Learning Based Multi-Label Text Classification of UNGA Resolutions
==========

The main goal of this research is to produce a useful software for United Nations (UN), that could help to speed up the process of qualifying the UN documents following the Sustainable Development Goals (SDGs) in order to monitor the progresses at the world level to fight poverty, discrimination, climate changes. In fact human labeling of UN documents would be a daunting task given the size of the impacted corpus. Thus, automatic labeling must be adopted at least as a first step of a multi-phase process to reduce the overall effort of cataloguing and classifying. Deep Learning (DL) is nowadays one of the most powerful tools for state-of-the-art (SOTA) AI for this task, but very often it comes with the cost of an expensive and error-prone preparation of a training-set. In the case of multi-label text classification of domain-specific text it seems that we cannot effectively adopt DL without a big-enough domain-specific training-set. In this paper, we show that this is not always true. In fact we propose a novel method that is able, through statistics like TF-IDF, to exploit pre- trained SOTA DL models (such as the Universal Sentence Encoder) without any need for traditional transfer learning or any other expensive training procedure. We show the effectiveness of our method in a legal context, by classifying UN Resolutions according to their most related SDGs. 

## Installation

* requires python3.7+
* clone this repo
* cd to the repo/development
* create a virtual environment: `python3 -m venv venv`
* load the virtual environment: `source venv/bin/activate`
* install the dependencies: `pip install -r requirements.txt`
* install the spaCy model: `python -m spacy download en_core_web_md`

## Usage

* load the virtual environment: `source venv/bin/activate`
* to run the demo: `python demo_SDG.py`
* to compare different algorithms and build graphics: `python statistics/algorithm_comparison.py <path/to/dataset.json> <path/to/created_figure>`
* to print dataset support: `python statistics/print_dataset_support.py <path/to/dataset.json>`

**Datasets are in directory [dataset](dataset)**

## Contact

To report issues, use GitHub Issues. 
For other queries, contact Francesco Sovrano: 
* <francesco.sovrano2@unibo.it>
* <cesco.sovrano@gmail.com>

## License

This software has been built upon [UN Challenge 2019](https://gitlab.com/CIRSFID/un-challange-2019).
License is available [here](LICENSE)