# Moth-Scanner

Insect detection and moth classification pipeline
Code for the paper "[Deep Learning Pipeline for Automated Visual Moth Monitoring: Insect Localization and Species Classification](https://arxiv.org/abs/2307.15427)"

## Installation
After cloning the repository, initialize and update the submodules:

```bash
git clone git@github.com:cvjena/moth_scanner.git
cd moth_scanner
git submodule init
git submodule update
```

Follow the installation instructions for the [classifier](https://github.com/cvjena/moth_classifier#installation) or the [detector](https://github.com/cvjena/moth_detector#installation).

Train a classifier model and a detection model. Copy the resulting outputs to `models/JENA_MOTHS`.
Rename the weights to `weights.npz`.

To run the pipeline, run

```bash
cd scripts
DATA=<folder with some images> ./run.sh
```

## Citation
You are welcome to use our code in your research! If you do so please cite it as:

```bibtex
@article{korsch2023deep,
  title={Deep learning pipeline for automated visual moth monitoring: insect localization and species classification},
  author={Korsch, Dimitri and Bodesheim, Paul and Denzler, Joachim},
  journal={arXiv preprint arXiv:2307.15427},
  year={2023}
}
```

## License
This work is licensed under a [GNU Affero General Public License][agplv3].

[![AGPLv3][agplv3-image]][agplv3]

[agplv3]: https://www.gnu.org/licenses/agpl-3.0.html
[agplv3-image]: https://www.gnu.org/graphics/agplv3-88x31.png
