TINT
====
TINT (TINT is not TITAN) is an easy-to-use storm cell tracking package based
on the TITAN methodology by Dixon and Wiener. This code is in early alpha
stage, so documentation and testing are still being built. If you have any
suggestions or wish to contribute, please open an issue. Feel free to email
me at mhpicel@gmail.com if you need assistance.

`Check out this demonstration <https://github.com/openradar/TINT/blob/master/examples/tint_demo.ipynb/>`_

The development is currently led by the Data Informatics and Geophysical
Retrievals (DIGR) group in the Environmental Sciences Group at Argonne
National Laboratory. 

Dependencies
------------
- `NumPy <https://numpy.org/>`_
- `Pandas <https://pandas.pydata.org/>`_
- `SciPy <https://www.scipy.org/>`_
- `matplotlib <https://matplotlib.org/>`_
- `cartopy <https://scitools.org.uk/cartopy/docs/latest/>`_
- `Py-ART <http://arm-doe.github.io/pyart/>`_
- `ffmpeg <https://www.ffmpeg.org/>`_

Install
-------
To install TINT, first install the dependencies listed above. We recommend
installing Py-ART from conda forge::

	conda install -c conda-forge arm_pyart

Then clone::

	git clone https://github.com/openradar/TINT.git

then::

	cd TINT
	pip install -e .

Citing
------
Currently for citing please cite:

Fridlind, A. M., van Lier-Walqui, M., Collis, S., Giangrande, S. E., Jackson,
R. C., Li, X., Matsui, T., Orville, R., Picel, M. H., Rosenfeld, D., Ryzhkov,
A., Weitz, R., and Zhang, P.: Use of polarimetric radar measurements to
constrain simulated convective cell evolution: a pilot study with Lagrangian
tracking, Atmos. Meas. Tech., 12, 2979–3000,
https://doi.org/10.5194/amt-12-2979-2019, 2019.

Acknowledgements
----------------
This work is the adaptation of tracking code in R created by Bhupendra Raut who was working at Monash University,
Australia in the Australian Research Council's Centre of Excellence for Climate System Science led by Christian Jakob.
This work was supported by the Department of Energy, Atmospheric Systems Research (ASR) under Grant DE-SC0014063,
“The vertical structure of convective mass-flux derived from modern radar systems - Data analysis in support of cumulus
parametrization”

The development of this software is supported by the Climate Model Development
and Validation (CMDV) activity which funded by the Office of Biological and
Environmental Research in the US Department of Energy Office of Science.

References
----------
Dixon, M. and G. Wiener, 1993: TITAN: Thunderstorm Identification, Tracking,
Analysis, and Nowcasting—A Radar-based Methodology. J. Atmos. Oceanic
Technol., 10, 785–797, doi: 10.1175/1520-0426(1993)010<0785:TTITAA>2.0.CO;2.

Leese, J.A., C.S. Novak, and B.B. Clark, 1971: An Automated Technique for Obtaining Cloud Motion from Geosynchronous
Satellite Data Using Cross Correlation. J. Appl. Meteor., 10, 118–132, doi: 10.1175/1520-0450(1971)010<0118:AATFOC>2.0.CO;2.

