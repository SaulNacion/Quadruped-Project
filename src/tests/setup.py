import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'test_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all launch files.
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'rviz'), glob(os.path.join('rviz', '*.rviz')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='morg',
    maintainer_email='alaurao@uni.pe',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'publisher_camera = test_package.publisher_camera:main',
            'subscriber_camera = test_package.subscriber_camera:main',
        ],
    },
)
