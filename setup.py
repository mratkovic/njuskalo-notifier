from setuptools import setup

setup(name='njuskalo-notifier',
      version='0.3',
      description='njuskalo.hr scraper that alerts when new ads matching given filters appear',
      long_description='njuskalo.hr scraper that alerts when new ads matching given filters appear',
      keywords='njuskalo scraper script notifier',
      url='https://github.com/mratkovic/njuskalo-notifier',
      author='Marko Ratkovic',
      author_email='marko.ratkovic@yahoo.com',
      license='MIT',
      packages=['sniffer_scraper'],
      install_requires=[
          'scrapy',
          'tqdm',
      ],
      entry_points={
        'console_scripts': ['njuskalo-notifier=sniffer_scraper.main:main']
      },
      include_package_data=True,
      zip_safe=False)