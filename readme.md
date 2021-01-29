# BioKlustering overview
We introduce BioKlustering, a user-friendly open-source and publicly available web app for unsupervised and semi-supervised learning specialized in cases when sequence alignment and/or experimental phenotyping of all classes are not possible. 

Among its main advantages, BioKlustering

1. allows for maximally unbalanced settings of partially observed labels including cases when only one class is observed, which is currently prohibited in most semi-supervised methods,
2. takes unaligned sequences as input and thus, allows learning for widely diverse sequences (impossible to align) such as virus and bacteria,
3. is easy to use for anyone with little or no programming expertise, and 
4. works well with small sample sizes.


# Usage

BioKlustering is browser-based (preferably Google Chrome), and thus, no installation is needed. Users simply need to click on the following link: xxxxx.

More details are available in the documentation: [DOCS.md](https://github.com/solislemuslab/bioklustering/blob/master/DOCS.md).

# Source Code
BioKlustering is an [open source](http://opensource.org) project, and the source code is available at in this repository with the following structure:
- `BioKlustering-Website` contains all the code for the website and machine-learning models (see `readme.md` file inside this folder)
- `manuscript` contains the reproducible analysis and sample dataset used in the published manuscript (in review)


### Steps to run this website locally

Users with strong programming skills might like to modify the existing code and run a version of the website locally. 

1. Clone this repository
   
```
git clone https://github.com/solislemuslab/bioklustering
```

2. Get inside the `BioKlustering-Website` folder, create and activate a [python virtual environment](https://docs.python.org/3/tutorial/venv.html):

```
cd BioKlustering-Website
python3 -m venv virtual-env
source virtual-env/bin/activate
```
   
3. Install the necessary packages with

```  
pip3 install -r requirements.txt
```

A list of packages can be found in the `requirements.txt` file and is listed below:
```
    numpy~=1.19.4
    pandas~=1.1.5
    bio~=0.2.3
    scikit-learn~=0.23.2
    plotly~=4.14.1
    Django~=3.1.2
    django-crispy-forms~=1.9.2
    django-plotly-dash~=1.4.2
    channels~=2.4.0
    channels-redis~=3.1.0
    django-redis~=4.12.1
    daphne~=2.5.0
    redis~=3.5.3
    psutil~=5.7.3
```

4. You might also need to install `plotly-orca` which is for writing and saving the static plotly images locally. To install with conda, you can use the following command (or see [this link](https://plotly.com/python/orca-management/) for other alternatives). 

```
conda install -c plotly plotly-orca==1.2.1 psutil requests
```
To install conda, you can follow instructions in [this link](https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html). You might need to add a path to conda if it is not in your `PATH`.

5. Run the website with

```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

**Note:** We recommend you use Google Chrome to render the website because different browsers might result in different interface and functionalities

**Note:** When you run the website locally, you will have many changes to `.pyc` local files that you should discard prior to any commit with `git checkout -- <file>` and new untracked files created when running the website locally should be deleted prior to any commit if you intent to contribute to the website.

### Steps to test this website locally
1. Make sure you are in a virtual environment.
```
source virtual-env/bin/activate
```
2. Install [selenium](https://selenium-python.readthedocs.io/installation.html)
```
pip3 install selenium
```
3. Run the following command
```
python3 manage.py test
```


# Contributions

Users interested in expanding functionalities in BioKlustering are welcome to do so.
See details on how to contribute in [CONTRIBUTING.md](https://github.com/solislemuslab/bioklustering/blob/master/CONTRIBUTING.md)

# License
BioKlustering is licensed under the [MIT](https://opensource.org/licenses/MIT) licence. &copy; SolisLemus lab projects (2020)

# Citation
If you use the BioKlustering website in your work, we ask that you cite the following paper:
```
(upcoming)
```

# Feedback, issues and questions

- Issues reports are encouraged through the [GitHub issue tracker](https://github.com/solislemuslab/bioklustering/issues)
- Feedback is always welcome via the following [google form](https://forms.gle/SUYQ6X3WNotpQphj6)
