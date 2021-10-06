"""
botocore-refreshable-credentials
================================

"""
import pkg_resources

from botocore_refreshable_credentials.session import get_session

version = pkg_resources.get_distribution(
    'botocore-refreshable-credentials').version

__all__ = ['get_session', 'version']
