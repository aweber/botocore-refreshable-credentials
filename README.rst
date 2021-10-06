botocore-refreshable-credentials
================================
Implements an botocore.Session subclass for using botocore with expiring
credentials (IAM STS).

|Version| |Status| |Coverage| |License|

Usage
=====

.. code:: python

    import botocore_refreshable_credentials

    session = botocore_refreshable_credentials.get_session()
    client = session.create_client('rekognition')
        ...


Python Versions Supported
-------------------------
3.8+

.. |Version| image:: https://img.shields.io/pypi/v/botocore-refreshable-credentials.svg?
   :target: https://pypi.python.org/pypi/botocore-refreshable-credentials

.. |Status| image:: https://github.com/aweber/botocore-refreshable-credentials/workflows/Testing/badge.svg?
   :target: https://github.com/aweber/botocore-refreshable-credentials/actions?workflow=Testing
   :alt: Build Status

.. |Coverage| image:: https://img.shields.io/codecov/c/github/aweber/botocore-refreshable-credentials.svg?
   :target: https://codecov.io/github/aweber/botocore-refreshable-credentials?branch=master

.. |License| image:: https://img.shields.io/pypi/l/botocore-refreshable-credentials.svg?
