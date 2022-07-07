==============================================
Stock Market data extraction
==============================================

Installation
============

As Scrapy Splash comes in the form of a Docker Image, to install and use Scrapy Splash we first need to have Docker installed on our machine. So if you haven't Docker installed already then use one of the following links to install Docker:

`Install Docker Linux`_

.. _Install Docker Linux: https://docs.docker.com/desktop/linux/install/


`Install Docker Mac OS X`_

.. _Install Docker Mac OS X: https://docs.docker.com/desktop/mac/install/


`Install Docker Windows`_

.. _Install Docker Windows: https://docs.docker.com/desktop/windows/install/


Download the Docker installation package, and follow the instructions. Your computer may need to restart after installation.

Check `Scrapy Splash Guide. A JS Rendering Service For Web Scraping`_ for more info.

.. _Scrapy Splash Guide. A JS Rendering Service For Web Scraping: https://scrapeops.io/python-scrapy-playbook/scrapy-splash/



Download Scrapy Splash::

    $ docker pull scrapinghub/splash

Install Python dependencies using pip::

    $ pip install requirements.txt

Run the script::

    $ python3 main.py
