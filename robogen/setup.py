from setuptools import setup, find_packages

setup(
    name='robogen',
    version='0.1.0',
    include_package_data=True,
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    url='https://github.com/jmi2k/robogen',
    author='José Miguel Sánchez García',
    author_email='soy.jmi2k@gmail.com',
    description='Code generation tool for RoboComp',
    entry_points={'console_scripts': ['robogen = robogen.main:app']},
)

