from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='web_analytics',
    description='Tools for web analytics',
    version='0.0.1',
    long_description=readme(),
    author='John Jung',
    author_email='john@johnjung.us',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/johnjung/web_analytics',
    scripts=[
        'web_analytics/ab_testing',
        'web_analytics/line_of_best_fit',
        'web_analytics/log_parsing',
        'web_analytics/tfidf'
    ]
)
